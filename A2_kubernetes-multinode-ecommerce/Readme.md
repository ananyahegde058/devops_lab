A2 - Kubernetes Multi-Node E-Commerce

Project Directory

A2_kubernetes-multinode-ecommerce/
├── screenshots/
│   ├── Access_shopping_cart.png
│   ├── deployments_replicasets.png
│   ├── docker-images.png
│   ├── final-output.png
│   ├── ls.png
│   ├── minikube-nodes.png
│   └── pods-distributed.png
├── Dockerfile.product
├── Dockerfile.shopping
├── product_catalog.py
├── product_catalog_deployment.yaml
├── product_catalog_service.yaml
├── shopping_cart.py
├── shopping_cart_deployment.yaml
└── shopping_cart_service.yaml

Commands Used

1. Clean Minikube

minikube stop
minikube delete

2. Create 3-Node Cluster

minikube start --nodes 3 -p devops-multinode --driver=docker --force
minikube status -p devops-multinode
kubectl get nodes
kubectl get nodes -o wide

3. Enable Registry

minikube -p devops-multinode addons enable registry

4. Build Docker Images

docker build -t product-catalog:latest -f Dockerfile.product .
docker build -t shopping-cart:latest -f Dockerfile.shopping .
docker images

5. Load Images into Minikube

minikube -p devops-multinode image load product-catalog:latest
minikube -p devops-multinode image load shopping-cart:latest
minikube -p devops-multinode ssh -- docker images

6. Deploy Applications

kubectl apply -f product_catalog_deployment.yaml
kubectl apply -f shopping_cart_deployment.yaml
kubectl get deployments

7. Check ReplicaSets and Pods

kubectl get rs
kubectl get deployment,rs,pods
kubectl get pods
kubectl get pods -o wide

8. Deploy Services

kubectl apply -f product_catalog_service.yaml
kubectl apply -f shopping_cart_service.yaml
kubectl get svc
kubectl get endpoints

9. Access Services

minikube -p devops-multinode service product-catalog-service
minikube -p devops-multinode service shopping-cart-service

Use the localhost URLs shown by Minikube.

10. Test Product Catalog

curl http://127.0.0.1:<PRODUCT_PORT>/products

11. Test Shopping Cart

curl http://127.0.0.1:<CART_PORT>/cart

curl -X POST http://127.0.0.1:<CART_PORT>/cart ^
-H "Content-Type: application/json" ^
-d "{"id":1,"name":"Laptop","quantity":1}"

In WSL/Linux, use \ instead of ^ for multiline commands.

12. Test Pod Fault Tolerance

kubectl get pods -o wide
kubectl delete pod <shopping-cart-pod-name>
kubectl get pods -o wide

Kubernetes automatically creates a replacement Pod to maintain 3 replicas.

Final Verification

kubectl get nodes
kubectl get deployments
kubectl get rs
kubectl get pods -o wide
kubectl get svc
kubectl get endpoints
kubectl get all

Result

3-node Minikube cluster created.

Product Catalog deployed with 2 replicas.

Shopping Cart deployed with 3 replicas.

Pod anti-affinity distributes replicas across nodes.

Kubernetes Deployments manage the ReplicaSets.

Services expose both applications.

APIs tested using curl