#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

service cron start
(echo "0 * * * * kinit $KRB_PRINCIPAL -kt $KRB_KEYTAB") | crontab -

kinit $KRB_PRINCIPAL -kt $KRB_KEYTAB

# uncomment below when you see any issue with db...
# mlflow db upgrade $DB_URI

mlflow server \
    --backend-store-uri $DB_URI \
    --host 0.0.0.0 \
    --port $VIRTUAL_PORT \
    --default-artifact-root $ARTIFACT_PATH
        --gunicorn-opts "log-level debug"
