# Exercise 6: Real-Time Operations Monitoring and Alerting (Quick-Commerce App)

## 1. Overview & Scenario
In this exercise, you simulate operations for **ZAPPTTO**, a fast-paced quick-commerce delivery service. To ensure operational efficiency and high SLA delivery performance, you implement an automated real-time monitoring and alerting stack utilizing:
- **Python (`prometheus_client`)**: Simulates live delivery metrics and serves an HTTP `/metrics` endpoint.
- **Prometheus**: Periodically scrapes metrics from the Python application and evaluates automated alerting rules.
- **Grafana**: Visualizes delivery metrics through an interactive operational dashboard.
- **Jenkins**: Automates the build, validation, and container deployment workflow via a declarative pipeline.

---

## 2. Directory Structure

```text
Exercise_6_Delivery_Monitoring/
├── delivery_metrics.py               # Python application simulating delivery metrics on port 8000
├── Dockerfile                        # Multi-platform container definition for delivery_metrics
├── requirements.txt                  # Python dependencies (prometheus-client)
├── prometheus.yml                    # Prometheus scrape configuration and alert rule mapping
├── alert_rules.yml                   # Threshold rules for pending deliveries and delivery duration
├── docker-compose.yml                # Unified container orchestration for the full monitoring stack
├── Jenkinsfile                       # Multi-stage CI/CD pipeline automation script
├── dashboards/
│   └── delivery_dashboard.json       # Exported Grafana dashboard JSON (4 delivery panels)
├── provisioning/
│   └── datasources/
│       └── prometheus.yml            # Automated Prometheus datasource configuration for Grafana
├── output/
│   ├── metrics_endpoint_sample.txt   # Verified capture of /metrics scrape endpoint
│   ├── alert_simulation_log.txt      # Execution log of delivery_metrics with active thresholds
│   ├── prometheus_targets.txt        # Scrape target status and rule evaluations
│   └── screenshot_instructions.md    # Step-by-step instructions for capturing UI screenshots
└── README.md                         # This documentation file
```

---

## 3. File Descriptions & Purpose

| File | Purpose |
| :--- | :--- |
| `delivery_metrics.py` | Defines Prometheus gauges (`total_deliveries`, `pending_deliveries`, `on_the_way_deliveries`) and summaries (`average_delivery_time`), serving them on HTTP port 8000. |
| `Dockerfile` | Packages `delivery_metrics.py` into a lightweight Python 3.10-slim container image. |
| `requirements.txt` | Pins Python library dependencies (`prometheus-client`). |
| `prometheus.yml` | Instructs Prometheus to scrape localhost (port 9090) and the delivery service (port 8000) every 5 seconds. |
| `alert_rules.yml` | Configures alerts: `HighPendingDeliveries` (> 10 pending for 15s) and `HighAverageDeliveryTime` (> 30s avg for 15s). |
| `docker-compose.yml` | Allows spinning up the metrics app, Prometheus, and Grafana simultaneously on a shared Docker bridge network. |
| `dashboards/delivery_dashboard.json` | Ready-to-import Grafana dashboard with panels for Total, Pending, On-the-Way, and Average Delivery Time. |
| `provisioning/datasources/prometheus.yml` | Grafana auto-provisioning file ensuring Prometheus is pre-configured as the default datasource. |
| `Jenkinsfile` | Declarative pipeline testing Docker availability, building the metrics container, and validating endpoints. |
| `output/` | Directory containing verified command output logs and screenshot capture instructions. |

---

## 4. Prerequisites
- **Python**: 3.8+ (with `pip`)
- **Docker & Docker Compose**: Installed and running
- **Curl / Web Browser**: For accessing dashboards and endpoints

---

## 5. Execution Steps

### Option A: Local Python & Containerized Monitoring
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the metrics simulation**:
   ```bash
   python delivery_metrics.py
   ```
3. **Verify the metrics endpoint**:
   ```bash
   curl http://localhost:8000/metrics
   ```
4. **Run Prometheus**:
   ```bash
   docker run -d --name prometheus -p 9090:9090 \
     -v ${PWD}/prometheus.yml:/etc/prometheus/prometheus.yml \
     -v ${PWD}/alert_rules.yml:/etc/prometheus/alert_rules.yml \
     prom/prometheus
   ```
5. **Run Grafana**:
   ```bash
   docker run -d --name grafana -p 3000:3000 grafana/grafana
   ```

### Option B: Unified Docker Compose (Recommended)
From the `Exercise_6_Delivery_Monitoring/` folder, execute:
```bash
docker compose up -d --build
```
This starts:
- Metrics App on `http://localhost:8000/metrics`
- Prometheus on `http://localhost:9090`
- Grafana on `http://localhost:3000` (auto-connected to Prometheus)

### Option C: Jenkins Pipeline Automation
1. Ensure Jenkins is accessible (`http://localhost:8080`).
2. Create a new Pipeline job named `Delivery-Monitoring-Pipeline`.
3. Select **Pipeline script** and copy the contents of `Jenkinsfile`.
4. Click **Build Now** to execute the complete build and verification workflow.

---

## 6. Accessing Dashboards & Simulating Alerts

1. **Prometheus Targets**:
   - Navigate to `http://localhost:9090/targets`.
   - Confirm both `prometheus` and `delivery_service` are marked in green as **UP**.
2. **Prometheus Alerts**:
   - Navigate to `http://localhost:9090/alerts`.
   - When pending deliveries exceed 10 for more than 15 seconds, the `HighPendingDeliveries` alert transitions from `PENDING` to `FIRING`.
3. **Grafana Dashboard**:
   - Access `http://localhost:3000` (Credentials: `admin` / `admin`).
   - Go to **Dashboards** > **New** > **Import**.
   - Upload `dashboards/delivery_dashboard.json` or paste its JSON content.
   - Click **Import** to view real-time delivery graphs and stat tiles.

---

## 7. Verification & Actual Test Results

Verification was performed on the environment with the following recorded results:
- **Metrics Endpoint**: Successfully returned HTTP 200 with active metrics:
  ```text
  total_deliveries 58.0
  pending_deliveries 18.0
  on_the_way_deliveries 5.0
  average_delivery_time_count 4.0
  average_delivery_time_sum 128.09
  ```
- Detailed raw metric evidence is stored in [`output/metrics_endpoint_sample.txt`](file:///d:/devops_lab/Exercise_6_Delivery_Monitoring/output/metrics_endpoint_sample.txt).
- Simulation console log is saved in [`output/alert_simulation_log.txt`](file:///d:/devops_lab/Exercise_6_Delivery_Monitoring/output/alert_simulation_log.txt).

---

## 8. Troubleshooting

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| Prometheus shows `delivery_service` target as `DOWN` | Container cannot reach host localhost | Ensure `host.docker.internal:8000` or the Docker network service name `delivery_metrics:8000` is used in `prometheus.yml`. |
| Port 8000 or 9090 already in use | Conflicting existing processes or containers | Check active containers via `docker ps` and terminate conflicting containers using `docker stop <id>`. |
| Grafana cannot connect to Prometheus | Incorrect datasource URL | Inside Docker Compose, set URL to `http://prometheus:9090`. For standalone containers, use `http://host.docker.internal:9090`. |

---

## 9. Cleanup

To tear down all containers and networks:
```bash
docker compose down -v
```
Or if containers were run individually:
```bash
docker rm -f delivery_metrics prometheus grafana
```
