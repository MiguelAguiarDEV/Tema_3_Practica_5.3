FROM openjdk:17-jdk-slim

ARG SPARK_VERSION=3.3.2
ARG HADOOP_VERSION=3

ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV SPARK_CLASSPATH=/opt/spark/jars/*

# Instalar dependencias necesarias y reemplazar paquetes obsoletos
RUN apt-get update && apt-get install -y \
    wget \
    procps \
    python3 \
    python3-pip \
    libmariadb-dev-compat \
    libmariadb-dev \
    && \
    wget -qO /tmp/spark.tgz https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xzf /tmp/spark.tgz -C /opt && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark && \
    rm /tmp/spark.tgz && \
    pip install pyspark==${SPARK_VERSION} && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install pandas pyspark mysql-connector-python matplotlib
RUN pip install delta-spark==2.2.0

# Copiar el conector JDBC
COPY mysql-connector-j-8.0.33.jar /opt/spark/jars/
COPY delta-core_2.12-2.2.0.jar /opt/spark/jars/
COPY mongo-spark-connector_2.12-3.0.1.jar /opt/spark/jars/
COPY bson-4.2.3.jar /opt/spark/jars/
COPY mongodb-driver-core-4.2.3.jar /opt/spark/jars/
COPY mongodb-driver-sync-4.2.3.jar /opt/spark/jars/
COPY delta-storage-2.2.0.jar /opt/spark/jars/

WORKDIR /opt/spark
EXPOSE 4040 8080 7077 6066

CMD ["spark-shell"]
