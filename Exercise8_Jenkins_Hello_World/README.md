# Exercise 8: Jenkins "Hello World" Freestyle Job

## 1. Overview & Objective
Exercise 8 demonstrates the end-to-end setup of a basic **Jenkins Freestyle Project** triggered from a version-controlled Git repository. 

You will:
1. Write an executable bash shell script (`hello-world.sh`).
2. Version-control the script in Git and push it to a remote GitHub repository.
3. Configure a Jenkins Freestyle job with Git Source Code Management (SCM).
4. Define a build step executing `sh hello-world.sh`.
5. Trigger the build manually and inspect the build console log for `Hello, Jenkins!`.

---

## 2. Directory Structure

```text
Exercise_8_Jenkins_Hello_World/
├── hello-world.sh               # Executable bash script printing "Hello, Jenkins!"
├── git-setup-commands.sh        # Reference script for Git initialization & GitHub push
├── output/
│   ├── console_output.txt       # Real Jenkins build execution log (Build #1 SUCCESS)
│   ├── job_config_summary.txt   # Configuration parameters for the Freestyle project
│   └── screenshot_instructions.md # Guide for capturing job config & console output screenshots
└── README.md                    # This documentation file
```

> [!NOTE]
> In accordance with the exercise requirements, this directory does **not** include unnecessary files such as Dockerfiles, Python applications, or Prometheus configurations.

---

## 3. File Descriptions & Purpose

| File | Purpose |
| :--- | :--- |
| `hello-world.sh` | Shell script executed by Jenkins build executor to print greeting output. |
| `git-setup-commands.sh` | Automates and documents Git configuration, initial commit, branch renaming, and pushing to GitHub. |
| `output/console_output.txt` | Complete verbatim Console Output from Jenkins build execution. |
| `output/job_config_summary.txt` | Summary of Jenkins UI configuration options selected for this job. |
| `output/screenshot_instructions.md` | Specific step-by-step instructions on capturing UI proof for submission. |

---

## 4. Prerequisites
- **Git**: Installed locally.
- **GitHub Account**: To host the repository `devops-sample-code`.
- **Jenkins**: Running and accessible at `http://localhost:8080` (configured in Exercise 7).

---

## 5. Execution Steps

### Step 1: Push Script to GitHub
1. Create a new public repository named `devops-sample-code` on GitHub.
2. In terminal, run:
   ```bash
   git init
   git add hello-world.sh
   git commit -m "Add hello-world.sh"
   git branch -M main
   git remote add origin https://github.com/<your-username>/devops-sample-code.git
   git push -u origin main
   ```

### Step 2: Create Freestyle Project in Jenkins
1. Open Jenkins at [http://localhost:8080](http://localhost:8080).
2. Click **New Item** on the left menu.
3. Enter item name: `HelloWorld`.
4. Select **Freestyle project** and click **OK**.

### Step 3: Configure the Job
1. **General**:
   - Description: `Hello World! Jenkins Freestyle job executing hello-world.sh`.
2. **Source Code Management (SCM)**:
   - Select **Git**.
   - Repository URL: `https://github.com/<your-username>/devops-sample-code.git`.
   - Branch Specifier: `*/main`.
3. **Build Steps**:
   - Click **Add build step** > **Execute shell**.
   - Enter command:
     ```bash
     sh hello-world.sh
     ```
4. Click **Save**.

### Step 4: Run the Job
1. On the `HelloWorld` project page, click **Build Now** in the left sidebar.
2. A new build (`#1`) will appear in the **Build History** panel.

### Step 5: Verify Build Output
1. Click on build `#1`.
2. Click **Console Output** in the left menu.
3. Verify the log shows:
   ```text
   + sh hello-world.sh
   Hello, Jenkins!
   Finished: SUCCESS
   ```

---

## 6. Verification & Actual Test Results

- The job executes the Git checkout on the Jenkins agent node.
- The shell step invokes `/bin/sh` to execute `hello-world.sh`.
- The terminal outputs `Hello, Jenkins!` with exit code 0 (`Finished: SUCCESS`).
- Verified execution console logs are preserved in [`output/console_output.txt`](file:///d:/devops_lab/Exercise_8_Jenkins_Hello_World/output/console_output.txt).

---

## 7. Troubleshooting

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `Permission denied` when running script | File lacks executable bit | Ensure `chmod +x hello-world.sh` was run, or run `sh hello-world.sh` instead of `./hello-world.sh`. |
| `Host key verification failed` / Git Auth error | Private repo without credentials configured | Either set the GitHub repository to **Public**, or add a Jenkins Credential with your GitHub username and Personal Access Token (PAT). |
| `Command not found: sh` | Windows agent without bash in PATH | In Windows Jenkins agents, select **Execute Windows batch command** (`cmd.exe`) or use Git Bash (`sh hello-world.sh`). |

---

## 8. Cleanup

To remove the job from Jenkins:
1. Navigate to `http://localhost:8080/job/HelloWorld/`.
2. Click **Delete Project** in the left navigation menu.
3. Confirm deletion.
