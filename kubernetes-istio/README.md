# Service Mesh en Kubernetes con Istio

## Pasos previos

```bash
#Instalar docker (si se requiere)
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker

#Instalar kubectl
sudo apt install -y apt-transport-https ca-certificates curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo snap install kubectl --classic
kubectl version --client

#Instalar minikube (chequear si la arquitectura es arm o amd)
dpkg --print-architecture
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube version

# Arrancar minikube con docker driver
minikube start --driver=docker
# If you encounter root privileges error, run:
minikube start --driver=docker --force
minikube status
kubectl cluster-info
kubectl config view
kubectl get nodes
kubectl get pods
minikube dashboard

#Prune system en caso de errores de re-arranque
minikube delete --all --purge
docker system prune

```

## 1. Instalación de Istio en Kubernetes

```bash
# Descargar Istio
curl -L https://istio.io/downloadIstio | sh -

# Moverse al directorio de Istio
cd istio-1.x.x

# Añadir istioctl al PATH
export PATH=$PWD/bin:$PATH

# Instalar Istio con perfil demo
istioctl install --set profile=demo -y

#Chequear el deployment
kubectl -n istio-system get deploy

# Habilitar inyección automática de sidecar en el namespace default
kubectl label namespace default istio-injection=enabled
```

## 2. Despliegue de una Aplicación de Ejemplo (Microservicios)

```yaml
# frontend.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          limits:
            memory: "128Mi"
            cpu: "200m"
          requests:
            memory: "64Mi"
            cpu: "100m"
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

```yaml
# backend.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: kennethreitz/httpbin  # API de prueba que responde con eco
        ports:
        - containerPort: 80
        resources:
          limits:
            memory: "128Mi"
            cpu: "200m"
          requests:
            memory: "64Mi"
            cpu: "100m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP

# ingress.yml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demo-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$1
spec:
  rules:
  - host: demo.local
    http:
      paths:
      - path: /(.*)
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      - path: /api/(.*)
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
```

## 3. Configuración de Reglas de Tráfico con Istio

```yaml
# virtual-service.yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: frontend-vs
spec:
  hosts:
  - frontend
  http:
  - route:
    - destination:
        host: frontend
        subset: v1
      weight: 90
    - destination:
        host: frontend
        subset: v2
      weight: 10
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: frontend-dr
spec:
  host: frontend
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
  trafficPolicy:
    loadBalancer:
      simple: ROUND_ROBIN
```

## 4. Configuración de Circuit Breaker

```yaml
# circuit-breaker.yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: backend-cb
spec:
  host: backend
  trafficPolicy:
    outlierDetection:
      consecutiveErrors: 3
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 100
```

## 5. Configuración de Políticas de Seguridad

```yaml
# security-policy.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
spec:
  mtls:
    mode: STRICT
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: frontend-policy
spec:
  selector:
    matchLabels:
      app: frontend
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/backend"]
    to:
    - operation:
        methods: ["GET"]
```

## 6. Configuración de Monitorización y Observabilidad

```yaml
# telemetry.yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: service-telemetry
spec:
  tracing:
    - randomSamplingPercentage: 100.0
  metrics:
    - providers:
      - name: prometheus
    - overrides:
      - match:
          metric: REQUEST_COUNT
        tagOverrides:
          response_code:
            operation: UPSERT
            value: "{{.Response.Code}}"
```

## 7. Ejemplo de Configuración de Gateway

```yaml
# gateway.yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: frontend-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: frontend-vs-gateway
spec:
  hosts:
  - "*"
  gateways:
  - frontend-gateway
  http:
  - route:
    - destination:
        host: frontend
        port:
          number: 80
```

## 8. Comandos para Verificación y Monitorización

```bash
#Aplicamos las configuraciones en orden
kubectl apply -f frontend.yml
kubectl apply -f backend.yml
kubectl apply -f ingress.yml
kubectl apply -f virtual-service.yml
kubectl apply -f circuit-breaker.yml
kubectl apply -f security-policy.yml
kubectl apply -f telemetry.yml
kubectl apply -f gateway.yml

#Aplicar todas las configuraciones a la vez
kubectl apply -f .

#Borrarlas para reinstalarlas de nuevo
kubectl delete -f .;kubectl apply -f .

# Habilitar minikube para poder trabajar con imágenes locales
eval $(minikube -p minikube docker-env)

# Verificar que todo está corriendo
kubectl get pods
kubectl get services
kubectl get ingress

# Terminal 1: Logs del frontend
kubectl logs -f deployment/frontend

# Terminal 2: Logs del backend
kubectl logs -f deployment/backend

# Escalar el frontend a 3 réplicas
kubectl scale deployment frontend --replicas=3

#Abrir un tunel al cluster de Kubernetes
minikube tunnel

#Obtener la IP de minikube
minikube ip

#Abrir un servicio
minikube service frontend

# Habilitar el addon de ingress si no está habilitado
minikube addons enable ingress

# Eliminar un pod y ver cómo se recrea
kubectl delete pod -l app=frontend

# Habilitar métricas en Minikube
minikube addons enable metrics-server

# Ver uso de recursos (necesario API de métricas)
kubectl top pods

# Verificar los servicios de Istio
kubectl get svc -n istio-system

# Ver las métricas de un servicio específico
istioctl dashboard metrics frontend

# Acceder al dashboard de Kiali
istioctl dashboard kiali

# Ver los logs de un pod específico
kubectl logs <pod-name> -c istio-proxy

# Verificar la configuración de Istio
istioctl analyze
```

## 9. Uso de Kompose

```bash
# 1. Instalar Kompose (Imprimimos arquitectura para saber cual hay que instalar)
dpkg --print-architecture
# Linux
curl -L https://github.com/kubernetes/kompose/releases/download/v1.34.0/kompose-linux-amd64 -o kompose
# Linux ARM64
curl -L https://github.com/kubernetes/kompose/releases/download/v1.34.0/kompose-linux-arm64 -o kompose
chmod +x kompose
sudo mv ./kompose /usr/local/bin/kompose

# 2. Uso de Kompose (Run kompose convert in the same directory as your compose.yaml file)
kompose convert
#Aplicar a kubernetes
kubectl apply -f .
```