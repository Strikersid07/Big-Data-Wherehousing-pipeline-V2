from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Read Ignite Table") \
    .getOrCreate()

df = spark.read.format("jdbc").options(
    url="jdbc:ignite:thin://127.0.0.1:10800/PUBLIC",
    driver="org.apache.ignite.IgniteJdbcThinDriver",
    dbtable="CRYPTO_TICKS",
    fetchsize="1000"   # 👈 Force non-zero fetch size
).load()

df.show(10, truncate=False)
