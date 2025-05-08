# Dockerfile para MongoDB
FROM mongo:7.0

# Copia scripts de inicialización si existen
COPY docker-entrypoint-initdb.d/ /docker-entrypoint-initdb.d/

# Exponer el puerto por defecto de MongoDB
EXPOSE 27017
