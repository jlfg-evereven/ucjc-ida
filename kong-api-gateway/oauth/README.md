# Configurando el entorno

Para hacer funcionar este proyecto, ejecuta los siguientes comandos.

* Añadimos el servicio de test de hola mundo:

```shell
curl -i -X POST http://localhost:8001/services \
  --data name=hola-service \
  --data url=http://host.docker.internal:5000
```
* Añadimos una ruta para nuestro servicio

```shell
curl -i -X POST http://localhost:8001/services/hola-service/routes \
  --data 'paths[]=/api/hola' \
  --data 'hosts[]=jlfgucjc.org' \
  --data name=hola-route
```
* Ahora probamos la nueva API

```shell
curl -X GET \
  --url "http://127.0.0.1:8000/api/hola" \
  --header "Host: jlfgucjc.org"
```

* Añadimos el OAuth 2.0 plugin, con 3 scopes:

```shell
curl -X POST \
  --url http://127.0.0.1:8001/services/hola-service/plugins/ \
  --data "name=oauth2" \
  --data "config.scopes=email, phone, address" \
  --data "config.mandatory_scope=true" \
  --data "config.enable_authorization_code=true"
```
Nos dará un ouput incluyendo una `provision_key` que usaremos más tarde:

```json
{
    "service_id": "2c0c8c84-cd7c-40b7-c0b8-41202e5ee50b",
    "value": {
        "scopes": [
            "email",
            "phone",
            "address"
        ],
        "mandatory_scope": true,
        "provision_key": "2ef290c575cc46eec61947aa9f1e67d3",
        "hide_credentials": false,
        "enable_authorization_code": true,
        "token_expiration": 7200
    },
    "created_at": 1435783325000,
    "enabled": true,
    "name": "oauth2",
    "id": "656954bd-2130-428f-c25c-8ec47227dafa"
}
```
La `provision_key` will be sent by the web application when communicating with Kong, to securely authenticate itself with Kong.

* Probamos la API de nuevo, para ver que está protegida:

```shell
curl -X GET \
  --url "http://127.0.0.1:8000/api/hola" \
  --header "Host: jlfgucjc.org"
```

Esto nos devolverá un error (generado por Kong), ya que faltan las credenciales de acceso.

* Creamos un Kong consumer (called `ucjc-consumer`):

```shell
curl -X POST \
  --url "http://127.0.0.1:8001/consumers/" \
  --data "username=ucjc-consumer" 
```
* Ahora un OAuth 2.0 client application llamado `Hello World App`:

```shell
curl -X POST \
  --url "http://127.0.0.1:8001/consumers/ucjc-consumer/oauth2/" \
  --data "name=Hello World App" \
  --data "redirect_uris[]=http://konghq.com/"
```

Nos devolverá la siguiente respuesta, incluyendo `client_id` y `client_secret` que usaremos más tarde:

```json
{
    "consumer_id": "a0977612-bd8c-4c6f-ccea-24743112847f",
    "client_id": "318f98be1453427bc2937fceab9811bd",
    "id": "7ce2f90c-3ec5-4d93-cd62-3d42eb6f9b64",
    "name": "Hello World App",
    "created_at": 1435783376000,
    "redirect_uri": "http://konghq.com/",
    "client_secret": "efbc9e1f2bcc4968c988ef5b839dd5a4"
}
```

# Lanzamos la aplicación web

```shell
docker build -t oauth-server .
docker run --add-host=host.docker.internal:host-gateway -p 3000:3000 oauth-server
``` 

En el navegador, ve a `http://localhost:3000/authorize?response_type=code&client_id=I2Ni67rw1LDLHecp9Urk2KpFO99BhaYP` para ver la página de autorización.

Para propósitos de prueba establecemos el `redirect_uri` a `http://konghq.com`, pero en producción esta será una URL que la aplicación cliente podrá leer para parsear el código e intercambiarlo con un token de acceso: `https://konghq.com/?code=pmIPlplKe7pGgXukhnPtvSQbn0eVfMWI`

# Conclusions

Ahora la aplicación cliente tiene un `code` que se puede utilizar más adelante para solicitar un `access_token`.

Para recuperar un `access_token` ahora puedes ejecutar la siguiente petición:


```shell
curl -X POST \
  --url "https://127.0.0.1:8443/api/hola/oauth2/token" \
  --header "Host: jlfgucjc.org" \
  --data "grant_type=authorization_code" \
  --data "client_id=I2Ni67rw1LDLHecp9Urk2KpFO99BhaYP" \
  --data "client_secret=3ok69JZYNqACL0yisQaTXkaCyV66THeG" \
  --data "redirect_uri=http://konghq.com/" \
  --data "code=pmIPlplKe7pGgXukhnPtvSQbn0eVfMWI" \
  --insecure
```

* Ahora probamos la API de nuevo y vemos el resultado
```shell
curl -X GET \
  --url "http://127.0.0.1:8000/api/hola" \
  --header "Host: jlfgucjc.org" \
  --header "Authorization: bearer fNVCymjb6uZH4D474lSQD93cPGe0k2UM"
```

Notese que en la respuesta que Kong inyecto un número extra de headers antes de enviar la petición al upstream service:

```json
    ...
    "x-consumer-id": "77e3f7ca-a969-48bb-a6d0-4a104ea7ad1e",
    "x-consumer-username": "ucjc-consumer",
    "x-authenticated-scope": "email address",
    ...
```