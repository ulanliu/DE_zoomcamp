import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq
from datetime import datetime 

PROJECT_ID = os.getenv('GCP_PROJECT_ID')
BUCKET = os.getenv('GCP_GCS_BUCKET')
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trips_data_all')

URL_PREFIX = 'https://d37ci6vzurychx.cloudfront.net/trip-data'
URL_TEMPLATE = URL_PREFIX + '/yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
OUTPUT_TEMPLATE = AIRFLOW_HOME + '/output_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
TABLE_TEMPLATE = 'yellow_taxi_{{ execution_date.strftime(\'%Y_%m\') }}'

def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)

with DAG(
    dag_id="data_ingestation_gcp_dag",
    schedule_interval="0 6 2 * *",
    start_date=datetime(2019, 3, 1),
    end_date=datetime(2019, 7, 31),
    catchup=True,
    max_active_runs=3
) as dag:

    download_dataset_task = BashOperator(
        task_id="download_dataset_task",
        bash_command=f'curl -sSLf {URL_TEMPLATE} > {OUTPUT_TEMPLATE}'
    )

    local_to_gcp_task = PythonOperator(
        task_id="local_to_gcp_task",
        python_callable=upload_to_gcs,
        op_kwargs=dict(
            bucket=BUCKET,
            object_name="raw/yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet",
            local_file=OUTPUT_TEMPLATE
        )
    )

    bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "external_table",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/raw/yellow_tripdata_" + "{{ execution_date.strftime(\'%Y-%m\') }}" + ".parquet"],
            },
        },
        retries=1
    )

    download_dataset_task >> local_to_gcp_task >> bigquery_external_table_task