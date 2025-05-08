from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder \
        .appName("MovieProfileJoin") \
        .getOrCreate()  # Eliminada la configuración explícita de spark.jars

    # Propiedades de conexión JDBC
    jdbc_url = "jdbc:mysql://mysql-moviebind:3306/moviebind"  # Hostname cambiado a mysql-moviebind
    connection_properties = {
        "user": "user",
        "password": "1234",
        "driver": "com.mysql.cj.jdbc.Driver"
    }

    # Cargar la tabla 'users'
    users_df = spark.read.jdbc(url=jdbc_url,
                               table="users",
                               properties=connection_properties)

    # Cargar la tabla 'profiles'
    profiles_df = spark.read.jdbc(url=jdbc_url,
                                  table="profiles",
                                  properties=connection_properties)

    # Realizar el join entre users_df y profiles_df
    movies_profile_dataframe = users_df.join(
        profiles_df,
        users_df.nickname == profiles_df.user_nickname,
        "inner"
    )

    # Mostrar el esquema y algunas filas del DataFrame resultante
    print("Esquema del DataFrame 'movies_profile_dataframe':")
    movies_profile_dataframe.printSchema()

    print("Primeras filas del DataFrame 'movies_profile_dataframe':")
    movies_profile_dataframe.show(5)

    spark.stop()

if __name__ == "__main__":
    main()
