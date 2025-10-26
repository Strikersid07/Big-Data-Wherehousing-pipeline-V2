from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit

spark = SparkSession.builder \
    .appName("Hudi Ingest Posts") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.hudi.catalog.HoodieCatalog") \
    .enableHiveSupport() \
    .getOrCreate()

# Load and clean data
df = spark.read.json("hdfs://localhost:9000/user/hpstrikersid_0711/data/raw/posts.json")

df = df.filter("id IS NOT NULL") \
       .withColumn("created_at", current_timestamp()) \
       .withColumn("partition_col", lit("default_partition"))

# Write to Hudi
df.write.format("hudi") \
    .option("hoodie.table.name", "posts_hudi") \
    .option("hoodie.datasource.write.recordkey.field", "id") \
    .option("hoodie.datasource.write.partitionpath.field", "partition_col") \
    .option("hoodie.datasource.write.precombine.field", "created_at") \
    .option("hoodie.datasource.write.table.type", "COPY_ON_WRITE") \
    .option("hoodie.datasource.write.keygenerator.class", "org.apache.hudi.keygen.SimpleKeyGenerator") \
    .option("hoodie.index.type", "SIMPLE") \
    .option("hoodie.parquet.compression.codec", "snappy") \
    .option("hoodie.metadata.enable", "false") \
    .option("hoodie.datasource.hive_sync.enable", "true") \
    .option("hoodie.datasource.hive_sync.table", "posts_hudi") \
    .option("hoodie.datasource.hive_sync.database", "default") \
    .option("hoodie.datasource.hive_sync.mode", "hms") \
    .option("hoodie.datasource.hive_sync.support_timestamp", "true") \
    .option("hoodie.datasource.hive_sync.partition_fields", "partition_col") \
    .option("hoodie.datasource.hive_sync.use_jdbc", "false") \
    .option("hoodie.datasource.hive_sync.metastore.uris", "thrift://localhost:9083") \
    .mode("overwrite") \
    .save("hdfs://localhost:9000/hive/warehouse/posts_hudi")

spark.stop()