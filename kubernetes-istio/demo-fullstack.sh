#!/bin/bash
# setup-demo.sh

echo "🚀 Iniciando demo de Kubernetes..."

# Verificar que Minikube está instalado
if ! command -v minikube &> /dev/null; then
    echo "❌ Minikube no está instalado. Por favor, instálalo primero."
    exit 1
fi

# Iniciar Minikube
# echo "📦 Iniciando Minikube..."
# minikube start

# Habilitar Ingress
echo "🔧 Habilitando Ingress Controller..."
minikube addons enable ingress

# Aplicar configuraciones
echo "📄 Aplicando configuraciones..."
kubectl apply -f frontend.yml
kubectl apply -f backend.yml
kubectl apply -f ingress.yml

# Esperar a que los pods estén listos
echo "⏳ Esperando a que los pods estén listos..."
kubectl wait --for=condition=ready pod -l app=frontend --timeout=120s
kubectl wait --for=condition=ready pod -l app=backend --timeout=120s

# Configurar /etc/hosts
echo "🔧 Configurando acceso local..."
echo "$(minikube ip) demo.local" | sudo tee -a /etc/hosts

echo "✅ Demo lista!"
echo "📝 Puedes acceder a:"
echo "   Frontend: http://demo.local"
echo "   Backend: http://demo.local/api/get"

# Mostrar pods en ejecución
echo "\n📊 Pods en ejecución:"
kubectl get pods

echo "\n💡 Para ver los logs del frontend: kubectl logs -f deployment/frontend"
echo "💡 Para ver los logs del backend: kubectl logs -f deployment/backend"