# Crear nuevo environment si no lo hemos creado
```bash
fission environment create --name pet-store-env \
    --image fission/python-env \
    --builder fission/python-builder \
    --version 3
```

# Dependencias del package
```bash
mkdir insert-product-pkg
cd insert-product-pkg
touch __init__.py
echo "psycopg2-binary==2.9.9" > requirements.txt
touch build.sh
chmod +x build.sh
```

# Crear y desplegar el package, funcion y ruta
```bash
zip -jr ins-prod-src-pkg.zip insert-product-pkg/
fission package create --sourcearchive ins-prod-src-pkg.zip --env pet-store-env --buildcmd "./build.sh" --name insert-product-pkg
fission pkg info --name insert-product-pkg
fission fn create --name insert-product --pkg insert-product-pkg --entrypoint "insert_product.main"
fission route create --method POST \
    --url /products \
    --function insert-product \
    --name insert-product-route
```


# Probar la función (usando la CLI de Fission)
```bash
fission function test --name insert-product --method POST \
    --body '{
        "name": "Collar LED",
        "description": "Collar luminoso para paseos nocturnos",
        "price": 24.99,
        "category": "Accesorios",
        "stock": 50
    }'
```

------------------------------------------------

# Check de los logs
```bash
fission pkg info --name insert-product-pkg
fission function logs --name insert-product

```

# Limpiar los pods
```bash
kubectl delete pods -n fission --all
```

# Limpiar el entorno
```bash
fission function delete --name insert-product
fission route delete --name insert-product-route
fission package delete --name insert-product-pkg
rm ins-prod-src-pkg.zip
```
