# Dockerfile base para Node.js
FROM node:16

# Crear directorio de la aplicación
WORKDIR /usr/src/app

# Archivo package.json para las dependencias
COPY package.json ./

# El archivo package.json necesario contendría:
#COPY package.json ./
#RUN echo '{\
#  "name": "oauth-authorization-server",\
#  "version": "1.0.0",\
#  "description": "OAuth 2.0 Authorization Server",\
#  "main": "app.js",\
#  "dependencies": {\
#    "express": "^4.17.1",\
#    "body-parser": "^1.19.0",\
#    "jade": "^1.11.0",\
#    "body-parser": "^1.19.0",\
#    "request": "^2.88.2"\
#  }\
#}' > package.json

# Instalar dependencias
RUN npm install

# Copiar código fuente
COPY . .

# Crear directorio de vistas y agregar plantillas necesarias
RUN mkdir -p views

# Crear plantilla index.jade
RUN echo 'html\n\
  head\n\
    title OAuth 2.0 Authorization Server\n\
  body\n\
    h1 OAuth 2.0 Authorization Server\n\
    p Welcome to the authorization server' > views/index.jade

# Crear plantilla authorization.jade
RUN echo 'html\n\
  head\n\
    title OAuth 2.0 Authorization\n\
  body\n\
    h1 Authorization Request\n\
    p Application #{application_name} is requesting access\n\
    form(method="post", action="/authorize")\n\
      input(type="hidden", name="client_id", value=client_id)\n\
      input(type="hidden", name="response_type", value=response_type)\n\
      input(type="hidden", name="scope", value=scope)\n\
      input(type="submit", value="Authorize")' > views/authorization.jade

# Variables de entorno por defecto
ENV NODE_ENV=production \
    PROVISION_KEY=spz9JC7FQvjZmqvSedxMWu6hq5icu0sV \
    SERVICE_HOST=jlfgucjc.org \
    KONG_ADMIN=http://host.docker.internal:8001 \
    KONG_API=https://host.docker.internal:8443 \
    API_PATH=/api/hola \
    SCOPES='{"email": "Grant permissions to read your email address","address": "Grant permissions to read your address information","phone": "Grantpermissionstoreadyourmobilephonenumber"}' \
    LISTEN_PORT=3000

# Exponer puerto
EXPOSE 3000

# Comando para ejecutar la aplicación
CMD ["node", "app.js"]