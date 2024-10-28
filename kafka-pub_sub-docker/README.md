# Implementación con Docker Compose y Docker Swarm

Los scripts son orientativos, se tienen que adaptar al stack de despliegue

## 0.1. Uso de docker compose
```bash
# 1. Crear y arrancar los contenedores
docker-compose up -d

# 2. Ver los logs
docker-compose logs -f

# 3. Verificar estado de los contenedores
docker-compose ps

# 4. Detener los contenedores
docker-compose down

# 5. Limpiar 
docker-compose down -v --rmi all --remove-orphans

# 6. Construir contenedores
docker-compose build

# 7. Reconstruir contenedores
docker-compose up -d --build

# 8. Levantar contenedores específicos
docker-compose up mycontainer
```

## 0.2. Creación de un topic
```bash
docker exec -it mi-kafka bash

# Creación de un topic
kafka-topics.sh --bootstrap-server localhost:9092 --create --topic pageview
>
kafka-topics.sh --list --bootstrap-server localhost:9092
> pageview
# Crear dos particiones a nuestro topic
kafka-topics.sh \
    --topic pageview \
    --alter \
    --partitions 2 \
    --bootstrap-server localhost:9092
```

## 1. Inicialización del Cluster

```bash
#Iniciar swarm
docker swarm init

# Inicializar Swarm en el nodo manager
docker swarm init --advertise-addr <IP-DEL-MANAGER>

# La salida te dará un comando para unir workers, similar a:
docker swarm join --token SWMTKN-1-xxxxxx <IP-DEL-MANAGER>:2377

# Ver nodos del cluster
docker node ls
```

## 2. Stack de Ejemplo (Aplicación Web + Base de Datos)

Uso del stack de docker compose para kafka actual


## 3. Despliegue del Stack

```bash
# Desplegar el stack
docker stack deploy -c docker-compose.yml myapp

# Verificar servicios
docker service ls

# Ver detalles de un servicio específico
docker service ps myapp_web

# Escalar un servicio
docker service scale myapp_web=5
```

## 4. Scripts de Gestión

```bash
# monitor.sh - Script para monitorizar el cluster
#!/bin/bash

echo "=== Estado del Cluster ==="
docker node ls

echo -e "\n=== Servicios Activos ==="
docker service ls

echo -e "\n=== Uso de Recursos ==="
docker stats --no-stream
```

```bash
# cleanup.sh - Script para limpieza
#!/bin/bash

echo "Eliminando stack..."
docker stack rm myapp

echo "Esperando a que los servicios se detengan..."
sleep 10

echo "Limpiando redes..."
docker network prune -f

echo "Limpiando volúmenes no utilizados..."
docker volume prune -f
```

## 5. Comandos Útiles para Gestión

```bash
# Listar todos los servicios
docker service ls

# Ver logs de un servicio
docker service logs myapp_web

# Actualizar una imagen de servicio
docker service update --image nginx:latest myapp_web

# Inspeccionar un servicio
docker service inspect myapp_web

# Ver estadísticas de uso
docker stats
```

## 6. Configuración de Rollback

```bash
# Configurar política de rollback
docker service update \
  --rollback-parallelism 1 \
  --rollback-delay 30s \
  --rollback-monitor 60s \
  myapp_web

# Realizar rollback manual
docker service rollback myapp_web
```

## 7. Ejemplo de Configuración de Secrets (si tenemos base de datos en el compose)

```bash
# Crear secrets
echo "mypassword" | docker secret create db_password -
echo "mycert" | docker secret create ssl_cert -

# Modificar el servicio para usar secrets
docker service update \
  --secret-add source=db_password,target=/run/secrets/db_password \
  myapp_db
```

## 8. Monitorización Básica

```bash
# Visualizer (ya incluido en el stack)
# Accesible en http://localhost:8080

# Prometheus & Grafana (configuración adicional)
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    deploy:
      placement:
        constraints:
          - node.role == manager

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    deploy:
      placement:
        constraints:
          - node.role == manager
```

## 9. Consideraciones de Seguridad

1. **Firewall**
```bash
# Abrir puertos necesarios
ufw allow 2377/tcp  # Comunicación del cluster
ufw allow 7946/tcp  # Comunicación entre nodos
ufw allow 4789/udp  # Overlay network
```

2. **TLS**
```bash
# Rotar certificados del cluster
docker swarm ca --rotate

# Forzar rotación de certificados de nodos
docker swarm update --cert-expiry 48h
```

## 10. Verificación y Troubleshooting

```bash
# Verificar estado del cluster
docker node inspect self --format '{{ .Status.State }}'

# Verificar redes
docker network ls --filter driver=overlay

# Verificar logs del sistema
journalctl -u docker.service

# Verificar conectividad entre servicios
docker run --rm --network myapp_frontend alpine ping api
```
