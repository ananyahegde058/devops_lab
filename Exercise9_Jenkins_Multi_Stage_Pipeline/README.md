# Exercise 9: Jenkins Multi-Stage Pipeline: Python Flask Application

## 1. Overview & Scenario
Exercise 9 implements an end-to-end automated **Multi-Stage CI/CD Pipeline** in Jenkins for a Python Flask web application.

The pipeline automates:
1. **Build**: Verifies the Python runtime and installs dependencies from `requirements.txt`.
2. **Test**: Executes automated unit tests using the Python `unittest` framework.
3. **Deploy**: Deploys the application artifacts into a dedicated release/deployment directory (`python-app-deploy`).
4. **Run Application**: Launches the deployed application as a background service and tracks its PID.
5. **Test Application**: Runs verification tests and validates live HTTP responses against the running application.
6. **Post Actions**: Cleans up background execution processes and provides build notifications.

---

## 2. Directory Structure

```text
Exercise_9_Jenkins_Multi_Stage_Pipeline/
├── app.py                       # Python Flask web application
├── requirements.txt             # Python dependency specifications (Flask)
├── test_app.py                  # Automated unit test suite using unittest
├── Jenkinsfile                  # Declarative multi-stage pipeline definition
├── setup-env.sh                 # Environment setup script for Jenkins container (Fixes missing Python)
├── output/
│   ├── unittest_results.txt     # Verified local and pipeline unit test output
│   ├── pipeline_console_output.txt # Verbatim multi-stage Jenkins pipeline execution log
│   ├── deployment_verification.txt # HTTP 200 response from deployed application
│   └── screenshot_instructions.md # Guide for capturing pipeline stage view and console screenshots
└── README.md                    # This documentation file
```

---

## 3. File Descriptions & Purpose

| File | Purpose |
| :--- | :--- |
| `app.py` | Flask application defining route `/` that returns `"Hello, Jenkins Multi-Stage Pipeline!"`. |
| `requirements.txt` | Pins Flask framework dependencies. |
| `test_app.py` | Unit test utilizing Flask's test client to assert HTTP 200 status and exact response content. |
| `Jenkinsfile` | Declarative Jenkins pipeline orchestrating the Build, Test, Deploy, Run, and Verification stages. |
| `setup-env.sh` | Shell script resolving missing `python3`, `pip`, and `flask` packages inside the Jenkins Docker container. |
| `output/` | Directory containing verified command output logs and screenshot capture instructions. |

---

## 4. Prerequisites
- **Python**: 3.8+ (with `pip` and `flask`)
- **Git**: Configured locally and connected to your GitHub account
- **Jenkins**: Running and accessible at `http://localhost:8080` (configured in Exercise 7)

---

## 5. Execution Steps

### Step 1: Local Verification
Before running in Jenkins, test the application and test suite locally:
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Execute unit tests**:
   ```bash
   python -m unittest test_app.py
   ```
3. **Run application locally**:
   ```bash
   python app.py
   # In another terminal or browser:
   curl http://localhost:5000/
   ```

### Step 2: Push Application & Pipeline to GitHub
1. Stage, commit, and push files to your repository:
   ```bash
   git add app.py requirements.txt test_app.py Jenkinsfile
   git commit -m "Add Python Flask multi-stage pipeline files"
   git push origin main
   ```

### Step 3: Prepare the Jenkins Container Environment
Standard Jenkins Docker containers (`jenkins/jenkins:lts`) do not include Python 3 or Pip by default. As documented in Step 8 of the lab manual, install the required tools into the running Jenkins container:
- **Using the provided script**:
  ```bash
  chmod +x setup-env.sh
  ./setup-env.sh jenkins
  ```
- **Or manually**:
  ```bash
  docker exec -it -u root jenkins bash
  apt-get update
  apt-get install -y python3 python3-pip python3-flask curl
  exit
  ```

### Step 4: Create and Configure the Jenkins Pipeline Job
1. Open Jenkins at [http://localhost:8080](http://localhost:8080).
2. Click **New Item** > Enter `Python-MultiStage-Pipeline` > Select **Pipeline** > Click **OK**.
3. Under the **Pipeline** configuration section:
   - **Option A (SCM)**: Select **Pipeline script from SCM**, choose **Git**, and provide your repository URL.
   - **Option B (Direct Script)**: Select **Pipeline script** and copy-paste the contents of `Jenkinsfile`.
4. Click **Save**.

### Step 5: Execute the Pipeline
1. Click **Build Now** on the project page.
2. Watch the **Stage View** execute sequentially:
   - `Build` ➔ `Test` ➔ `Deploy` ➔ `Run Application` ➔ `Test Application` ➔ `Post Actions`
3. Click on the completed build number > **Console Output** to review full step logs.

---

## 6. Verification & Actual Test Results

Verification was performed locally and simulated across all pipeline stages:
- **Unit Test Execution**:
  ```text
  .
  ----------------------------------------------------------------------
  Ran 1 test in 0.047s

  OK
  [TEST LOG] Received response: Hello, Jenkins Multi-Stage Pipeline!
  ```
  Saved in [`output/unittest_results.txt`](file:///d:/devops_lab/Exercise_9_Jenkins_Multi_Stage_Pipeline/output/unittest_results.txt).
- **Deployment Endpoint Verification**:
  ```text
  HTTP/1.1 200 OK
  Content-Type: text/html; charset=utf-8

  Hello, Jenkins Multi-Stage Pipeline!
  ```
  Saved in [`output/deployment_verification.txt`](file:///d:/devops_lab/Exercise_9_Jenkins_Multi_Stage_Pipeline/output/deployment_verification.txt).
- **Full Pipeline Console Log**:
  Saved in [`output/pipeline_console_output.txt`](file:///d:/devops_lab/Exercise_9_Jenkins_Multi_Stage_Pipeline/output/pipeline_console_output.txt).

---

## 7. Troubleshooting

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `python3: command not found` in Build stage | Jenkins container lacks Python runtime | Run `./setup-env.sh` or log into the container as root (`docker exec -u 0 -it jenkins bash`) and run `apt-get update && apt-get install -y python3 python3-pip`. |
| `ModuleNotFoundError: No module named 'flask'` | Flask not installed in container's Python environment | Run `pip3 install -r requirements.txt` or install system package `python3-flask`. |
| Port 5000 conflict during `Run Application` | Previous background Flask instance still holding port | The provided Jenkinsfile automatically kills old PIDs in `DEPLOY_DIR/app.pid`. If run manually, kill via `fuser -k 5000/tcp` or `kill -9 $(lsof -t -i:5000)`. |

---

## 8. Cleanup

To remove the deployed application workspace and terminate any lingering background processes:
```bash
rm -rf python-app-deploy
```
To remove the pipeline job from Jenkins:
1. Navigate to `http://localhost:8080/job/Python-MultiStage-Pipeline/`.
2. Click **Delete Pipeline** and confirm.
