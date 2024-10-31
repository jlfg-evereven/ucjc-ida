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

#Si queremos entrar al contenedor de minikube
minikube ssh

#Prune system en caso de errores de re-arranque
minikube delete --all --purge
docker system prune

# Descargar Istio
curl -L https://istio.io/downloadIstio | sh -

# Moverse al directorio de Istio
cd istio-1.x.x

# Añadir istioctl al PATH
export PATH=$PWD/bin:$PATH

# Instalar Istio con perfil demo
istioctl install --set profile=demo -y

# Verificar
kubectl -n istio-system get deploy

# Habilitar inyección automática de sidecar en el namespace default
kubectl label namespace default istio-injection=enabled

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

# Ver uso de recursos
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

kubectl patch svc <svc-name> -n <namespace> -p '{"spec": {"type": "LoadBalancer", "externalIPs":["172.31.71.218"]}}'

#Abrir un tunel al cluster de Kubernetes
minikube tunnel

#Obtener la IP de minikube
minikube ip

#Abrir un servicio
minikube service frontend

# Habilitar el addon de ingress si no está habilitado
minikube addons enable ingress


curl --resolve "hello-world.example:80:$( minikube ip )" -i http://hello-world.example


#Limpiar el entorno
kubectl delete services frontend backend
kubectl delete deployment frontend backend

curl --resolve "mi-app.local:80:$( minikube ip )" -i http://hello-world.example


# Ver los logs del ingress controller
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# Ver el estado del ingress
kubectl describe ingress mi-aplicacion-ingress
