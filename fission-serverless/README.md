# Install fission

```bash
kubectl create -k "github.com/fission/fission/crds/v1?ref=v1.20.5"
export FISSION_NAMESPACE="fission"
kubectl create namespace $FISSION_NAMESPACE
kubectl config set-context --current --namespace=$FISSION_NAMESPACE
kubectl apply -f https://github.com/fission/fission/releases/download/v1.20.5/fission-all-v1.20.5-minikube.yaml
kubectl config set-context --current --namespace=default #to change context to default namespace after installation
```

# Install CLI
```bash
curl -Lo fission https://github.com/fission/fission/releases/download/v1.20.5/fission-v1.20.5-linux-amd64 \
    && chmod +x fission && sudo mv fission /usr/local/bin/
```

# Check installation
```bash
fission version
fission check
```

# Install function
```bash
# Crear el entorno Python
fission env create --name pet-store --image ghcr.io/fission/python-env

# Crear la función
fission function create --name get-product --env pet-store --code get_product.py

# Crear la ruta HTTP
fission route create --method GET --url /products --function get-product
```

# Test función

```bash
fission function test --name get-product
fission function test --name get-product --query id=1
minikube service -n fission router --url

#La url será algo así
http://<FISSION_ROUTER>:<PORT>/products
curl http://192.168.49.2:31314/products
curl http://192.168.49.2:31314/products?id=1
```

# Actualizar la función si hemos hecho un cambio
```bash
fission function update --name get-product --env pet-store --code get_product.py
```

# Comandos de interés
```bash
# Listar los entornos
fission environment list
# Listar los paquetes
fission package list
#Listar las rutas
fission route list
# Listar las funciones
fission function list
# Logs de una función específica
fission function logs --name get-product
# Obtener metadatos de una función 
fission function getmeta --name get-product
```