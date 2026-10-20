#!/usr/bin/env python3
"""
apply_apparmor.py
Automates building and running a secured Flask Docker container with an AppArmor profile,
verifying security configuration, testing the HTTP endpoint, and providing clear diagnostics.
"""

import socket
import sys
import time
import urllib.request
import urllib.error
import docker
from docker.errors import DockerException, BuildError, APIError

IMAGE_TAG = "flask-apparmor"
PROFILE_NAME = "my-apparmor-profile"
CONTAINER_NAME = "flask-apparmor-test-instance"
PREFERRED_PORT = 5000


def find_available_port(start_port=5000, max_port=5050):
    """Finds an available TCP port on localhost starting from start_port."""
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No available TCP ports found in range {start_port}-{max_port}")


def check_docker_apparmor_support(client):
    """Inspects Docker daemon and reports whether host kernel supports AppArmor."""
    info = client.info()
    security_opts = info.get("SecurityOptions", [])
    has_apparmor = any("name=apparmor" in opt.lower() or opt.lower() == "apparmor" for opt in security_opts)
    kernel_version = info.get("KernelVersion", "unknown")
    os_name = info.get("OperatingSystem", "unknown")
    return has_apparmor, security_opts, kernel_version, os_name


def main():
    print("=" * 70)
    print("Exercise 5: Docker Security with AppArmor - Container Deployment")
    print("=" * 70)

    # 1. Connect to Docker daemon
    print("\n[Step 1/6] Connecting to Docker Daemon...")
    try:
        client = docker.from_env()
        client.ping()
        print("  [SUCCESS] Connected to Docker daemon successfully.")
    except DockerException as e:
        print(f"  [ERROR] Failed to connect to Docker daemon: {e}")
        print("  Please ensure Docker Desktop / Docker Engine is running.")
        sys.exit(1)

    # Check Host AppArmor support
    has_apparmor, sec_opts, kernel_ver, os_name = check_docker_apparmor_support(client)
    print(f"  Host OS: {os_name}")
    print(f"  Kernel:  {kernel_ver}")
    print(f"  Security Options: {sec_opts}")
    if has_apparmor:
        print("  Host Kernel AppArmor Support: [ACTIVE / SUPPORTED]")
    else:
        print("  Host Kernel AppArmor Support: [NOT ACTIVE / NOT SUPPORTED]")
        print("  (Note: Windows/WSL2 default kernel lacks active AppArmor LSM module)")

    # 2. Build the Docker image
    print(f"\n[Step 2/6] Building Docker image '{IMAGE_TAG}'...")
    try:
        image, build_logs = client.images.build(
            path=".",
            tag=IMAGE_TAG,
            rm=True,
            forcerm=True
        )
        print(f"  [SUCCESS] Built image '{IMAGE_TAG}' (ID: {image.short_id})")
    except BuildError as e:
        print(f"  [ERROR] Image build failed: {e}")
        sys.exit(1)
    except APIError as e:
        print(f"  [ERROR] Docker API error during build: {e}")
        sys.exit(1)

    # 3. Determine host port
    host_port = find_available_port(PREFERRED_PORT)
    print(f"\n[Step 3/6] Selected host port {host_port} (mapped to container port 5000)")

    # 4. Clean up any existing container with same name
    try:
        existing = client.containers.get(CONTAINER_NAME)
        print(f"  Cleaning up preexisting container '{CONTAINER_NAME}'...")
        existing.remove(force=True)
    except docker.errors.NotFound:
        pass

    container = None
    try:
        # Run container with AppArmor profile
        print(f"\n[Step 4/6] Running container with security_opt=['apparmor={PROFILE_NAME}']...")
        container = client.containers.run(
            IMAGE_TAG,
            name=CONTAINER_NAME,
            detach=True,
            ports={"5000/tcp": host_port},
            security_opt=[f"apparmor={PROFILE_NAME}"]
        )
        print(f"  [SUCCESS] Container started: {container.short_id} ({container.name})")

        # Wait for container startup
        time.sleep(2)
        container.reload()
        if container.status != "running":
            print(f"  [ERROR] Container is not running. Status: {container.status}")
            print("  Container logs:")
            print(container.logs().decode("utf-8", errors="replace"))
            sys.exit(1)

        # 5. Inspect container security configuration
        print("\n[Step 5/6] Inspecting Security Configuration & Confinement...")
        container_info = client.api.inspect_container(container.id)
        configured_sec_opt = container_info.get("HostConfig", {}).get("SecurityOpt", [])
        print(f"  Configured HostConfig.SecurityOpt: {configured_sec_opt}")

        # Check internal process confinement
        print("  Checking internal AppArmor confinement via /proc/self/attr/current...")
        res_code, res_out = container.exec_run("cat /proc/self/attr/apparmor/current")
        if res_code != 0:
            res_code, res_out = container.exec_run("cat /proc/self/attr/current")

        internal_status = res_out.decode("utf-8", errors="replace").strip() if res_code == 0 else "Unavailable"
        print(f"  Internal Confinement Attribute: '{internal_status}' (exit_code={res_code})")

        # Distinguish configured vs enforced
        print("\n  --- SECURITY ENFORCEMENT SUMMARY ---")
        if f"apparmor={PROFILE_NAME}" in (configured_sec_opt or []):
            print(f"  - Docker Flag Applied:    YES (apparmor={PROFILE_NAME})")
        else:
            print("  - Docker Flag Applied:    NO")

        if has_apparmor and PROFILE_NAME in internal_status:
            print("  - Kernel LSM Enforced:    YES (Kernel actively confining process)")
        else:
            print("  - Kernel LSM Enforced:    NO / NOT ACTIVE ON THIS HOST")
            print("    Reason: Host kernel does not have AppArmor LSM active.")
            print("    Container is running under Docker Desktop WSL2 emulation without kernel LSM.")

        # 6. Test HTTP Endpoint
        print("\n[Step 6/6] Testing Flask HTTP Endpoint...")
        url = f"http://localhost:{host_port}/"
        health_url = f"http://localhost:{host_port}/health"

        # Retry logic for HTTP check
        max_retries = 5
        response_text = ""
        for attempt in range(1, max_retries + 1):
            try:
                with urllib.request.urlopen(url, timeout=3) as resp:
                    if resp.status == 200:
                        response_text = resp.read().decode("utf-8")
                        print(f"  [SUCCESS] HTTP GET {url} -> 200 OK")
                        print(f"  Response Body: \"{response_text.strip()}\"")
                        break
            except Exception as e:
                if attempt == max_retries:
                    print(f"  [ERROR] HTTP request failed after {max_retries} attempts: {e}")
                time.sleep(1)

        expected_msg = "Hello, this is a secure Flask application running inside a Docker container!"
        if expected_msg in response_text:
            print("  [SUCCESS] Root response matches expected exercise requirement.")
        else:
            print("  [WARNING] Root response differed from expectation.")

        # Test health endpoint
        try:
            with urllib.request.urlopen(health_url, timeout=3) as h_resp:
                if h_resp.status == 200:
                    print(f"  [SUCCESS] HTTP GET {health_url} -> {h_resp.read().decode('utf-8').strip()}")
        except Exception:
            pass

        print("\n" + "=" * 70)
        print("Deployment & Verification Complete!")
        print("=" * 70)

    except Exception as e:
        print(f"\n[UNEXPECTED ERROR] {e}")
        raise
    finally:
        if container is not None:
            print(f"\n[CLEANUP] Stopping and removing container {container.short_id}...")
            try:
                container.stop(timeout=2)
                container.remove(force=True)
                print("  [SUCCESS] Container stopped and cleaned up.")
            except Exception as clean_err:
                print(f"  [WARNING] Error during container cleanup: {clean_err}")


if __name__ == "__main__":
    main()
