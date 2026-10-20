# Exercise 9: Screenshot Capture Instructions

To collect visual evidence for Exercise 9 (Jenkins Multi-Stage Pipeline), capture the following screenshots and place them into this `output/` directory:

---

### Screenshot 1: Create Pipeline Item
- **URL**: `http://localhost:8080/view/all/newJob`
- **Target Filename**: `output/01_create_pipeline_job.png`
- **What to show**:
  - Item name entered as `Python-MultiStage-Pipeline`.
  - Radio button for **Pipeline** selected.
- **How to capture**:
  1. Click **New Item** on the Jenkins dashboard.
  2. Enter the name, select **Pipeline**, capture the modal, and save as `01_create_pipeline_job.png`.

---

### Screenshot 2: Pipeline Configuration (SCM or Script)
- **URL**: `http://localhost:8080/job/Python-MultiStage-Pipeline/configure`
- **Target Filename**: `output/02_pipeline_configuration.png`
- **What to show**:
  - The Pipeline section with either:
    - **Pipeline script from SCM** pointing to your Git repository, or
    - **Pipeline script** showing the declarative stages (`Build`, `Test`, `Deploy`, `Run Application`, `Test Application`).
- **How to capture**:
  1. Navigate to the job's configure page.
  2. Scroll down to the Pipeline section.
  3. Capture the screen and save as `02_pipeline_configuration.png`.

---

### Screenshot 3: Pipeline Stage View (All Green)
- **URL**: `http://localhost:8080/job/Python-MultiStage-Pipeline/`
- **Target Filename**: `output/03_pipeline_stage_view_green.png`
- **What to show**:
  - The Stage View matrix showing build `#1` with all green columns:
    - `Declarative: Checkout SCM`
    - `Build`
    - `Test`
    - `Deploy`
    - `Run Application`
    - `Test Application`
    - `Declarative: Post Actions`
- **How to capture**:
  1. Trigger **Build Now**.
  2. Wait until the build completes.
  3. Capture the **Stage View** section on the job main page and save as `03_pipeline_stage_view_green.png`.

---

### Screenshot 4: Test & Deploy Console Logs
- **URL**: `http://localhost:8080/job/Python-MultiStage-Pipeline/1/console`
- **Target Filename**: `output/04_pipeline_console_output.png`
- **What to show**:
  - The console output displaying the unittest run (`Ran 1 test... OK`), deployment copy step, and `Finished: SUCCESS`.
- **How to capture**:
  1. Click on build `#1` > **Console Output**.
  2. Scroll to the test execution and deploy steps.
  3. Capture the window and save as `04_pipeline_console_output.png`.

---

### Screenshot 5: Deployed Application HTTP Response
- **URL**: `http://localhost:5000/`
- **Target Filename**: `output/05_deployed_app_response.png`
- **What to show**:
  - Browser showing `http://localhost:5000` with the response:
    `Hello, Jenkins Multi-Stage Pipeline!`
- **How to capture**:
  1. Open a browser window to `http://localhost:5000`.
  2. Capture the displayed text and URL bar, and save as `05_deployed_app_response.png`.
