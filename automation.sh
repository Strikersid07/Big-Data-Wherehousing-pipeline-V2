#!/bin/bash
# ===============================
# Automation Pipeline Script
# NiFi + HDFS + Hive Metastore + Ignite + Spark (via spark-submit) + Hudi + Trino + dbt
# ===============================

# ----------------------------
# 0. Environment Variables
# ----------------------------
set -euo pipefail

echo "==== Starting Big Data Pipeline ===="

# ============================
# 1. Start HDFS + YARN
# ============================
echo "[1/6] Starting HDFS + YARN..."
export HADOOP_HOME=$HOME/hadoop
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

cd $HADOOP_HOME/sbin
./start-dfs.sh
sleep 5
./start-yarn.sh
sleep 5
hdfs dfs -mkdir -p /user/hive/warehouse || true
echo "HDFS started."
cd ~

# ============================
# 2. Start Hive Metastore
# ============================
echo "[2/6] Starting Hive Metastore..."
cd $HOME/apache-hive-4.0.0-bin/bin/
nohup ./hive --service metastore > $HOME/hive-metastore.log 2>&1 &
sleep 8
echo "Hive Metastore started (logs: $HOME/hive-metastore.log)"
cd ~

# ============================
# 3. Start Apache Ignite
# ============================
echo "[3/6] Starting Apache Ignite..."
#cd $HOME/ignite/bin
#nohup ./ignite.sh > $HOME/ignite.log 2>&1 &
sleep 10
echo "Ignite started (logs: $HOME/ignite.log)"
cd ~

# ============================
# 4. Spark Submit
# ============================
echo "[4/6] Starting Spark submit"
cd $HOME/INPUT

# Make sure to use correct variable names and no spaces around =
spark-submit ignite_read1.py

echo "Spark job completed."

# ============================
# 5. Start Trino
# ============================
echo "[5/6] Starting Trino..."
cd $HOME/trino/bin
nohup ./launcher start > $HOME/trino.log 2>&1 &
sleep 35
echo "Trino started (logs: $HOME/trino.log)"
cd ~

# ============================
# 6. Run dbt for schema push
# ============================
echo "[6/6] Running dbt..."
cd $HOME/my_project

# Activate dbt virtual environment
source $HOME/dbt_env/bin/activate

# Save logs to file AND print to screen
LOGFILE="$HOME/dbt_run_$(date +%Y%m%d_%H%M%S).log"
dbt clean
dbt deps
dbt run | tee -a "$LOGFILE"

# Deactivate environment
deactivate

echo "dbt transformations applied (Ignite + Hive + HDFS). Logs saved at: $LOGFILE"
echo "==== Pipeline Completed Successfully ===="
