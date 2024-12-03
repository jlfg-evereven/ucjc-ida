# Crear nuevo environment
```bash
fission environment create --name pet-store-env \
    --image fission/python-env \
    --builder fission/python-builder \
    --version 3
```

# Dependencias del package
```bash
mkdir get-product-pkg
cd get-product-pkg
touch __init__.py
echo "psycopg2-binary==2.9.9" > requirements.txt
touch build.sh
chmod +x build.sh
```

# Crear y desplegar el package, funcion y ruta
```bash
zip -jr get-prod-src-pkg.zip get-product-pkg/
fission package create --sourcearchive get-prod-src-pkg.zip --env pet-store-env --buildcmd "./build.sh" --name get-product-pkg
fission pkg info --name get-product-pkg
fission fn create --name get-product --pkg get-product-pkg --entrypoint "get_product.main"
fission route create --method GET \
    --url /products \
    --function get-product \
    --name get-product-route
```

# Probar la función (usando la CLI de Fission)
```bash
# Obtener todos los productos
fission function test --name get-product --method GET

# Obtener producto por ID
fission function test --name get-product --method GET --query id=1

# Obtener productos por categoría
fission function test --name get-product --method GET --query category=Accesorios

```


------------------------------------------------


# Check de los logs
```bash
fission pkg info --name get-product-pkg
fission function logs --name get-product
```

# Limpiar los pods
```bash
kubectl delete pods -n fission --all
```

# Limpiar el entorno
```bash
fission function delete --name get-product
fission route delete --name get-product-route
fission package delete --name get-product-pkg
rm get-prod-src-pkg.zip
```
