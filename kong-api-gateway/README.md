# Implementación de Kong API Gateway

DISCLAIMER: Los siguientes scripts son generalistas, por tanto necesitan adaptarse para que tengan validez en un proposito determinado. En el fichero scripts.sh he dejado los que ejecuto para mostrar ejemplos. Esta misma información también se puede encontrar en los apuntes.

## 1. Docker Compose para Kong y sus dependencias

```yaml
# docker-compose.yml
version: '3.7'

services:
  kong-database:
    image: postgres:13
    environment:
      POSTGRES_USER: kong
      POSTGRES_DB: kong
      POSTGRES_PASSWORD: kongpass
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "kong"]
      interval: 5s
      timeout: 5s
      retries: 5

  kong-migration:
    image: kong:latest
    command: kong migrations bootstrap
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kongpass
    depends_on:
      - kong-database

  kong:
    image: kong:latest
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kongpass
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: 0.0.0.0:8001
    depends_on:
      - kong-migration
    ports:
      - "8000:8000"  # Proxy
      - "8001:8001"  # Admin API
      - "8443:8443"  # Proxy SSL
      - "8444:8444"  # Admin API SSL

  konga:
    image: pantsel/konga:latest
    environment:
      DB_ADAPTER: postgres
      DB_HOST: kong-database
      DB_USER: kong
      DB_PASSWORD: kongpass
      DB_DATABASE: kong
    depends_on:
      - kong
    ports:
      - "1337:1337"
```

RUN
```bash
docker compose up -d
```

kong  basic_auth  url_loopback=http://host.docker.internal:8001 

## 2. Configuración de Servicios y Rutas usando la API Admin de Kong

```bash
# 1. Crear un servicio para la API de usuarios
curl -i -X POST http://localhost:8001/services \
  --data name=user-service \
  --data url=http://user-service:8080

# 2. Crear una ruta para el servicio de usuarios
curl -i -X POST http://localhost:8001/services/user-service/routes \
  --data 'paths[]=/api/users' \
  --data name=user-route

# 3. Crear un servicio para la API de productos
curl -i -X POST http://localhost:8001/services \
  --data name=product-service \
  --data url=http://product-service:8081

# 4. Crear una ruta para el servicio de productos
curl -i -X POST http://localhost:8001/services/product-service/routes \
  --data 'paths[]=/api/products' \
  --data name=product-route
```

## 3. Configuración de Plugins

```bash
# 1. Configurar Rate Limiting
curl -i -X POST http://localhost:8001/plugins \
  --data name=rate-limiting \
  --data config.minute=100 \
  --data config.policy=local

# 2. Configurar Autenticación JWT
curl -i -X POST http://localhost:8001/plugins \
  --data name=jwt \
  --data config.secret_key=your-secret-key

# 3. Configurar CORS
curl -i -X POST http://localhost:8001/plugins \
  --data name=cors \
  --data config.origins=* \
  --data config.methods=GET,POST,PUT,DELETE \
  --data config.headers=Content-Type,Authorization

# 4. Configurar Request Transformation
curl -i -X POST http://localhost:8001/plugins \
  --data name=request-transformer \
  --data config.add.headers[]=x-customer-id:$(client_id)
```

## 4. Ejemplo de Configuración de Consumidor y Credenciales

```bash
# 1. Crear un consumidor
curl -i -X POST http://localhost:8001/consumers \
  --data username=example-user

# 2. Crear credenciales JWT para el consumidor
curl -i -X POST http://localhost:8001/consumers/example-user/jwt \
  --data algorithm=HS256 \
  --data key=my-wonderful-key \
  --data secret=example-secret

# 3. Crea una de ejemplo
curl -H "Content-Type: application/json" -X POST -d '{}' http://localhost:8001/consumers/example-user/jwt

# 4. Para generar un bearer token
http://jwtbuilder.jamiekurtz.com/
```

## 5. Ejemplo de Uso del API Gateway

```bash
# 1. Obtener un token JWT
TOKEN=$(curl -s http://localhost:8001/consumers/example-user/jwt/my-wonderful-key)

# 2. Hacer una solicitud al API Gateway
curl -i -X GET http://localhost:8000/api/users \
  -H "Authorization: Bearer $TOKEN"

# 3. Solicitud al servicio de productos
curl -i -X GET http://localhost:8000/api/products \
  -H "Authorization: Bearer $TOKEN"
```

## 6. Configuración de Monitorización

```bash
# Ver plugins activos
curl -s http://localhost:8001/plugins | jq

# Ver consumidores
curl -s http://localhost:8001/consumers | jq

# Configuración de Prometheus plugin
curl -i -X POST http://localhost:8001/plugins  \
  --data name=prometheus

# Configuración de File Log plugin
curl -i -X POST http://localhost:8001/plugins \
  --data name=file-log \
  --data config.path=/usr/local/kong/logs/access.log
```

## 7. Ejemplo de Política de Seguridad

```bash
# Configurar IP Restriction
curl -i -X POST http://localhost:8001/routes/hola-route/plugins \
  --data name=ip-restriction \
  --data config.allow=["10.10.10.0/24"]

# Configurar ACL
curl -i -X POST http://localhost:8001/routes/hola-route/plugins \
  --data name=acl \
  --data config.allow=["admin", "service-a"]
```

## 8. Ejemplo de Response Transformation

```bash
curl -i -X POST http://localhost:8001/plugins \
  --data name=response-transformer \
  --data config.add.headers[]=x-response-time \
  --data config.add.json.timestamp=$(date) \
  --data config.remove.json=internal_id
```

## 9. Crear una aplicación OAuth2
```bash
curl -X POST http://localhost:8001/consumers/consumer1/oauth2 \
  --data "name=My Application" \
  --data "client_id=CLIENTE-ID" \
  --data "client_secret=CLIENTE-SECRET" \
  --data "redirect_uri=http://example.com/callback"

# Obtener token (Client Credentials Grant)
curl -X POST https://localhost:8443/oauth2/token \
  --data "grant_type=client_credentials" \
  --data "client_id=CLIENTE-ID" \
  --data "client_secret=CLIENTE-SECRET" \
  --data "scope=email"
```