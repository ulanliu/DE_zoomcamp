import os
import logging

from datetime import datetime

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
import pyarrow as pa
import pyarrow.csv as pv
import pyarrow.parquet as pq
import pandas as pd

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

def remodel_parquet_data_type(src_file, dest_file):
        # df = pd.read_parquet(src_file)
        # df = df.astype(
        # {
        #     'dispatching_base_num': 'str',
        #     'pickup_datetime': 'datetime64[ns]',
        #     'dropOff_datetime': 'datetime64[ns]',
        #     'PUlocationID': 'Int64',
        #     'DOlocationID': 'Int64',
        #     'SR_Flag': 'Int64',
        #     'Affiliated_base_number': 'str'
        # })
        # df.to_parquet(dest_file, allow_truncated_timestamps=True)
    
        df = pq.read_table(src_file).to_pandas(safe=False)
        df = df.astype(
        {
            'dispatching_base_num': 'str',
            'pickup_datetime': 'datetime64[ns]',
            'dropOff_datetime': 'datetime64[ns]',
            'PUlocationID': 'Int64',
            'DOlocationID': 'Int64',
            'SR_Flag': 'Int64',
            'Affiliated_base_number': 'str'
        })
        # To avoid 'ArrowInvalid' Casting from timestamp[ns] to timestamp[us] would lose data: -3787364347419103232
        # Need to add use_deprecated_int96_timestamps=True
        df.to_parquet(dest_file, use_deprecated_int96_timestamps=True)

FHV_URL_PREFIX = 'https://d37ci6vzurychx.cloudfront.net/trip-data'
FHV_URL_TEMPLATE = FHV_URL_PREFIX + '/fhv_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
FHV_OUTPUT_TEMPLATE = AIRFLOW_HOME + '/output_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
FHV_TABLE_TEMPLATE = 'fhv_tripdata_{{ execution_date.strftime(\'%Y_%m\') }}'
FHV_OUTPUT_EDITED_TEMPLATE = AIRFLOW_HOME + '/output_{{ execution_date.strftime(\'%Y-%m\') }}_edited.parquet'

with DAG(
    dag_id="FHV_data_upload_dag",
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

    remodel_data_type_task = PythonOperator(
        task_id='remodel_data_type_task',
        python_callable=remodel_parquet_data_type,
        op_kwargs={
            'src_file':FHV_OUTPUT_TEMPLATE,
            'dest_file':FHV_OUTPUT_EDITED_TEMPLATE
        }
    )

    local_to_gcp_task = PythonOperator(
        task_id="local_to_gcp_task",
        python_callable=upload_to_gcs,
        op_kwargs=dict(
            bucket=BUCKET,
            object_name="raw/fhv_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet",
            local_file=FHV_OUTPUT_EDITED_TEMPLATE
        )
    )

    download_dataset_task >> remodel_data_type_task >> local_to_gcp_task

