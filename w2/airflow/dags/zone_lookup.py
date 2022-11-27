import os
import logging

from datetime import datetime

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage

import pyarrow.csv as pv
import pyarrow.parquet as pq

PROJECT_ID = os.getenv('GCP_PROJECT_ID')
BUCKET = os.getenv('GCP_GCS_BUCKET')
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trips_data_all')

default_args = {
    "owner": "airflow",
    #"start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1
}

def upload_to_gcs(bucket, object_name, local_file):
    client = storage.Client()
    bucket = client.bucket(bucket)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)

def format_to_parquet(src_file, dest_file):
    if not src_file.endswith('.csv'):
        logging.error('Can only accept source files in CSV format, for the moment')
        return
    table = pv.read_csv(src_file)
    pq.write_table(table, dest_file)

ZONE_URL_TEMPLATE = 'https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv'
ZONE_CSV_TEMPLATE = AIRFLOW_HOME + '/output_{{ execution_date.strftime(\'%Y-%m\') }}.csv'
ZONE_PARQUET_TEMPLATE = AIRFLOW_HOME + '/output_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
ZONE_TABLE_TEMPLATE = 'taxi_zone_lookup'

with DAG(
    dag_id="zone_data_to_gcp_dag",
    default_args=default_args,
    start_date=datetime(2019, 1, 1),
    schedule_interval='@once',
    catchup=True
) as dag:
    
    download_dataset_task = BashOperator(
        task_id="download_dataset_task",
        bash_command=f'curl -sSLf {ZONE_URL_TEMPLATE} > {ZONE_CSV_TEMPLATE}'
    )

    parquetize_task = PythonOperator(
        task_id="parquetize_file_task",
        python_callable=format_to_parquet,
        op_kwargs={
            'src_file': ZONE_CSV_TEMPLATE,
            'dest_file': ZONE_PARQUET_TEMPLATE
        }
    )

    local_to_gcp_task = PythonOperator(
        task_id="local_to_gcp_task",
        python_callable=upload_to_gcs,
        op_kwargs=dict(
            bucket=BUCKET,
            object_name="raw/taxi_zone/taxi_zone_lookup.parquet",
            local_file=ZONE_PARQUET_TEMPLATE
        )
    )

    download_dataset_task >> parquetize_task >> local_to_gcp_task