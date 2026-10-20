# Flash Sale Application — Flask and Kubernetes ReplicaSet

## 1. Project Overview

This project demonstrates how to deploy and scale a Flask web application using Kubernetes ReplicaSets on a single-node Minikube cluster.

The application simulates an e-commerce flash sale, similar to Flipkart Big Billion Days or Amazon Prime Day. It provides a homepage, a simulated purchase endpoint, and a health-check endpoint.

Kubernetes ReplicaSets ensure that the desired number of application Pods remain running. If a Pod fails or is deleted, Kubernetes automatically creates a replacement.

## 2. Objectives

- Understand Kubernetes Pods, ReplicaSets, and Services.
- Deploy a Flask application using Docker and Minikube.
- Create and manage three application replicas.
- Scale the ReplicaSet from three to five Pods.
- Observe Pod distribution across a single node.
- Test automatic Pod replacement.
- Inspect ReplicaSet details and health probes.

## 3. Technologies Used

- Python 3.11
- Flask
- Gunicorn
- Docker Desktop
- Kubernetes
- Minikube
- kubectl

## 4. Application Endpoints

| Endpoint | Description |
|---|---|
| `/` | Displays a welcome message, Pod hostname, and timestamp. |
| `/buy?user=123` | Simulates a purchase and returns a randomly selected product, user ID, time, and serving Pod hostname. |
| `/health` | Returns the application's health status and Pod hostname. |

**Note:** The purchase endpoint is a simulation. It does not process real payments or store orders.

## 5. Docker Image Creation

A Dockerfile is used to containerize the Flask application.

The image is built with the following command:

```powershell
minikube image build -t flashsale:1.0 .
```

The image is built directly inside Minikube so that the local Kubernetes cluster can use it without requiring a Docker Hub push.

## 6. Minikube Setup

Start the Minikube cluster:

```powershell
minikube start --driver=docker --cpus=2 --memory=3000
```

Verify the node status:

```powershell
kubectl get nodes
```

The node should show `Ready` status.

## 7. Deploy the ReplicaSet and Service

Apply the Kubernetes configuration:

```powershell
kubectl apply -f flashsale-replicaset.yaml
```

Verify the ReplicaSet:

```powershell
kubectl get rs
```

Verify the Pods:

```powershell
kubectl get pods
```

Initially, the ReplicaSet is configured to maintain three replicas of the Flash Sale application.

The Kubernetes Service named `flashsale-svc` exposes the application internally on port 80 and forwards requests to container port 5000.

## 8. Access the Application

Run the following command:

```powershell
minikube service flashsale-svc --url
```

Keep this terminal open and access the URL displayed in the terminal using a web browser.

Test the following endpoints:

- Homepage: `http://127.0.0.1:<port>/`
- Buy endpoint: `http://127.0.0.1:<port>/buy?user=123`
- Health endpoint: `http://127.0.0.1:<port>/health`

Replace `<port>` with the port printed by Minikube.

The responses include the hostname of the Pod that handled the request.

## 9. Scaling the ReplicaSet

Initially, the ReplicaSet maintains three Pods.

To increase the number of replicas to five, execute:

```powershell
kubectl scale rs flashsale-rs --replicas=5
```

Verify the updated ReplicaSet:

```powershell
kubectl get rs
```

Verify the Pods:

```powershell
kubectl get pods
```

Kubernetes creates two additional Pods to reach the desired replica count of five.

## 10. Pod Distribution

To view the Pod IP addresses and the nodes hosting them, execute:

```powershell
kubectl get pods -o wide
```

Since the exercise uses a single-node Minikube cluster, all five Pods run on the `minikube` node.

## 11. Testing ReplicaSet Self-Healing

First, list the Pods:

```powershell
kubectl get pods
```

Copy one actual Pod name and delete it:

```powershell
kubectl delete pod <pod-name>
```

Replace `<pod-name>` with the actual name of one of your Pods.

Verify the Pods again:

```powershell
kubectl get pods
```

Kubernetes automatically creates a replacement Pod to maintain the desired number of five replicas.

## 12. Inspecting ReplicaSet Details

Execute the following command:

```powershell
kubectl describe rs flashsale-rs
```

This command displays:

- ReplicaSet name and labels.
- Desired, current, and ready replica counts.
- Container image and port.
- Resource requests and limits.
- Readiness and liveness probes.
- Events related to Pod creation.

## 13. Results and Observations

1. The Flask application was deployed successfully on Minikube.
2. The initial ReplicaSet maintained three running Pods.
3. The ReplicaSet was scaled to five replicas.
4. The homepage and simulated purchase endpoint returned JSON responses.
5. The serving Pod hostname was visible in the application responses.
6. All five Pods were running on the single Minikube node.
7. The ReplicaSet configuration included readiness and liveness probes.
8. Deleting a Pod causes Kubernetes to create a replacement and restore the desired replica count.

## 14. Key Learnings

**Pod Distribution:** Each Pod runs an instance of the same application. Multiple replicas provide additional capacity.

**Resiliency:** A ReplicaSet maintains the desired number of Pods by creating replacements when Pods are deleted or become unavailable.

**Scalability:** The number of replicas can be increased or decreased according to application requirements.

**Load Distribution:** A Kubernetes Service provides a common endpoint for accessing the application and routes requests to eligible Pods. Requests are not guaranteed to be distributed evenly.

**Resource Efficiency:** Replicas can be adjusted to match demand. This exercise uses manual scaling; automatic traffic-based scaling requires additional configuration.

**Single-Node Limitation:** All Pods run on one node, so this exercise does not provide protection against node failure.

## 15. Screenshot Evidence

The `output` folder contains screenshots documenting the practical implementation:

- `01-replicaset-scaled-to-5-pods.png` — ReplicaSet scaled to five Pods.
- `02-pod-distribution-across-single-node.png