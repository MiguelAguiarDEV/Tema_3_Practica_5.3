# Práctica 5.2: Análisis de Ventas y Consultas con Spark, MySQL y Hadoop

[Repositorio en GitHub](https://github.com/MiguelAguiarDEV/BIU_5.2)


Esta práctica integra Spark, MySQL y Hadoop usando Docker. Aquí tienes los pasos y comandos para cada apartado, adaptados a los ejercicios y scripts de esta práctica. Cada sección incluye una breve explicación y cómo ver los resultados.

---

## 1. Preparación del entorno Docker

### 1.1. Eliminar contenedores y red anteriores (opcional)
```sh
docker rm -f spark-master-custom hadoop-namenode mysql-moviebind mongo-ecommerce || true
docker network rm spark-network || true
```
_Elimina contenedores y red si existen, para evitar conflictos._

### 1.2. Crear la red Docker
```sh
docker network create spark-network
```
_Crea la red para que los contenedores se comuniquen._

### 1.3. Construir las imágenes personalizadas
```sh
docker build -t spark-custom:3.3.2 ./spark-docker
docker build -t hadoop-custom:3.3.2 ./hadoop-docker
docker build -t my-mysql ./mysql-docker
docker build -t mongo-ecommerce ./mongo-docker
```
_Compila las imágenes de Spark, Hadoop y MySQL._

### 1.4. Iniciar los contenedores (MySQL, Spark, Hadoop, MongoDB)
```sh
docker run -d --name mysql-moviebind --network spark-network -p 3306:3306 my-mysql

docker run -d --name spark-master-custom --network spark-network -p 8080:8080 -p 7077:7077 -v "$(pwd)/spark-docker:/opt/spark/data" spark-custom:3.3.2 tail -f /dev/null

docker run -d --name hadoop-namenode --network spark-network hadoop-custom:3.3.2 tail -f /dev/null

docker run -d --name mongo-ecommerce --network spark-network -p 27017:27017 mongo-ecommerce
```
_Lanza los contenedores y monta la carpeta de trabajo en Spark. Incluye MongoDB junto a los otros servicios para facilitar el arranque por bloques._

### 1.4.1. (Solo la primera vez) Formatear el NameNode de Hadoop
```sh
docker exec -it hadoop-namenode bash -c "/opt/hadoop/bin/hdfs namenode -format"
```
_Inicializa el sistema de archivos HDFS._

### 1.5. Iniciar servicios HDFS en Hadoop
```sh
docker exec -it hadoop-namenode bash
# Dentro del contenedor ejecuta:
export HDFS_NAMENODE_USER=root
export HDFS_DATANODE_USER=root
export HDFS_SECONDARYNAMENODE_USER=root
/opt/hadoop/sbin/hadoop-daemon.sh start namenode
/opt/hadoop/sbin/hadoop-daemon.sh start datanode
/opt/hadoop/sbin/hadoop-daemon.sh start secondarynamenode
exit
```
_Inicia los servicios de HDFS._

### 1.6. Instalar ping (opcional, para pruebas de red)
```sh
docker exec -it spark-master-custom bash -c "apt-get update && apt-get install -y iputils-ping"
```
_Permite usar ping dentro del contenedor._

---

## 2. Ejecución de scripts

### 2.1. Mostrar todas las tablas de MySQL como DataFrame
```sh
docker exec -it spark-master-custom spark-submit /opt/spark/data/table_data_frame.py
```
_Conecta a MySQL y muestra los datos de todas las tablas principales como DataFrame por consola._

---

## 7. Ejecución detallada de cada script de la tarea

### 7.1. movies_profile_dataframe.py
```sh
docker exec -it spark-master-custom spark-submit /opt/spark/data/movies_profile_dataframe.py
```

### 7.2. non_relational_db.py
```sh
docker exec -it spark-master-custom spark-submit /opt/spark/data/non_relational_db.py
```

### 7.3. delta_lake_1.py
```sh
docker exec -it spark-master-custom spark-submit /opt/spark/data/delta_lake_1.py
```

### 7.4. delta_lake_2.py 
```sh
docker exec -it spark-master-custom spark-submit /opt/spark/data/delta_lake_2.py
```
