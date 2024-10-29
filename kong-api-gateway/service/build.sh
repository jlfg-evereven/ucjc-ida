#!/usr/bin/env bash

#Limpio mis contenedores <none>
docker image prune -f
#Levanto el docker-compose
docker build -t hello-flask:latest .