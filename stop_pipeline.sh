#!/bin/bash
# ===============================
# Stop Big Data Pipeline
# NiFi + Trino + Ignite + Hive Metastore + HDFS/YARN + dbt venv
# ===============================

set -euo pipefail

echo "==== Stopping Big Data Pipeline ===="


# --- 2. Stop Trino ---
echo "[2/6] Stopping Trino..."
$HOME/trino/bin/launcher stop || true
sleep 5

# --- 3. Stop Ignite ---
#echo [3/6] Stopping Apache Ignite..."
#IGNITE_PID=$(jps | grep CommandLineStartup" | awk {print $1}')
#if [ -n $IGNITE_PID" ]; then
#  kill -9 $IGNITE_PID
#  echo Ignite stopped."
#else
#  echo Ignite was not running."
#fi
sleep 5

# --- 4. Stop Hive Metastore ---
echo "[4/6] Stopping Hive Metastore..."
HMS_PID=$(jps | grep "RunJar" | awk '{print $1}')
if [ -n "$HMS_PID" ]; then
  kill -9 $HMS_PID
  echo "Hive Metastore stopped."
else
  echo "Hive Metastore was not running."
fi
sleep 5

# --- 5. Stop HDFS + YARN ---
echo "[5/6] Stopping HDFS + YARN..."
$HOME/hadoop/sbin/stop-all.sh || true
sleep 5

# --- 6. Deactivate dbt venv if active ---
if [ -n "${VIRTUAL_ENV:-}" ]; then
  echo "[6/6] Deactivating dbt environment..."
  deactivate
fi

echo "==== All Services Stopped ===="
