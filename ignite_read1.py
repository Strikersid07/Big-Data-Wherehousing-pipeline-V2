from pyspark.sql import SparkSession
from pyspark.sql.utils import AnalysisException

# 1. Start Spark session with Hive support
spark = SparkSession.builder \
    .appName("IgniteToHudi") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.catalogImplementation", "hive") \
    .config("hive.metastore.uris", "thrift://localhost:9083") \
    .config("spark.driver.userClassPathFirst", "true") \
    .config("spark.executor.userClassPathFirst", "true") \
    .enableHiveSupport() \
    .getOrCreate()

# 2. Try dropping previous Hudi RO/RT tables, ignore errors if not exist
for table in ["crypto_ticks_hudi", "crypto_ticks_hudi_ro", "crypto_ticks_hudi_rt"]:
    try:
        spark.sql(f"DROP TABLE IF EXISTS {table}")
        print(f"Dropped table if existed: {table}")
    except AnalysisException as e:
        print(f"Could not drop table {table}, continuing. Error: {e}")

# 3. Read from Ignite
ignite_df = spark.read.format("jdbc").options(
    url="jdbc:ignite:thin://127.0.0.1:10800/PUBLIC",
    driver="org.apache.ignite.IgniteJdbcThinDriver",
    dbtable="CRYPTO_TICKS",
    fetchsize="1000"
).load()

# 4. Hudi options
hudi_options = {
    "hoodie.table.name": "crypto_ticks_hudi",
    "hoodie.datasource.write.recordkey.field": "ID",
    "hoodie.datasource.write.precombine.field": "LAST_UPDATED",
    "hoodie.datasource.write.operation": "upsert",
    "hoodie.datasource.write.table.type": "MERGE_ON_READ",
    "hoodie.metadata.enable": "false",
    # Hive sync
    "hoodie.datasource.hive_sync.enable": "true",
    "hoodie.datasource.hive_sync.mode": "hms",
    "hoodie.datasource.hive_sync.database": "default",
    "hoodie.datasource.hive_sync.table": "crypto_ticks_hudi",
    "hoodie.datasource.hive_sync.use_jdbc": "false"
}

# 5. Write to Hudi (HDFS + Hive)
ignite_df.write.format("hudi") \
    .options(**hudi_options) \
    .mode("overwrite") \
    .option("hoodie.datasource.write.hive_style_partitioning", "true") \
    .option("hoodie.cleaner.policy", "KEEP_LATEST_COMMITS") \
    .save("hdfs://localhost:9000/user/hudi/crypto_ticks_hudi")

spark.stop()
