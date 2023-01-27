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

FHV_URL_PREFIX = 'https://d37ci6vzurychx.cloudfront.net/trip-data'
FHV_URL_TEMPLATE = FHV_URL_PREFIX + '/fhv_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
FHV_OUTPUT_TEMPLATE = AIRFLOW_HOME + '/output_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
FHV_TABLE_TEMPLATE = 'fhv_tripdata_{{ execution_date.strftime(\'%Y_%m\') }}'


with DAG(
    dag_id="FHV_data_to_gcp_dag",
    schedule_interval="0 6 2 * *",
    start_date=datetime(2019, 1, 1),
    end_date=datetime(2019, 12, 31),
    default_args=default_args,
    catchup=True,
    max_active_runs=3
) as dag:
    
    download_dataset_task = BashOperator(
        task_id="download_dataset_task",
        bash_command=f'curl -sSLf {FHV_URL_TEMPLATE} > {FHV_OUTPUT_TEMPLATE}'
    )

    local_to_gcp_task = PythonOperator(
        task_id="local_to_gcp_task",
        python_callable=upload_to_gcs,
        op_kwargs=dict(
            bucket=BUCKET,
            object_name="raw/fhv_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet",
            local_file=FHV_OUTPUT_TEMPLATE
        )
    )

    download_dataset_task >> local_to_gcp_task

