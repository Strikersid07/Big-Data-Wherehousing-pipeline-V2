# Big-Data-Wherehousing-pipeline-V2
# ⚡ Automated Big Data Pipeline: NiFi → Ignite → Spark (Hudi) → Hive + HDFS → Trino → dbt  

### 🧠 Overview
This repository contains a fully automated **Big Data Pipeline** that orchestrates a complete data flow — from ingestion to analytics — using a modern open-source stack.

The setup integrates **Apache NiFi** for real-time ingestion, **Apache Ignite** for in-memory caching and compute, **Apache Spark 3.5** (with **Hudi**) for processing and incremental storage, **Hive Metastore + HDFS** for durability and schema tracking, and **Trino + dbt** for querying and transformations.

The included automation script handles startup, orchestration, and logging for each service, creating a repeatable and reliable workflow for data engineers.

---

## ⚙️ Pipeline Flow

**1️⃣ NiFi → Ignite**  
- **NiFi** ingests raw data directly into **Apache Ignite** caches or tables.  
- Ignite serves as a high-speed ingestion and compute layer, allowing **Spark** to read data in real-time without hitting disk.

**2️⃣ Spark 3.5 + Hudi → Hive + HDFS**  
- **Spark** runs the job `ignite_read1.py` to pull data from Ignite, process it, and write it into **Hudi tables**.  
- These Hudi tables are saved both to **HDFS** (for persistence) and registered in the **Hive Metastore** (for schema management).  
- The setup provides **ACID compliance, incremental updates, and snapshot isolation**.

**3️⃣ Hive Metastore**  
- Stores metadata for all Hudi tables, enabling query federation across Spark, Trino, and dbt.

**4️⃣ Trino Query Layer**  
- **Trino** connects to Hive Metastore and queries Hudi tables stored in HDFS for distributed, high-speed SQL analytics.

**5️⃣ dbt Transformation Layer**  
- **dbt** uses the Trino/Hive connection to perform data transformations, model creation, and schema validation.  
- Ensures all transformations are version-controlled, repeatable, and CI/CD compatible.

---

## 🧩 Tech Stack & Versions

| Component | Version | Role |
|------------|----------|------|
| **Java** | 17 | Runtime for Hadoop, Hive, Spark |
| **Apache Hadoop (HDFS + YARN)** | 3.x | Distributed storage & resource management |
| **Apache Hive** | 4.0.0 | Schema & metadata store |
| **Apache Ignite** | 2.x | In-memory ingestion & compute layer |
| **Apache Spark** | 3.5.x | Data processing engine (integrated with Hudi) |
| **Apache Hudi** | Spark 3.5 bundle JAR | Incremental data lake storage |
| **Trino** | 435+ | Distributed SQL query engine |
| **dbt-core** | Latest stable | Data transformation & modeling layer |
| **Apache NiFi** | 1.27+ | Data ingestion & orchestration layer |

---

## 🧰 Prerequisites

Before running the automation:

- Set required environment variables:
  ```bash
  export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
  export HADOOP_HOME=$HOME/hadoop
  export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
