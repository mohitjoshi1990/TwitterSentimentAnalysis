#!/usr/bin/env bash

IP=$(grep $(hostname) /tmp/nodes  | awk -F ' ' {'print $2'} | xargs)
export SPARK_MASTER_HOST=$IP
export JAVA_HOME="/usr/"
export SPARK_LOCAL_IP="127.0.0.1"

