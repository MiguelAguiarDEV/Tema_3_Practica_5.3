from pyspark.sql import SparkSession

# Crear sesión de Spark sin intentar descargar paquetes
spark = SparkSession.builder \
    .appName("MongoToSpark") \
    .config("spark.mongodb.input.uri", "mongodb://mongo-ecommerce:27017/ecommerce.clientes") \
    .config("spark.mongodb.output.uri", "mongodb://mongo-ecommerce:27017/ecommerce.clientes") \
    .getOrCreate()

# Reducir verbosidad de logs
spark.sparkContext.setLogLevel("ERROR")

# Leer desde MongoDB - especificando la colección explícitamente
df = spark.read.format("com.mongodb.spark.sql.DefaultSource") \
    .option("database", "ecommerce") \
    .option("collection", "clientes") \
    .load()

# Mostrar los datos
print("Contenido de la colección 'clientes' en MongoDB leído desde Spark:")
df.show(truncate=False)

def show_and_count(tabla):
    df = spark.read.format("mongo") \
        .option("uri", f"mongodb://mongo-ecommerce:27017/ecommerce.{tabla}") \
        .load()
    print(f"\nColección: {tabla}")
    df.show()
    df.printSchema()
    print(f"Total de documentos en {tabla}: {df.count()}")
    return df

spark.stop()