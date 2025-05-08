from pyspark.sql import SparkSession
from delta.tables import DeltaTable

# Inicializar SparkSession con soporte Delta Lake
spark = SparkSession.builder \
    .appName("DeltaLakeEcommerce") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# 1. Leer datos de MongoDB (simulación: crea DataFrames de ejemplo)
usuarios = spark.createDataFrame([
    {"_id": "1", "nombre": "Juan Pérez", "email": "juan@mail.com", "tipo": "cliente"},
    {"_id": "2", "nombre": "Tienda XYZ", "email": "xyz@shop.com", "tipo": "vendedor"},
    {"_id": "3", "nombre": "Admin", "email": "admin@admin.com", "tipo": "administrador"}
])

productos = spark.createDataFrame([
    {"_id": "p1", "nombre": "Laptop", "precio": 800, "stock": 10},
    {"_id": "p2", "nombre": "Auriculares", "precio": 50, "stock": 50}
])

# 2. Persistir los DataFrames en Delta Lake
usuarios.write.format("delta").mode("overwrite").save("/tmp/delta/usuarios")
productos.write.format("delta").mode("overwrite").save("/tmp/delta/productos")

# 3. Leer y modificar datos usando SQL
spark.sql("CREATE TABLE IF NOT EXISTS usuarios_delta USING DELTA LOCATION '/tmp/delta/usuarios'")
spark.sql("CREATE TABLE IF NOT EXISTS productos_delta USING DELTA LOCATION '/tmp/delta/productos'")

print("Usuarios antes de UPDATE (SQL):")
spark.sql("SELECT * FROM usuarios_delta").show()
spark.sql("UPDATE usuarios_delta SET nombre = 'Juan Actualizado' WHERE nombre = 'Juan Pérez'")
print("Usuarios después de UPDATE (SQL):")
spark.sql("SELECT * FROM usuarios_delta").show()

# 4. Leer y modificar datos usando la API de Delta Lake
usuarios_delta = DeltaTable.forPath(spark, "/tmp/delta/usuarios")
print("Usuarios antes de UPDATE (API):")
usuarios_delta.toDF().show()
usuarios_delta.update(
    condition="nombre = 'Juan Actualizado'",
    set={"nombre": "'Juan Modificado API'"}
)
print("Usuarios después de UPDATE (API):")
usuarios_delta.toDF().show()

# 5. Consulta sobre una snapshot (Time Travel)
print("Historial de versiones de usuarios:")
usuarios_delta.history().show()
df_v0 = spark.read.format("delta").option("versionAsOf", 0).load("/tmp/delta/usuarios")
print("Usuarios en la versión 0 (Time Travel):")
df_v0.show()

# 6. Crear una tabla Delta con datos de bing_covid-19_data.parquet
covid_df = spark.read.parquet("/opt/spark/data/bing_covid-19_data.parquet")
covid_df.write.format("delta").mode("overwrite").save("/tmp/delta/covid")
spark.sql("CREATE TABLE IF NOT EXISTS covid_delta USING DELTA LOCATION '/tmp/delta/covid'")
print("Datos de covid_delta:")
spark.sql("SELECT * FROM covid_delta").show(5)

spark.stop()
