from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit, col, split, to_timestamp, month, year, sum as _sum, trim
from delta.tables import DeltaTable

# Crear sesión Spark
spark = SparkSession.builder \
    .appName("DeltaLakeMedallionFull") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# --- BRONZE ---
ventas_df = spark.read.option("header", True).csv("/opt/spark/data/salesdata/*.csv")
ventas_df = ventas_df.toDF(*[c.replace(" ", "_").replace("-", "_") for c in ventas_df.columns])
ventas_df = ventas_df.withColumn("ingestion_time", current_timestamp()) \
                     .withColumn("source_system", lit("carga inicial CSV"))
ventas_df.write.format("delta").mode("overwrite").save("hdfs://hadoop-namenode:9000/delta/bronze/sales/")
print("Capa Bronze creada exitosamente.")
spark.read.format("delta").load("hdfs://hadoop-namenode:9000/delta/bronze/sales/").show(5, truncate=False)

# --- SILVER ---
ventas_clean_df = ventas_df.dropna()
ventas_clean_df = ventas_clean_df.filter(col("Product") != "Product")
split_col = split(col("Purchase_Address"), ", ")
ventas_clean_df = ventas_clean_df.withColumn("City", trim(split_col.getItem(1)))
ventas_clean_df = ventas_clean_df.withColumn("State", split(split_col.getItem(2), " ").getItem(0))
ventas_clean_df = ventas_clean_df.withColumn("Order_Date", to_timestamp(col("Order_Date"), "MM/dd/yy HH:mm"))
ventas_clean_df = ventas_clean_df.withColumn("Month", month(col("Order_Date")))
ventas_clean_df = ventas_clean_df.withColumn("Year", year(col("Order_Date")))
ventas_clean_df.write.format("delta").mode("overwrite").partitionBy("Year").save("hdfs://hadoop-namenode:9000/delta/silver/sales/")
print("Capa Silver creada exitosamente.")
spark.read.format("delta").load("hdfs://hadoop-namenode:9000/delta/silver/sales/").show(5, truncate=False)

# --- GOLD ---
ventas_2019 = ventas_clean_df.filter(col("Year") == 2019) \
    .groupBy("Month") \
    .agg(_sum(col("Quantity_Ordered") * col("Price_Each")).alias("Total_Recaudado")) \
    .orderBy("Month")
ventas_2019.write.format("delta").mode("overwrite").save("hdfs://hadoop-namenode:9000/delta/gold/sales/ventas2019")
ventas_2019.write.format("delta").mode("overwrite").saveAsTable("ventas2019_delta")
top10_ciudades = ventas_clean_df.groupBy("City") \
    .agg(_sum("Quantity_Ordered").alias("Total_Ventas")) \
    .orderBy(col("Total_Ventas").desc()) \
    .limit(10)
top10_ciudades.write.format("delta").mode("overwrite").save("hdfs://hadoop-namenode:9000/delta/gold/sales/top10ciudades")
top10_ciudades.write.format("delta").mode("overwrite").saveAsTable("top10ciudades_delta")
print("Contenido de Ventas 2019:")
spark.read.format("delta").load("hdfs://hadoop-namenode:9000/delta/gold/sales/ventas2019/").show(truncate=False)
print("Contenido de Top 10 ciudades:")
spark.read.format("delta").load("hdfs://hadoop-namenode:9000/delta/gold/sales/top10ciudades/").show(truncate=False)

# --- AUDITORÍA: Añadir ventas ficticias y propagar ---
data_nueva = [
    ("999991", "Wireless Mouse", 2, 25.99, "2019-07-15 12:00:00", "123 Liberty St, New York City, NY 10001"),
    ("999992", "Mechanical Keyboard", 1, 79.99, "2019-11-22 18:30:00", "500 Main St, San Francisco, CA 94016"),
    ("999993", "USB-C Hub", 3, 45.00, "2019-03-05 09:45:00", "77 5th Ave, Los Angeles, CA 90001"),
]
columns = ["Order_ID", "Product", "Quantity_Ordered", "Price_Each", "Order_Date", "Purchase_Address"]
nuevas_ventas_df = spark.createDataFrame(data_nueva, schema=columns) \
    .withColumn("ingestion_time", current_timestamp()) \
    .withColumn("source_system", lit("libro oculto 2019"))
tabla_bronze = DeltaTable.forPath(spark, "hdfs://hadoop-namenode:9000/delta/bronze/sales/")
tabla_bronze.alias("bronze").merge(
    nuevas_ventas_df.alias("nuevas"),
    "bronze.Order_ID = nuevas.Order_ID"
).whenNotMatchedInsertAll().execute()
print("✅ Nuevas ventas ficticias insertadas correctamente en Bronze.")
bronze_df = spark.read.format("delta").load("hdfs://hadoop-namenode:9000/delta/bronze/sales/")
bronze_df.filter(col("Order_ID").isin("999991", "999992", "999993")).show(truncate=False)
# Actualizar Silver
gold_bronze_df = spark.read.format("delta").load("hdfs://hadoop-namenode:9000/delta/bronze/sales/")
silver_nuevas = gold_bronze_df.filter(col("source_system") == "libro oculto 2019") \
    .withColumn("City", trim(split(col("Purchase_Address"), ",").getItem(1))) \
    .withColumn("State", split(split(col("Purchase_Address"), ",").getItem(2), " ").getItem(1)) \
    .withColumn("Order_Date", to_timestamp("Order_Date", "yyyy-MM-dd HH:mm:ss")) \
    .withColumn("Month", month("Order_Date")) \
    .withColumn("Year", year("Order_Date"))
silver_df = spark.read.format("delta").load("hdfs://hadoop-namenode:9000/delta/silver/sales/")
silver_actualizado = silver_df.unionByName(silver_nuevas)
silver_actualizado.write.format("delta").mode("overwrite").partitionBy("Year").save("hdfs://hadoop-namenode:9000/delta/silver/sales/")
# Actualizar Gold
ventas_2019 = silver_actualizado.filter(col("Year") == 2019) \
    .groupBy("Month") \
    .agg(_sum(col("Quantity_Ordered") * col("Price_Each")).alias("Total_Recaudado")) \
    .orderBy("Month")
ventas_2019.write.format("delta").mode("overwrite").save("hdfs://hadoop-namenode:9000/delta/gold/sales/ventas2019")
top10_ciudades = silver_actualizado.groupBy("City") \
    .agg(_sum("Quantity_Ordered").alias("Total_Ventas")) \
    .orderBy(col("Total_Ventas").desc()) \
    .limit(10)
top10_ciudades.write.format("delta").mode("overwrite").save("hdfs://hadoop-namenode:9000/delta/gold/sales/top10ciudades")
# --- TIME TRAVEL: Histórico y comparación ---
print("\n✅ Recuperando la versión inicial (versión 0) de ventas2019...")
ventas2019_v0 = spark.read.format("delta") \
    .option("versionAsOf", 0) \
    .load("hdfs://hadoop-namenode:9000/delta/gold/sales/ventas2019")
print("\n✅ Contenido de ventas2019 en la versión 0 (antes de la auditoría):")
ventas2019_v0.orderBy("Month").show(truncate=False)
print("\n✅ Contenido actual de ventas2019 (después de la auditoría):")
ventas_2019.orderBy("Month").show(truncate=False)
print("\n✅ Histórico de versiones de ventas2019:")
spark.sql("DESCRIBE HISTORY delta.`hdfs://hadoop-namenode:9000/delta/gold/sales/ventas2019`").show(truncate=False)
spark.stop()
