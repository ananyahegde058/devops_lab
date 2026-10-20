# Exercise 8: Screenshot Capture Instructions

To capture visual evidence for Exercise 8 (Jenkins "Hello World" Job), follow these steps and save images directly in this `output/` folder:

---

### Screenshot 1: Create New Freestyle Project
- **URL**: `http://localhost:8080/view/all/newJob`
- **Target Filename**: `output/01_create_freestyle_job.png`
- **What to show**:
  - Item name entered as `HelloWorld`.
  - Radio button for **Freestyle project** selected.
- **How to capture**:
  1. On the Jenkins dashboard, click **New Item**.
  2. Type `HelloWorld` and select **Freestyle project**.
  3. Capture the screen before clicking OK, and save as `01_create_freestyle_job.png`.

---

### Screenshot 2: Configure Git SCM & Build Step
- **URL**: `http://localhost:8080/job/HelloWorld/configure`
- **Target Filename**: `output/02_job_configuration.png`
- **What to show**:
  - Source Code Management section with **Git** selected and your repository URL (`https://github.com/<username>/devops-sample-code.git`).
  - Build Steps section showing **Execute shell** with `sh hello-world.sh`.
- **How to capture**:
  1. In the job configuration page, scroll through SCM and Build Steps.
  2. Capture the configuration panels and save as `02_job_configuration.png`.

---

### Screenshot 3: Trigger Build Now
- **URL**: `http://localhost:8080/job/HelloWorld/`
- **Target Filename**: `output/03_build_history_success.png`
- **What to show**:
  - Left navigation showing **Build Now** clicked.
  - **Build History** table displaying `#1` with a blue (success) ball icon and timestamp.
- **How to capture**:
  1. Click **Build Now** on the left menu.
  2. Wait 2-5 seconds until the build completes with a blue circle.
  3. Capture the job overview page and save as `03_build_history_success.png`.

---

### Screenshot 4: Build Console Output
- **URL**: `http://localhost:8080/job/HelloWorld/1/console`
- **Target Filename**: `output/04_console_output.png`
- **What to show**:
  - Console text showing:
    ```text
    + sh hello-world.sh
    Hello, Jenkins!
    Finished: SUCCESS
    ```
- **How to capture**:
  1. Click on build `#1` under Build History.
  2. Select **Console Output** from the sub-menu.
  3. Capture the full browser window and save as `04_console_output.png`.
