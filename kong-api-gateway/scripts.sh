#!/usr/bin/env bash

curl -i -X POST http://localhost:8001/services \
  --data name=hola-service \
  --data url=http://host.docker.internal:5000

curl -i -X POST http://localhost:8001/services/hola-service/routes \
  --data 'paths[]=/api/hola' \
  --data name=hola-route

#Para el servicio completo
curl -X POST http://localhost:8001/services/hola-service/plugins \
   --data "name=rate-limiting" \
   --data config.minute=5 \
   --data config.policy=local

#Para una ruta determinada
curl -X POST http://localhost:8001/routes/hola-route/plugins \
   --data "name=rate-limiting" \
   --data config.minute=5 \
   --data config.policy=local

###############################

## Crear nuestro JWT
curl -i -X POST http://localhost:8001/consumers \
  --data username=example-user

curl -i -X POST http://localhost:8001/consumers/example-user/jwt \
  --data algorithm=HS256 \
  --data key=my-perfect-key \
  --data secret=example-secret

TOKEN=$(curl -s http://localhost:8001/consumers/example-user/jwt/my-perfect-key)

# Crea una de ejemplo
curl -H "Content-Type: application/json" -X POST -d '{}' http://localhost:8001/consumers/example-user/jwt

# Para generar un bearer token (sin necesidad de implementar un cliente)
http://jwtbuilder.jamiekurtz.com/

#######################################

curl -i -X GET http://localhost:8000/api/hola \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJteS1wZXJmZWN0LWtleSIsImlhdCI6MTczMDE5ODk3MSwiZXhwIjoxNzYxNzM0OTcxLCJhdWQiOiJ3d3cuZXhhbXBsZS5jb20iLCJzdWIiOiJqcm9ja2V0QGV4YW1wbGUuY29tIiwiR2l2ZW5OYW1lIjoiSm9obm55IiwiU3VybmFtZSI6IlJvY2tldCIsIkVtYWlsIjoianJvY2tldEBleGFtcGxlLmNvbSIsIlJvbGUiOlsiTWFuYWdlciIsIlByb2plY3QgQWRtaW5pc3RyYXRvciJdfQ.b9os0Y70WO2sKbYhmNFyGs54lYOhGLgA2schUFGil3s"


# host.docker.internal

# NAME  TYPE    KONG ADMIN URL  KONG VERSION    CREATED         
# kong  basic_auth  http://host.docker.internal:8001    3.8.0


curl -X POST http://localhost:8001/services/hola-service/plugins \
  --data "name=basic-auth" \
  --data "config.hide_credentials=true"

# 3. Crear credenciales
curl -X POST http://localhost:8001/consumers/example-user/basic-auth \
  --data "username=example-user" \
  --data "password=supersecret"