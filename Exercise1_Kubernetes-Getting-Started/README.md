# Kubernetes Nginx Pod Deployment

## Commands & Outputs

### 1. Install Chocolatey

Open **PowerShell as Administrator** and run:

``` powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
```

``` powershell
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
```

``` powershell
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

Close and reopen PowerShell, then verify:

``` powershell
choco --version
```

**Output**

``` text
2.7.4
```

### 2. Install Minikube

``` powershell
choco install minikube
```

**Output**

``` text
Minikube v1.38.1 already installed.
```

### 3. Start Minikube with Docker

``` powershell
minikube delete
minikube start --driver=docker
```

**Output**

``` text
Removed all traces of the "minikube" cluster.

Using the docker driver based on user configuration
Starting "minikube" primary control-plane node in "minikube" cluster
Creating docker container
Preparing Kubernetes
Configuring bridge CNI
Verifying Kubernetes components
Done! kubectl is now configured to use "minikube" cluster
```

### 4. Check Kubernetes Node

``` powershell
kubectl get nodes
```

**Output**

``` text
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   ...   v1.35.1
```

### 5. Create Nginx Pod

``` powershell
kubectl run hello-k8s --image=nginx --port=80
```

**Output**

``` text
pod/hello-k8s created
```

### 6. Check Pod

``` powershell
kubectl get pods
```

**Output**

``` text
NAME        READY   STATUS    RESTARTS   AGE
hello-k8s   1/1     Running   0          10s
```

### 7. Expose Pod

``` powershell
kubectl expose pod hello-k8s --type=NodePort --port=80
```

**Output**

``` text
service/hello-k8s exposed
```

### 8. Open Nginx

``` powershell
minikube service hello-k8s
```

**Output**

``` text
┌───────────┬───────────┬─────────────┬───────────────────────────┐
│ NAMESPACE │   NAME    │ TARGET PORT │            URL            │
├───────────┼───────────┼─────────────┼───────────────────────────┤
│ default   │ hello-k8s │ 80          │ http://192.168.49.2:31139 │
└───────────┴───────────┴─────────────┴───────────────────────────┘
* Starting tunnel for service hello-k8s.
┌───────────┬───────────┬─────────────┬────────────────────────┐
│ NAMESPACE │   NAME    │ TARGET PORT │          URL           │
├───────────┼───────────┼─────────────┼────────────────────────┤
│ default   │ hello-k8s │             │ http://127.0.0.1:54334 │
└───────────┴───────────┴─────────────┴────────────────────────┘
* Opening service default/hello-k8s in default browser...
! Because you are using a Docker driver on windows, the terminal needs to be open to run it.
```

### Final Result

``` text
Welcome to nginx!
If you see this page, nginx is successfully installed and working. Further configuration is required for the web server, reverse proxy, API gateway, load balancer, content cache, or other features.

For online documentation and support please refer to nginx.org.
To engage with the community please visit community.nginx.org.
For enterprise grade support, professional services, additional security features and capabilities please refer to f5.com/nginx.

Thank you for using nginx.
```
