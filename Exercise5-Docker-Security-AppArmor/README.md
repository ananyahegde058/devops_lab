# Exercise 5: Docker Security with AppArmor and Python

## 1. Exercise Objective

The objective of this exercise is to understand and implement container security using **AppArmor (Application Armor)** Linux Security Module (LSM) policies combined with **Docker Engine** and the **Docker SDK for Python**.

In this exercise, you will:
- Containerize a secure Python Flask application listening on `0.0.0.0:5000` using a modern, supported base image (`python:3.11-slim`).
- Design, structure, and validate a custom AppArmor profile (`my-apparmor-profile`) enforcing the principle of least privilege: restricting access to sensitive system paths (`/etc/passwd`, `/etc/shadow`, `/root`), blocking shell binary executions (`/bin/bash`, `/bin/sh`), dropping dangerous Linux capabilities (`sys_admin`, `sys_rawio`, `sys_ptrace`), while permitting the necessary network binding and runtime dependencies for the Flask service.
- Automate container build, profile deployment, port publishing, container inspection, HTTP endpoint testing, and guaranteed lifecycle teardown using `apply_apparmor.py` via the Docker SDK for Python.
- Execute security verification checks via `test_restricted_actions.py` to test restricted file reads, restricted binary execution, permitted application operations, and process confinement state.
- Perform a thorough architectural security audit of the host environment (Windows 11 with Docker Desktop and WSL2), distinguishing between a configured security flag (`HostConfig.SecurityOpt`) and active Linux kernel LSM enforcement.
- Provide practical instructions for running this confinement profile on native Linux hosts.

---

## 2. Prerequisites

### Host Environment Requirements
- **Docker Desktop**: Version 29.8+ (API 1.56) running with Linux containers backend (WSL2 Engine).
- **Python**: Version 3.8+ on the host system with packages:
  - `docker` (v7.0+)
  - `flask` (v3.0+)
  - `requests` / standard library `urllib`
- **WSL2 (Windows Subsystem for Linux)**: Ubuntu 24.04 LTS distribution with `apparmor` and `apparmor-utils` installed.

### Native Linux Prerequisites (for Kernel Enforcement)
On a native Debian or Ubuntu Linux server:
```bash
sudo apt-get update
sudo apt-get install -y apparmor apparmor-utils docker.io
sudo systemctl enable --now apparmor
sudo systemctl enable --now docker
```

---

## 3. Project Structure

```text
Exercise-5-Docker-Security-AppArmor/
├── app.py                      # Flask web application (0.0.0.0:5000, / and /health)
├── Dockerfile                  # Container specification using python:3.11-slim
├── requirements.txt            # Pinned dependencies (Flask==3.0.3, Werkzeug==3.0.6)
├── my-apparmor-profile         # Custom AppArmor profile for Python Flask confinement
├── apply_apparmor.py           # Docker SDK automation script (build, run, inspect, verify, cleanup)
├── test_restricted_actions.py  # Test suite verifying restricted & permitted actions
├── README.md                   # Comprehensive exercise documentation & answers
├── .dockerignore               # Build context exclusions (venv, git, cache, output)
└── output/                     # Execution evidence screenshots
    ├── 01-project-structure.png
    ├── 02-docker-version.png
    ├── 03-apparmor-status.png
    ├── 04-docker-image-build.png
    ├── 05-flask-container-running.png
    ├── 06-apparmor-profile-verification.png
    ├── 07-restricted-actions-test.png
    └── 08-final-results.png
```

---

## 4. Explanation of Each File

| File | Purpose and Technical Details |
| :--- | :--- |
| `app.py` | Python Flask microservice configured to listen on `0.0.0.0:5000`. Returns the required message `"Hello, this is a secure Flask application running inside a Docker container!"` on `/` and service diagnostic metrics on `/health`. |
| `Dockerfile` | Multi-stage, lightweight container build using `python:3.11-slim`. Sets `/app` as the working directory, copies `requirements.txt`, installs dependencies with `--no-cache-dir`, copies only needed code, exposes port 5000, and specifies `CMD ["python", "app.py"]`. |
| `requirements.txt` | Pins compatible and secure releases of `Flask==3.0.3` and `Werkzeug==3.0.6`. |
| `my-apparmor-profile` | Complete, syntactically verified AppArmor profile for `my-apparmor-profile` with `flags=(attach_disconnected,mediate_deleted)`. Uses `#include <abstractions/base>` and `<abstractions/nameservice>`, allows network binding on port 5000, denies `/etc/passwd*`, `/etc/shadow*`, `/root/**`, blocks execution of `/bin/bash` and `/bin/sh`, drops `sys_admin` and other dangerous capabilities, while allowing Python interpreter, standard libraries, and application paths. |
| `apply_apparmor.py` | Python automation script utilizing the official Docker SDK (`docker.from_env()`). Connects to the daemon, builds `flask-apparmor`, handles dynamic host port conflicts, applies `--security-opt apparmor=my-apparmor-profile`, inspects `HostConfig.SecurityOpt`, tests HTTP endpoints, verifies confinement status, and guarantees container cleanup via `finally`. |
| `test_restricted_actions.py` | Automated security testing harness. Spawns the secured container, queries `/proc/self/attr/current` for active confinement, attempts restricted file read (`/etc/passwd`), attempts restricted binary execution (`/bin/bash`), verifies permitted Python computation and application file access, and outputs an audit matrix. |
| `.dockerignore` | Prevents unnecessary host files (virtual environments, cache, `.git`, `output/`) from inflating the Docker build context. |
| `output/` | Directory containing verified visual evidence PNG screenshots captured directly from the execution environment. |

---

## 5. Host Environment Details & Security Audit

The lab was executed on the following system:
- **Host Operating System**: Windows 11 Home / Pro (amd64)
- **Docker Client Version**: 29.8.2 (Context: `desktop-linux`)
- **Docker Server Engine**: 29.8.2 on `linux/amd64` (Docker Desktop 4.95.0)
- **WSL Distributions**: `Ubuntu` (WSL2, Ubuntu 24.04 LTS), `docker-desktop` (WSL2)
- **Linux Kernel Version**: `6.18.33.2-microsoft-standard-WSL2`

### Critical Security Finding: Docker Desktop / WSL2 AppArmor Architecture
An in-depth kernel audit of the WSL2 environment yielded:
1. `zcat /proc/config.gz | grep CONFIG_SECURITY_APPARMOR`: Returns `CONFIG_SECURITY_APPARMOR=y`. The AppArmor code is compiled into the Microsoft WSL2 kernel.
2. `CONFIG_DEFAULT_SECURITY_APPARMOR`: Is **not set**.
3. `/sys/module/apparmor/parameters/enabled`: Outputs **`N`**.
4. `/sys/kernel/security/lsm`: Lists `capability,landlock,yama,safesetid,selinux,ima`. AppArmor is absent from active LSMs.
5. `docker info | grep "Security Options"`: Displays `seccomp` and `cgroupns`. `apparmor` is not listed.

**Key Technical Insight**:
When running Docker Desktop on Windows, the Docker CLI allows `--security-opt apparmor=my-apparmor-profile` and records it inside `HostConfig.SecurityOpt`. However, because the underlying WSL2 microVM kernel boots without `apparmor=1 security=apparmor`, the `runc` runtime cannot attach the AppArmor profile to the kernel task. The profile is therefore **configured in Docker metadata, but not actively enforced by the kernel**. 

Our implementation explicitly detects and distinguishes between **configured security options** and **active kernel LSM enforcement**, avoiding false reporting.

---

## 6. Commands to Build and Run the Container

### 6.1 Build the Docker Image
From the `Exercise-5-Docker-Security-AppArmor` directory:
```powershell
docker build -t flask-apparmor .
```

### 6.2 Run the Container Manually
Run the container mapping host port 5000 to container port 5000 with the security option:
```powershell
docker run -d --name flask-app -p 5000:5000 --security-opt apparmor=my-apparmor-profile flask-apparmor
```

### 6.3 Test HTTP Response
```powershell
curl.exe http://localhost:5000/
curl.exe http://localhost:5000/health
```

Expected output:
```text
Hello, this is a secure Flask application running inside a Docker container!
{"pid":1,"python_version":"3.11.17","service":"flask-apparmor","status":"healthy"}
```

### 6.4 Clean Up
```powershell
docker rm -f flask-app
```

---

## 7. Instructions for AppArmor on a Native Linux System

To achieve **full kernel LSM enforcement** on a compatible Linux host (e.g. Ubuntu 22.04 / 24.04 or Debian 12):

### Step 1: Install Utilities & Enable AppArmor
```bash
sudo apt update && sudo apt install -y apparmor apparmor-utils
sudo systemctl enable --now apparmor
sudo aa-status
```
`aa-status` must confirm that the AppArmor module is loaded and `apparmorfs` is mounted.

### Step 2: Copy and Validate the Profile
```bash
sudo cp my-apparmor-profile /etc/apparmor.d/my-apparmor-profile
sudo apparmor_parser -v -r /etc/apparmor.d/my-apparmor-profile
```
Output:
```text
Replacement succeeded for "my-apparmor-profile".
```

### Step 3: Verify Profile Loaded in Kernel
```bash
sudo aa-status | grep my-apparmor-profile
# Or inspect kernel security interface:
cat /sys/kernel/security/apparmor/profiles | grep my-apparmor-profile
```

### Step 4: Run the Container Under Kernel Confinement
```bash
docker run -d --name secure-flask -p 5000:5000 \
  --security-opt apparmor=my-apparmor-profile \
  flask-apparmor
```

### Step 5: Verify Confinement Inside Container
```bash
docker exec secure-flask cat /proc/self/attr/apparmor/current
```
Output on native Linux:
```text
my-apparmor-profile (enforce)
```

---

## 8. Python SDK Automation Execution

### 8.1 Running `apply_apparmor.py`
Execute the automated deployment script from PowerShell:
```powershell
python apply_apparmor.py
```

**Verified Output**:
```text
======================================================================
Exercise 5: Docker Security with AppArmor - Container Deployment
======================================================================

[Step 1/6] Connecting to Docker Daemon...
  [SUCCESS] Connected to Docker daemon successfully.
  Host OS: Docker Desktop
  Kernel:  6.18.33.2-microsoft-standard-WSL2
  Security Options: ['name=seccomp,profile=builtin', 'name=cgroupns']
  Host Kernel AppArmor Support: [NOT ACTIVE / NOT SUPPORTED]
  (Note: Windows/WSL2 default kernel lacks active AppArmor LSM module)

[Step 2/6] Building Docker image 'flask-apparmor'...
  [SUCCESS] Built image 'flask-apparmor' (ID: sha256:eae0f55e0784)

[Step 3/6] Selected host port 5000 (mapped to container port 5000)

[Step 4/6] Running container with security_opt=['apparmor=my-apparmor-profile']...
  [SUCCESS] Container started: 7706488ba9af (flask-apparmor-test-instance)

[Step 5/6] Inspecting Security Configuration & Confinement...
  Configured HostConfig.SecurityOpt: ['apparmor=my-apparmor-profile']
  Checking internal AppArmor confinement via /proc/self/attr/current...
  Internal Confinement Attribute: 'kernel ' (exit_code=0)

  --- SECURITY ENFORCEMENT SUMMARY ---
  - Docker Flag Applied:    YES (apparmor=my-apparmor-profile)
  - Kernel LSM Enforced:    NO / NOT ACTIVE ON THIS HOST
    Reason: Host kernel does not have AppArmor LSM active.
    Container is running under Docker Desktop WSL2 emulation without kernel LSM.

[Step 6/6] Testing Flask HTTP Endpoint...
  [SUCCESS] HTTP GET http://localhost:5000/ -> 200 OK
  Response Body: "Hello, this is a secure Flask application running inside a Docker container!"
  [SUCCESS] Root response matches expected exercise requirement.
  [SUCCESS] HTTP GET http://localhost:5000/health -> {"pid":1,"python_version":"3.11.17","service":"flask-apparmor","status":"healthy"}

======================================================================
Deployment & Verification Complete!
======================================================================

[CLEANUP] Stopping and removing container 7706488ba9af...
  [SUCCESS] Container stopped and cleaned up.
```

### 8.2 Running `test_restricted_actions.py`
Execute the security test harness:
```powershell
python test_restricted_actions.py
```

**Verified Output**:
```text
===========================================================================
Exercise 5: AppArmor Restricted-Action Security Test Suite
===========================================================================
Docker Daemon OS:  Docker Desktop
Kernel Version:    6.18.33.2-microsoft-standard-WSL2
Security Options:  ['name=seccomp,profile=builtin', 'name=cgroupns']
Host AppArmor LSM: INACTIVE / NOT SUPPORTED

Starting test container 'flask-apparmor-security-test' on host port 5001...
Container is running with ID: af4bca586bb5

--- [Test 1: Flask Application Reachability] ---
URL: http://localhost:5001/
Reachable: True
Response: 'Hello, this is a secure Flask application running inside a Docker container!'

--- [Test: Process Confinement Check] ---
Command executed:  `cat /proc/self/attr/apparmor/current`
Actual Exit Code:  1
Actual Output:     cat: /proc/self/attr/apparmor/current: Invalid argument
Expected on Linux: my-apparmor-profile (enforce)
Analysis:          UNCONFINED / INACTIVE: Host kernel does not enforce AppArmor LSM

--- [Test: Restricted Read: /etc/passwd] ---
Command executed:  `cat /etc/passwd`
Actual Exit Code:  0
Actual Output:     root:x:0:0:root:/root:/bin/bash...
Expected on Linux: Exit Code 1 / Permission Denied
Analysis:          PERMITTED: /etc/passwd read succeeded (Expected on Windows/WSL2 Docker Desktop due to missing AppArmor LSM)

--- [Test: Restricted Exec: /bin/bash] ---
Command executed:  `/bin/bash -c 'echo shell_executed'`
Actual Exit Code:  0
Actual Output:     shell_executed
Expected on Linux: Exit Code 126 / Permission Denied
Analysis:          PERMITTED: /bin/bash execution succeeded (Expected on Windows/WSL2 Docker Desktop due to missing AppArmor LSM)

--- [Test: Permitted Action: Python Execution] ---
Command executed:  `python -c 'import math; print(math.sqrt(16))'`
Actual Exit Code:  0
Actual Output:     4.0
Expected on Linux: Exit Code 0, Output: 4.0
Analysis:          PASS: Permitted Python standard library operation succeeded as designed

--- [Test: Permitted Action: Read /app/app.py] ---
Command executed:  `python -c 'with open("/app/app.py") as f: print(f.read()[:50])'`
Actual Exit Code:  0
Actual Output:     """\nSecure Flask Application for Exercise 5: Docke...
Expected on Linux: Exit Code 0, Application code accessible
Analysis:          PASS: Application directory access permitted and verified

===========================================================================
FINAL TEST RESULTS MATRIX
===========================================================================
Test Name                        | Exit Code  | Status
---------------------------------------------------------------------------
Flask HTTP Endpoint              | 0          | PASS - Flask application is reachable and serving traffic
Process Confinement Check        | 1          | UNCONFINED / INACTIVE - Host kernel does not enforce AppArmor LSM
Restricted Read: /etc/passwd     | 0          | PERMITTED - /etc/passwd read succeeded (Expected on Windows/WSL2 Docker Desktop due to missing AppArmor LSM)
Restricted Exec: /bin/bash       | 0          | PERMITTED - /bin/bash execution succeeded (Expected on Windows/WSL2 Docker Desktop due to missing AppArmor LSM)
Permitted Action: Python Execution | 0          | PASS - Permitted Python standard library operation succeeded as designed
Permitted Action: Read /app/app.py | 0          | PASS - Application directory access permitted and verified
===========================================================================

[CLEANUP] Stopping and removing test container 'af4bca586bb5'...
[SUCCESS] Test container cleaned up successfully.
```

---

## 9. Actual Test Results & Security Comparison Matrix

| Action / Operation | Windows 11 + Docker Desktop (WSL2) | Native Linux with Kernel AppArmor | Status / Meaning |
| :--- | :--- | :--- | :--- |
| **Flask HTTP Service (`GET /`)** | Exit Code 0, HTTP 200 OK | Exit Code 0, HTTP 200 OK | **PASSED**: Application functions identically. |
| **Python Standard Math Library** | Exit Code 0, Output: `4.0` | Exit Code 0, Output: `4.0` | **PASSED**: Permitted runtime operations succeed. |
| **Read `/app/app.py`** | Exit Code 0, Content accessible | Exit Code 0, Content accessible | **PASSED**: App directory access permitted. |
| **Process Confinement Attribute** | `Invalid argument` / `kernel` | `my-apparmor-profile (enforce)` | **ENVIRONMENT LIMIT**: Kernel LSM not active in WSL2. |
| **Read `/etc/passwd`** | Exit Code 0 (Allowed) | Exit Code 1 / Permission Denied | **DOCUMENTED**: AppArmor denial occurs only on Linux kernel. |
| **Execute `/bin/bash`** | Exit Code 0 (Executed) | Exit Code 126 / Permission Denied | **DOCUMENTED**: Binary execution denied on Linux kernel. |

---

## 10. Troubleshooting & Environment Limitations

### 1. AppArmor on Windows / Docker Desktop
- **Issue**: Running `docker run --security-opt apparmor=my-apparmor-profile` succeeds without error, but restricted actions are still permitted.
- **Root Cause**: Docker Desktop runs containers inside a lightweight WSL2 Linux VM whose kernel does not have AppArmor enabled in its active LSM list (`/sys/kernel/security/lsm`). The Docker engine records the security option in `HostConfig`, but `runc` cannot enforce it at the Linux kernel level.
- **Resolution**: Acknowledge the architectural limitation. Use `apply_apparmor.py` and `test_restricted_actions.py` to diagnose kernel support, and deploy to a native Ubuntu/Debian server for production enforcement.

### 2. WSL2 AppArmor Parser Error
- **Issue**: Running `sudo apparmor_parser -r my-apparmor-profile` inside WSL2 Ubuntu outputs:
  ```text
  Warning: unable to find a suitable fs in /proc/mounts, is it mounted?
  ```
- **Root Cause**: The WSL2 kernel lacks the `apparmorfs` security filesystem mount because `/sys/module/apparmor/parameters/enabled` is `N`.
- **Workaround for Syntax Validation**: Use `apparmor_parser -Q -v my-apparmor-profile` (skip kernel load flag). This parses, compiles, and validates the profile syntax without requiring kernel loading.

### 3. Port Conflicts on Localhost
- **Issue**: Error `port is already allocated: 0.0.0.0:5000`.
- **Resolution**: Both `apply_apparmor.py` and `test_restricted_actions.py` implement `find_available_port()`, dynamically locating open TCP ports if port 5000 is occupied by another local service.

---

## 11. Evidence Screenshots

All 8 required evidence screenshots are located in [`output/`](output/):

| Screenshot Filename | Proof & Technical Verification |
| :--- | :--- |
| `01-project-structure.png` | Verifies complete, independent folder layout containing `app.py`, `Dockerfile`, `requirements.txt`, `my-apparmor-profile`, `apply_apparmor.py`, `test_restricted_actions.py`, `README.md`, `.dockerignore`, and all `output/` files. |
| `02-docker-version.png` | Shows Docker Client 29.8.2, Docker Desktop Server 29.8.2, Linux kernel `6.18.33.2-microsoft-standard-WSL2`, and existing security options (`seccomp`, `cgroupns`). |
| `03-apparmor-status.png` | Audits Ubuntu WSL2 environment: shows `apparmor` parameter `N`, `apparmor filesystem is not mounted`, active LSMs `capability,landlock,yama,safesetid,selinux,ima`, and `apparmor_parser 4.0.1`. |
| `04-docker-image-build.png` | Confirms successful build of `flask-apparmor:latest` using `python:3.11-slim` with Flask 3.0.3 and unbuffered environment variables. |
| `05-flask-container-running.png` | Demonstrates the running container (`docker ps`) mapped to `0.0.0.0:5000`, along with live HTTP responses from `/` (200 OK greeting) and `/health` (healthy JSON). |
| `06-apparmor-profile-verification.png` | Shows AppArmor profile syntax validation (`Addition succeeded for "my-apparmor-profile"`), inspection of `HostConfig.SecurityOpt`, and the process attribute unconfined status. |
| `07-restricted-actions-test.png` | Captures terminal execution of `test_restricted_actions.py` covering reachability, confinement, file read restrictions, executable restrictions, and permitted Python operations. |
| `08-final-results.png` | Displays the final executive results matrix summarizing all test cases, exit codes, and comparisons between Windows/WSL2 and native Linux hosts. |

---

## 12. Exercise Handout Questions and Answers

### Question 1: What is the purpose of using AppArmor with Docker containers?
**Answer:**
AppArmor (Application Armor) is a Linux Security Module (LSM) that implements Mandatory Access Control (MAC). While Docker containers provide namespace isolation (PID, mount, network) and cgroup resource limits, containers share the underlying host Linux kernel. If an attacker escapes application confinement or achieves root privileges within a container, standard Unix permissions are insufficient to prevent unauthorized access. AppArmor confines containerized processes to a strict, pre-approved security profile, restricting what files can be read, written, or executed, what network sockets can be opened, and what Linux capabilities can be invoked, even if the process runs as UID 0 (root).

### Question 2: How do AppArmor profiles help secure a Docker container?
**Answer:**
AppArmor profiles enforce path-based access control directly inside the Linux kernel:
1. **File System Protection**: Denies read, write, or link access to sensitive host or container paths (such as `/etc/shadow`, `/etc/passwd`, `/root`, and `/var/log`).
2. **Execution Restrictions**: Prevents the execution of unauthorized interpreters or administrative tools (such as `/bin/bash`, `/bin/sh`, or package managers), preventing attackers from establishing interactive shells or downloading secondary payloads.
3. **Capability Filtering**: Drops dangerous Linux capabilities like `CAP_SYS_ADMIN`, `CAP_SYS_RAWIO`, and `CAP_SYS_PTRACE`, reducing kernel exploit surfaces.
4. **Network Restrictions**: Limits network socket creation to specific protocols (e.g. allowing `inet stream` for HTTP while blocking raw sockets or unexpected protocol families).

### Question 3: Why is it important to restrict access to sensitive directories such as `/etc/` and `/var/`?
**Answer:**
- `/etc/` contains critical system and security configuration files, including user databases (`/etc/passwd`), password hashes (`/etc/shadow`), group memberships (`/etc/group`), sudo privileges (`/etc/sudoers`), and DNS resolver settings (`/etc/resolv.conf`). If a web application vulnerability (such as Local File Inclusion / LFI) allows an attacker to read these files, they can enumerate accounts, crack passwords, or poison DNS configurations.
- `/var/` holds runtime state, spool files, system logs (`/var/log`), and database directories. Unauthorized write access can enable attackers to tamper with audit trails, wipe access logs to conceal their presence, or corrupt service state.

### Question 4: What other capabilities can you restrict using AppArmor profiles?
**Answer:**
Beyond file paths and binary execution, AppArmor allows fine-grained restriction of:
1. **Linux Capabilities**: Denying capabilities such as `CAP_SYS_ADMIN` (prevents mounting filesystems), `CAP_NET_ADMIN` (prevents altering network interfaces/firewalls), `CAP_SYS_RAWIO` (blocks raw device access), `CAP_SYS_PTRACE` (prevents tracing other processes), and `CAP_DAC_OVERRIDE` (prevents bypassing standard file read/write checks).
2. **Network Protocol Families**: Restricting access to specific socket types (`raw`, `packet`, `dgram`, `stream`) and address families (`inet`, `inet6`, `unix`).
3. **Mount Operations**: Blocking `mount`, `umount`, and `remount` system calls.
4. **Inter-Process Communication (IPC)**: Restricting UNIX domain sockets, signals (killing or signaling processes outside the profile), and POSIX message queues.
5. **Memory and Execution Attributes**: Blocking `mmap` with execute permissions (`m`), preventing arbitrary in-memory shellcode execution.

### Question 5: How can you verify if an AppArmor profile is successfully applied to a Docker container?
**Answer:**
True verification requires checking **both** the Docker configuration layer and the Linux kernel enforcement layer:
1. **Docker Configuration Layer**:
   - Using the Docker CLI: `docker inspect <container_id> --format '{{json .HostConfig.SecurityOpt}}'`
   - Using the Docker SDK for Python: `client.api.inspect_container(container.id)['HostConfig']['SecurityOpt']`
   - This verifies that Docker launched the container with the `apparmor=my-apparmor-profile` parameter.
2. **Kernel Enforcement Layer**:
   - Inspecting the container process attribute from inside the container:
     `cat /proc/self/attr/apparmor/current` (or `/proc/self/attr/current`)
     On a properly confined system, this returns: `my-apparmor-profile (enforce)`.
   - Inspecting from the host using `aa-status`:
     `sudo aa-status`
     This will display the container process PID under the `processes are in enforce mode` section associated with `my-apparmor-profile`.
