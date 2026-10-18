# Docker Networking Lab – Flask, MySQL and Redis

## 1. Project Overview

This project demonstrates Docker container networking using a custom user-defined bridge network. Three containers are used:

- **Flask:** A Python-based REST API.
- **MySQL:** A relational database container.
- **Redis:** An in-memory data store.

All three containers are connected to the same Docker bridge network, allowing them to communicate using their container names.

## 2. Technologies Used

- Docker Desktop
- Docker CLI
- Python
- Flask
- MySQL 8.0
- Redis
- Windows PowerShell

## 3. Project Structure

```text
A4_docker-networking-lab/
├── app.py
├── requirements.txt
├── Dockerfile
├── outputs/
│   ├── 01_docker_network_list.png
│   ├── 02_mysql_redis_running.png
│   ├── 03_flask_image_built.png
│   ├── 04_flask_api_response.png
│   ├── 05_all_containers_running.png
│   ├── 06_network_inspect_full.png
│   ├── 07_network_inspect_containers.png
│   ├── 08_flask_mysql_connectivity.png
│   ├── 09_flask_redis_connectivity.png
│   ├── 10_flask_mysql_connectivity_repeat.png
│   └── 11_flask_redis_connectivity_repeat.png
└── README.md
```

## 4. Implementation Steps

### Step 1: Create a Docker Network

Created a custom bridge network named `my-bridge-net`.

```powershell
docker network create --driver bridge my-bridge-net
```

### Step 2: Start the MySQL Container

Pulled the MySQL 8.0 image and started a container connected to the custom network.

```powershell
docker run -d --name mysql --network my-bridge-net -e "MYSQL_ROOT_PASSWORD=LabPass123!" -e "MYSQL_DATABASE=labdb" mysql:8.0
```

### Step 3: Start the Redis Container

Pulled the Redis image and started the Redis container on the same network.

```powershell
docker run -d --name redis --network my-bridge-net redis:latest
```

### Step 4: Build the Flask Docker Image

Created a Dockerfile to package the Flask application and its Python dependencies into a Docker image named `flask-api`.

```powershell
docker build -t flask-api .
```

### Step 5: Run the Flask Container

Started the Flask container on the custom network and mapped port 5001 on the host to port 5001 in the container.

```powershell
docker run -d --name flask --network my-bridge-net -p 5001:5001 flask-api
```

### Step 6: Verify Running Containers

Checked the status of the containers.

```powershell
docker ps
```

Verified that the Flask, MySQL and Redis containers were running.

### Step 7: Test the Flask API

Opened the following URL in a web browser:

```text
http://localhost:5001/about
```

The API returned a JSON response containing the API name, version and description.

### Step 8: Inspect the Docker Network

Listed the Docker networks and inspected the custom network.

```powershell
docker network ls
docker network inspect my-bridge-net
```

Verified that the Flask, MySQL and Redis containers were attached to `my-bridge-net`.

### Step 9: Test Container-to-Container Connectivity

Tested connectivity from the Flask container to MySQL:

```powershell
docker exec flask ping -c 4 mysql
```

Tested connectivity from the Flask container to Redis:

```powershell
docker exec flask ping -c 4 redis
```

Both tests returned successful ping replies with zero packet loss, demonstrating network connectivity and name resolution between the containers.

## 5. Results

The following outcomes were achieved:

- Created a custom Docker bridge network.
- Started MySQL and Redis containers on the custom network.
- Built a Docker image for the Flask API.
- Exposed the Flask API on port 5001.
- Verified the API response through a web browser.
- Inspected the network and confirmed that all three containers were attached.
- Successfully tested connectivity from Flask to MySQL and Redis using container names.
- Captured screenshots of the implementation and test results in the `outputs/` directory.

## 6. Conclusion

This lab demonstrates how Docker user-defined bridge networks enable containers to communicate using container names. It also covers building a Flask image, running multiple containers, mapping ports, inspecting networks and testing connectivity.

The lab provides practical experience with containerization and Docker networking fundamentals.
