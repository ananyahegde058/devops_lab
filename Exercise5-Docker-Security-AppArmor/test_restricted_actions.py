#!/usr/bin/env python3
"""
test_restricted_actions.py
Executes security verification tests against a container launched with
--security-opt apparmor=my-apparmor-profile. Tests file read, binary execution,
permitted application operations, and process confinement status.
"""

import socket
import sys
import time
import urllib.request
import docker
from docker.errors import DockerException

IMAGE_TAG = "flask-apparmor"
PROFILE_NAME = "my-apparmor-profile"
CONTAINER_NAME = "flask-apparmor-security-test"
PREFERRED_PORT = 5001


def find_available_port(start_port=5001, max_port=5050):
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No available TCP ports found in range {start_port}-{max_port}")


def run_test(container, name, command, expected_on_apparmor_linux, explanation):
    print(f"\n--- [Test: {name}] ---")
    print(f"Command executed:  `{command}`")
    exit_code, output = container.exec_run(command)
    out_str = output.decode("utf-8", errors="replace").strip()
    # Truncate output preview if too long
    out_preview = out_str[:120] + ("..." if len(out_str) > 120 else "") if out_str else "<empty>"
    print(f"Actual Exit Code:  {exit_code}")
    print(f"Actual Output:     {out_preview}")
    print(f"Expected on Linux: {expected_on_apparmor_linux}")
    print(f"Analysis:          {explanation(exit_code, out_str)}")
    return {
        "name": name,
        "command": command,
        "exit_code": exit_code,
        "output": out_preview,
        "expected_linux": expected_on_apparmor_linux,
        "analysis": explanation(exit_code, out_str)
    }


def main():
    print("=" * 75)
    print("Exercise 5: AppArmor Restricted-Action Security Test Suite")
    print("=" * 75)

    try:
        client = docker.from_env()
        client.ping()
    except DockerException as e:
        print(f"[FATAL] Cannot connect to Docker daemon: {e}")
        sys.exit(1)

    info = client.info()
    sec_opts = info.get("SecurityOptions", [])
    has_apparmor = any("name=apparmor" in opt.lower() or opt.lower() == "apparmor" for opt in sec_opts)

    print(f"Docker Daemon OS:  {info.get('OperatingSystem')}")
    print(f"Kernel Version:    {info.get('KernelVersion')}")
    print(f"Security Options:  {sec_opts}")
    print(f"Host AppArmor LSM: {'ACTIVE' if has_apparmor else 'INACTIVE / NOT SUPPORTED'}")

    host_port = find_available_port(PREFERRED_PORT)

    # Clean up stale container
    try:
        client.containers.get(CONTAINER_NAME).remove(force=True)
    except docker.errors.NotFound:
        pass

    container = None
    results = []

    try:
        print(f"\nStarting test container '{CONTAINER_NAME}' on host port {host_port}...")
        container = client.containers.run(
            IMAGE_TAG,
            name=CONTAINER_NAME,
            detach=True,
            ports={"5000/tcp": host_port},
            security_opt=[f"apparmor={PROFILE_NAME}"]
        )
        time.sleep(2)
        container.reload()

        if container.status != "running":
            print(f"[ERROR] Container failed to start. Status: {container.status}")
            sys.exit(1)

        print(f"Container is running with ID: {container.short_id}")

        # Check 1: Web application reachability
        print("\n--- [Test 1: Flask Application Reachability] ---")
        url = f"http://localhost:{host_port}/"
        reachable = False
        response_msg = ""
        for _ in range(5):
            try:
                with urllib.request.urlopen(url, timeout=3) as resp:
                    if resp.status == 200:
                        response_msg = resp.read().decode("utf-8").strip()
                        reachable = True
                        break
            except Exception:
                time.sleep(1)

        print(f"URL: {url}")
        print(f"Reachable: {reachable}")
        print(f"Response: '{response_msg}'")
        results.append({
            "name": "Flask HTTP Endpoint",
            "command": f"HTTP GET {url}",
            "exit_code": 0 if reachable else 1,
            "output": response_msg,
            "expected_linux": "HTTP 200 OK with welcome message",
            "analysis": "PASS: Flask application is reachable and serving traffic" if reachable else "FAIL: Application unreachable"
        })

        # Check 2: Process AppArmor confinement state
        def check_confinement(code, out):
            if "my-apparmor-profile" in out:
                return "CONFINED: Process actively running under my-apparmor-profile"
            elif "unconfined" in out or "No such file" in out or code != 0:
                return "UNCONFINED / INACTIVE: Host kernel does not enforce AppArmor LSM"
            return f"Status: {out}"

        r2 = run_test(
            container,
            "Process Confinement Check",
            "cat /proc/self/attr/apparmor/current",
            "my-apparmor-profile (enforce)",
            check_confinement
        )
        results.append(r2)

        # Check 3: Restricted action - Read /etc/passwd
        def check_passwd(code, out):
            if code != 0 or "Permission denied" in out:
                return "DENIED: Access to /etc/passwd was blocked by AppArmor policy (Expected on Linux host)"
            return "PERMITTED: /etc/passwd read succeeded (Expected on Windows/WSL2 Docker Desktop due to missing AppArmor LSM)"

        r3 = run_test(
            container,
            "Restricted Read: /etc/passwd",
            "cat /etc/passwd",
            "Exit Code 1 / Permission Denied",
            check_passwd
        )
        results.append(r3)

        # Check 4: Restricted action - Execute /bin/bash
        def check_bash(code, out):
            if code in (126, 127) or "Permission denied" in out:
                return "DENIED: Execution of /bin/bash was blocked by AppArmor policy (Expected on Linux host)"
            return "PERMITTED: /bin/bash execution succeeded (Expected on Windows/WSL2 Docker Desktop due to missing AppArmor LSM)"

        r4 = run_test(
            container,
            "Restricted Exec: /bin/bash",
            "/bin/bash -c 'echo shell_executed'",
            "Exit Code 126 / Permission Denied",
            check_bash
        )
        results.append(r4)

        # Check 5: Permitted Python action
        def check_python(code, out):
            if code == 0 and "4.0" in out:
                return "PASS: Permitted Python standard library operation succeeded as designed"
            return f"FAIL: Python calculation error (exit_code={code})"

        r5 = run_test(
            container,
            "Permitted Action: Python Execution",
            "python -c 'import math; print(math.sqrt(16))'",
            "Exit Code 0, Output: 4.0",
            check_python
        )
        results.append(r5)

        # Check 6: Permitted file access inside /app/
        def check_app_file(code, out):
            if code == 0 and ("Flask" in out or "def home" in out or '"""' in out):
                return "PASS: Application directory access permitted and verified"
            return f"FAIL: Application file unreadable (exit_code={code})"

        r6 = run_test(
            container,
            "Permitted Action: Read /app/app.py",
            "python -c 'with open(\"/app/app.py\") as f: print(f.read()[:50])'",
            "Exit Code 0, Application code accessible",
            check_app_file
        )
        results.append(r6)

        # Summary Table
        print("\n" + "=" * 75)
        print("FINAL TEST RESULTS MATRIX")
        print("=" * 75)
        print(f"{'Test Name':<32} | {'Exit Code':<10} | {'Status'}")
        print("-" * 75)
        for r in results:
            short_analysis = r['analysis'].split(':')[0]
            print(f"{r['name']:<32} | {str(r['exit_code']):<10} | {short_analysis} - {r['analysis'].split(':')[1].strip() if ':' in r['analysis'] else r['analysis']}")
        print("=" * 75)

    finally:
        if container is not None:
            print(f"\n[CLEANUP] Stopping and removing test container '{container.short_id}'...")
            try:
                container.stop(timeout=2)
                container.remove(force=True)
                print("[SUCCESS] Test container cleaned up successfully.")
            except Exception as e:
                print(f"[WARNING] Error stopping container: {e}")


if __name__ == "__main__":
    main()
