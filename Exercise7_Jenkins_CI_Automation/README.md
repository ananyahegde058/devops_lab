# Exercise 7: Continuous Integration (CI) and Jenkins Setup

## 1. Overview & Objective
Exercise 7 introduces the foundational concepts of **Continuous Integration (CI)**, evaluates the landscape of 10 modern CI/CD automation platforms, and establishes a production-grade, containerized **Jenkins LTS** environment using Docker.

By completing this exercise, you will understand:
- The core principles and operational loop of Continuous Integration.
- How Jenkins compares against GitLab CI, GitHub Actions, CircleCI, Azure Pipelines, and others.
- The Master-Agent distributed architecture of Jenkins.
- Containerized deployment, persistent volume management, password extraction, and the initial setup wizard.

---

## 2. Directory Structure

```text
Exercise_7_Jenkins_CI_Automation/
├── docker-compose.yml                # Docker Compose definition with volume persistence
├── setup-jenkins.sh                  # Bash automation script for Linux/macOS
├── setup-jenkins.ps1                 # PowerShell automation script for Windows
├── ci_tools_comparison.md            # In-depth architectural guide & 10 CI tools comparison
├── output/
│   ├── jenkins_container_status.txt  # Verified docker run & process status evidence
│   ├── initial_admin_password_sample.txt # Verified admin secret extraction output
│   └── screenshot_instructions.md    # Instructions for capturing setup wizard screenshots
└── README.md                         # This documentation file
```

---

## 3. File Descriptions & Purpose

| File | Purpose |
| :--- | :--- |
| `docker-compose.yml` | Declarative service definition running `jenkins/jenkins:lts` with mapped ports `8080` (HTTP) and `50000` (Agent listener) and a named volume `jenkins_home`. |
| `setup-jenkins.sh` | Shell script automating container removal, startup, boot readiness polling, and automatic initial admin password retrieval. |
| `setup-jenkins.ps1` | Native PowerShell version of the deployment automation tailored for Windows host systems. |
| `ci_tools_comparison.md` | Comprehensive study covering CI definitions, benefits, developer workflows, comparison matrix of 10 CI tools, and Jenkins core concepts. |
| `output/` | Directory containing verified command output logs and screenshot capture instructions. |

---

## 4. Prerequisites
- **Docker**: Version 20.10+ (Docker Desktop running on Windows/macOS or Docker Engine on Linux)
- **Web Browser**: Chrome, Firefox, or Edge
- **System Memory**: At least 2GB of RAM allocated to Docker

---

## 5. Execution Steps

### Method 1: Using the Automated PowerShell Script (Windows)
Run PowerShell from this directory:
```powershell
.\setup-jenkins.ps1
```
The script will start the container, poll until Jenkins logs "Jenkins is fully up and running", and print your initial admin password in the terminal.

### Method 2: Using the Automated Bash Script (Linux / WSL / macOS)
```bash
chmod +x setup-jenkins.sh
./setup-jenkins.sh
```

### Method 3: Using Docker Compose
```bash
docker compose up -d
```
To view logs:
```bash
docker compose logs -f jenkins
```

### Method 4: Manual Docker Command
```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

---

## 6. Initial Configuration Walkthrough

1. **Access Web Interface**:
   Open [http://localhost:8080](http://localhost:8080) in your web browser.
2. **Retrieve Admin Password**:
   If not using the setup scripts, run:
   ```bash
   docker exec -it jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```
3. **Unlock Jenkins**:
   Paste the 32-character key into the "Administrator password" box and click **Continue**.
4. **Install Plugins**:
   Select **Install suggested plugins** and allow the automated installer to fetch standard plugins (Git, Pipeline, Ant, Gradle, Credentials).
5. **Create First Admin User**:
   Provide your preferred username, password, and email address. Click **Save and Continue**.
6. **Instance Configuration**:
   Confirm Jenkins URL as `http://localhost:8080/` and click **Save and Finish**.
7. **Start Using Jenkins**:
   Click **Start using Jenkins** to enter the main dashboard.

---

## 7. Verification & Actual Test Results

- **Container Status**: Container starts with ports `8080->8080` and `50000->50000` mapped and volume `jenkins_home` mounted.
- **Admin Password**: Successfully extracted from `/var/jenkins_home/secrets/initialAdminPassword`.
- **HTTP Readiness**: Endpoint `http://localhost:8080/login` responds with HTTP `200 OK`.
- Detailed logs are recorded in [`output/jenkins_container_status.txt`](file:///d:/devops_lab/Exercise_7_Jenkins_CI_Automation/output/jenkins_container_status.txt).
- Extracted secret proof is stored in [`output/initial_admin_password_sample.txt`](file:///d:/devops_lab/Exercise_7_Jenkins_CI_Automation/output/initial_admin_password_sample.txt).

---

## 8. Troubleshooting

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `Port 8080 is already allocated` | Another local service (or previous container) occupies 8080 | Run `docker ps` to find conflicting container, or change port mapping to `-p 8081:8080`. |
| Container exits immediately | Permission issues with mounted directory | Use Docker named volume `jenkins_home` instead of host bind mounts to ensure correct UID `1000` ownership. |
| Setup Wizard doesn't load | Network latency while pulling plugins | Wait 30-60 seconds for JVM warm-up. Check progress with `docker logs -f jenkins`. |

---

## 9. Cleanup

To stop and remove the Jenkins container while preserving your data volume:
```bash
docker compose down
# or
docker stop jenkins && docker rm jenkins
```

To completely delete all Jenkins data (including jobs, credentials, and plugins):
```bash
docker compose down -v
# or
docker volume rm jenkins_home
```
