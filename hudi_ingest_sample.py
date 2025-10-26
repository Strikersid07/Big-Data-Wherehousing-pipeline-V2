from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, explode
from pyspark.sql.types import StructType, StructField, IntegerType, StringType

# Initialize SparkSession with Hive support
spark = SparkSession.builder \
    .appName("Hudi Ingest Sample") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.hudi.catalog.HoodieCatalog") \
    .config("spark.sql.extensions", "org.apache.spark.sql.hudi.HoodieSparkSessionExtension") \
    .config("spark.sql.warehouse.dir", "hdfs:///user/hive/warehouse") \
    .enableHiveSupport() \
    .getOrCreate()

# Define schema for posts
schema = StructType([
    StructField("userId", IntegerType(), True),
    StructField("id", IntegerType(), True),
    StructField("title", StringType(), True),
    StructField("body", StringType(), True)
])

# Load data
input_path = "hdfs:///user/hpstrikersid_0711/data/raw/posts.json"
df = spark.read.schema(schema).option("multiline", "true").json(input_path)
df = df.withColumn("ingest_time", current_timestamp())

# Hudi + Hive sync settings
output_path = "hdfs:///user/hive/warehouse/posts_hudi"
table_name = "posts_hudi"
db_name = "default"

df.write.format("hudi") \
    .option("hoodie.table.name", table_name) \
    .option("hoodie.datasource.write.recordkey.field", "id") \
    .option("hoodie.datasource.write.partitionpath.field", "") \
    .option("hoodie.datasource.write.table.name", table_name) \
    .option("hoodie.datasource.write.operation", "insert") \
    .option("hoodie.upsert.shuffle.parallelism", 2) \
    .option("hoodie.insert.shuffle.parallelism", 2) \
    .option("hoodie.datasource.hive_sync.enable", "true") \
    .option("hoodie.datasource.hive_sync.mode", "hms") \
    .option("hoodie.datasource.hive_sync.database", db_name) \
    .option("hoodie.datasource.hive_sync.table", table_name) \
    .option("hoodie.datasource.hive_sync.use_jdbc", "false") \
    .option("hoodie.datasource.hive_sync.support_timestamp", "true") \
    .option("hoodie.datasource.hive_sync.partition_extractor_class", "org.apache.hudi.hive.NonPartitionedExtractor") \
    .mode("overwrite") \
    .save(output_path)

print("✅ Ingestion to Hudi + Hive Metastore successful")
spark.stop()
