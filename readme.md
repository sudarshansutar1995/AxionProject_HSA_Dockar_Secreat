# HSA + Docker + Kubernetes Secret + Git/GitHub — Full Flow

## 1. Overall Architecture

Humare project ka basic flow:

```text
Developer Code
     |
     v
Dockerfile
     |
     v
Docker Image
     |
     v
Azure Container Registry (ACR)
     |
     v
AKS
     |
     +----------------------+
     |                      |
     v                      v
Kubernetes Deployment    Kubernetes Secret
     |                      |
     v                      v
    Pods              Environment Variables
     |
     v
Kubernetes Service
     |
     v
Application Gateway / Ingress
     |
     v
Internet / Browser

```

Git flow:

```text
Local Project
     |
     v
git add .
     |
     v
git commit
     |
     v
git push
     |
     v
GitHub Repository

```

---

# 2. Project Structure

Example:

```text
AxionProject_HSA_Dockar_Secreat/
│
├── axion-data-simulator/
│   ├── simulator.py
│   └── Manifest/
│       ├── datasimulator.yaml
│       └── data-simu-secreat.yaml
│
├── axion-ingestion-service/
│   ├── config.py
│   └── Manifest/
│       ├── ingestion.yaml
│       ├── ingestion-hsa.yaml
│       └── ingestiom-secreat.yaml
│
├── axion-telemetry-query-service/
│   ├── config.py
│   └── Manifest/
│       ├── telemetry.yaml
│       ├── telemetry-hsa.yaml
│       └── telemetry-secreat.yaml
│
└── axion-ui/
    └── Manifest/
        ├── axionui.yaml
        ├── axionui-hsa.yaml
        └── axionui-secreat.yaml

```

---

# 3. Docker Concept

Dockerfile application ko package karta hai.

Basic flow:

```text
Source Code
    |
    v
Dockerfile
    |
    v
docker build
    |
    v
Docker Image
    |
    v
docker push
    |
    v
ACR

```

Example:

```powershell
docker build -t axionui:z1 .

```

Check image:

```powershell
docker images

```

---

# 4. Docker Image ko ACR mein Push Karna

Login:

```powershell
az login

```

ACR login:

```powershell
az acr login --name sudarshan2026

```

Tag image:

```powershell
docker tag axionui:z1 sudarshan2026.azurecr.io/axionui:z1

```

Push:

```powershell
docker push sudarshan2026.azurecr.io/axionui:z1

```

Check ACR:

```powershell
az acr repository list --name sudarshan2026 --output table

```

Specific image:

```powershell
az acr repository show-tags \
  --name sudarshan2026 \
  --repository axionui \
  --output table

```

---

# 5. Kubernetes Secret

Secret ka purpose:

Application configuration ko Deployment YAML se separate rakhna.

Example:

```yaml
apiVersion: v1
kind: Secret

metadata:
  name: axion-ui-secret

type: Opaque

stringData:
  VITE_API_BASE: "http://telemetry.sudsutar.site"

```

Apply:

```powershell
kubectl apply -f axionui-secreat.yaml

```

Check:

```powershell
kubectl get secret

```

Specific Secret:

```powershell
kubectl get secret axion-ui-secret

```

---

# 6. Secret ko Deployment mein Use Karna

Deployment ke container ke andar:

```yaml
env:
  - name: VITE_API_BASE
    valueFrom:
      secretKeyRef:
        name: axion-ui-secret
        key: VITE_API_BASE

```

Meaning:

```text
Kubernetes Secret
       |
       | VITE_API_BASE
       v
Deployment
       |
       v
Container Environment Variable

```

Important:

```text
Secret name:
axion-ui-secret

Secret key:
VITE_API_BASE

Container variable:
VITE_API_BASE

```

Teeno properly match hone chahiye.

---

# 7. Important Vite Concept

React + Vite application mein:

```js
const API_BASE = import.meta.env.VITE_API_BASE;

```

syntax correct hai.

But:

```text
Vite environment variables
        |
        v
npm run build
        |
        v
JavaScript bundle

```

Vite generally `VITE_*` values ko **build time** par bundle mein inject karta hai.

Therefore:

```yaml
env:
  - name: VITE_API_BASE

```

Kubernetes Pod mein add karna automatically already-built React JavaScript ko change nahi karta.

For runtime configuration, separate runtime config approach use karna padta hai.

For simple lab:

```text
VITE_API_BASE
      |
      v
Docker build time
      |
      v
npm run build
      |
      v
React bundle

```

---

# 8. Kubernetes Deployment

Example:

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: axion-ui

spec:
  replicas: 3

  selector:
    matchLabels:
      app: axion-ui

  template:
    metadata:
      labels:
        app: axion-ui

    spec:
      containers:
        - name: axion-ui

          image: sudarshan2026.azurecr.io/axionui:z3

          ports:
            - containerPort: 80

          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"

            limits:
              cpu: "500m"
              memory: "512Mi"

          env:
            - name: VITE_API_BASE
              valueFrom:
                secretKeyRef:
                  name: axion-ui-secret
                  key: VITE_API_BASE

```

Apply:

```powershell
kubectl apply -f axionui.yaml

```

Check Deployment:

```powershell
kubectl get deployment

```

Check Pods:

```powershell
kubectl get pods

```

---

# 9. Kubernetes Service

Deployment Pods ko directly internet par expose nahi karte.

Flow:

```text
Pod
 |
 v
Service
 |
 v
Ingress
 |
 v
Application Gateway
 |
 v
Internet

```

Example:

```yaml
apiVersion: v1
kind: Service

metadata:
  name: axionui-service-pod

spec:
  selector:
    app: axion-ui

  ports:
    - port: 80
      targetPort: 80

  type: ClusterIP

```

Check:

```powershell
kubectl get svc

```

---

# 10. Check Service Endpoints

Very important troubleshooting command:

```powershell
kubectl get endpoints axionui-service-pod

```

Expected:

```text
axionui-service-pod
10.244.x.x:80
10.244.x.x:80
10.244.x.x:80

```

Meaning:

```text
Service
   |
   +---- Pod 1
   |
   +---- Pod 2
   |
   +---- Pod 3

```

If endpoint is empty:

```text
ENDPOINTS <none>

```

then Service selector and Pod labels check karo.

---

# 11. HPA

HPA = Horizontal Pod Autoscaler.

Example:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler

metadata:
  name: axion-ui-hsa

spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: axion-ui

  minReplicas: 1
  maxReplicas: 3

  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70

```

Check:

```powershell
kubectl get hpa

```

---

# 12. Ingress / Application Gateway

Host-based routing:

```text
axionui.sudsutar.site
        |
        v
Application Gateway
        |
        v
axion-ui-service-pod
        |
        v
Axion UI Pods

```

Telemetry:

```text
telemetry.sudsutar.site
        |
        v
Application Gateway
        |
        v
telemetry-service-pod
        |
        v
Telemetry Pods

```

Ingestion:

```text
ingestion.sudsutar.site
        |
        v
Application Gateway
        |
        v
ingestion-service-pod
        |
        v
Ingestion Pods

```

---

# 13. Important Troubleshooting Flow

## Step 1 — Check Pods

```powershell
kubectl get pods

```

Pods should be:

```text
Running

```

and preferably:

```text
1/1

```

---

## Step 2 — Check Services

```powershell
kubectl get svc

```

---

## Step 3 — Check Endpoints

```powershell
kubectl get endpoints axionui-service-pod
kubectl get endpoints telemetry-service-pod
kubectl get endpoints ingestion-service-pod

```

---

## Step 4 — Check Ingress

```powershell
kubectl get ingress

```

Expected Application Gateway IP:

```text
4.247.243.171

```

---

## Step 5 — Test Telemetry API

```powershell
curl.exe -v --resolve telemetry.sudsutar.site:80:4.247.243.171 http://telemetry.sudsutar.site/devices

```

Expected:

```text
HTTP/1.1 200 OK
Content-Type: application/json

```

and JSON device data.

---

# 14. Test Specific Device API

Example:

```powershell
curl.exe -v --resolve telemetry.sudsutar.site:80:4.247.243.171 http://telemetry.sudsutar.site/devices/AX-CMP-E01-C4A6/latest

```

This checks:

```text
Browser/API Client
       |
       v
Application Gateway
       |
       v
Telemetry Ingress
       |
       v
Telemetry Service
       |
       v
Telemetry Pod
       |
       v
PostgreSQL

```

---

# 15. Browser Troubleshooting

If UI opens but data doesn't load:

```text
F12
 |
 +--- Console
 |
 +--- Network
       |
       +--- Fetch/XHR

```

Check requests:

```text
devices
summary
throughput
regions
top-anomalous

```

Check:

```text
Status
Request URL
Response

```

Expected:

```text
200
JSON response

```

If error:

```text
Unexpected token '<'

```

it usually means frontend expected JSON but received HTML.

For example:

```text
Expected:
{ ...JSON... }

Received:
<!doctype html>

```

---

# 16. Git Initialization

Go to project:

```powershell
cd "F:\DevOpsInsiders\kubernet\kubernet Example\AxionProject_HSA_Dockar_Secreat"

```

Initialize Git:

```powershell
git init

```

If you see:

```text
Reinitialized existing Git repository

```

it means Git repository already exists.

No problem.

---

# 17. Check Git Status

```powershell
git status

```

This shows:

```text
modified files
untracked files
staged files
branch
remote

```

---

# 18. Check Git Remote

```powershell
git remote -v

```

For this project:

```text
origin
https://github.com/sudarshansutar1995/AxionProject_HSA_Dockar_Secreat.git

```

If wrong remote exists:

```powershell
git remote set-url origin https://github.com/sudarshansutar1995/AxionProject_HSA_Dockar_Secreat.git

```

Verify:

```powershell
git remote -v

```

---

# 19. Add Files

```powershell
git add .

```

Check:

```powershell
git status

```

Now files should appear under:

```text
Changes to be committed

```

---

# 20. Commit

```powershell
git commit -m "Add HSA Docker and Kubernetes configuration"

```

Example successful output:

```text
[main 6db56af] Add HSA Docker and Kubernetes configuration

```

---

# 21. Push to GitHub

First time:

```powershell
git push -u origin main

```

After that:

```powershell
git push

```

because `main` is already tracking `origin/main`.

---

# 22. Complete Git Flow

Every time code changes:

```text
Change code
    |
    v
git status
    |
    v
git add .
    |
    v
git status
    |
    v
git commit -m "message"
    |
    v
git push
    |
    v
GitHub

```

Commands:

```powershell
git status

git add .

git status

git commit -m "Update application"

git push

```

---

# 23. Complete Docker → ACR → AKS Flow

```text
1. Change Application Code
             |
             v
2. Dockerfile
             |
             v
3. docker build
             |
             v
4. Docker Image
             |
             v
5. docker tag
             |
             v
6. docker push
             |
             v
7. Azure Container Registry
             |
             v
8. Update Kubernetes Deployment
             |
             v
9. kubectl apply
             |
             v
10. Kubernetes creates new Pods
             |
             v
11. Service
             |
             v
12. Ingress
             |
             v
13. Application Gateway
             |
             v
14. Browser

```

---

# 24. Complete Git + Docker + Kubernetes Flow

```text
Developer
   |
   | Code change
   v
Git Local Repository
   |
   | git commit
   v
GitHub
   |
   | Docker build
   v
Docker Image
   |
   | docker push
   v
Azure Container Registry
   |
   | Kubernetes Deployment
   v
AKS
   |
   +-------------------+
   |                   |
   v                   v
Secret              Deployment
                       |
                       v
                      Pods
                       |
                       v
                    Service
                       |
                       v
                    Ingress
                       |
                       v
              Application Gateway
                       |
                       v
                    Browser

```

---

# 25. Daily Commands Cheat Sheet

### Git

```powershell
git status
git add .
git commit -m "message"
git push

```

### Docker

```powershell
docker build -t axionui:z1 .
docker images
docker tag axionui:z1 sudarshan2026.azurecr.io/axionui:z1
docker push sudarshan2026.azurecr.io/axionui:z1

```

### ACR

```powershell
az acr login --name sudarshan2026

az acr repository list --name sudarshan2026 --output table

az acr repository show-tags --name sudarshan2026 --repository axionui --output table

```

### Kubernetes

```powershell
kubectl get pods
kubectl get svc
kubectl get ingress
kubectl get endpoints
kubectl get secret
kubectl get hpa

```

Apply:

```powershell
kubectl apply -f filename.yaml

```

Restart Deployment:

```powershell
kubectl rollout restart deployment axion-ui

```

Check rollout:

```powershell
kubectl rollout status deployment axion-ui

```

Logs:

```powershell
kubectl logs deployment/axion-ui

```

---

# 26. Most Important Things to Remember

### Git

```text
git add
   ↓
git commit
   ↓
git push

```

### Docker

```text
Dockerfile
   ↓
docker build
   ↓
Image

```

### ACR

```text
docker tag
   ↓
docker push
   ↓
ACR

```

### Kubernetes

```text
Deployment
   ↓
Pods
   ↓
Service
   ↓
Ingress
   ↓
Application Gateway

```

### Secret

```text
Secret
   ↓
Deployment env
   ↓
Container

```

But for **Vite** **`VITE_*`** **variables**, remember:

```text
Vite
   ↓
npm run build
   ↓
Environment value gets bundled

```

So Kubernetes runtime environment injection does not automatically modify an already-built Vite bundle.

---

# 27. Security Reminder

Never push actual credentials to GitHub.

Avoid committing:

```text
DB passwords
API keys
Access tokens
Service Principal passwords
ACR passwords
Private keys

```

For real projects, use:

```text
Azure Key Vault
Kubernetes Secrets
External Secrets
GitHub/Azure DevOps secret variables

```

Also, if a real credential has already been pushed to GitHub, **rotate/revoke it** rather than relying on deleting it from the latest commit.