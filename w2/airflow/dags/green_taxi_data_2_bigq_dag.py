import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator, BigQueryInsertJobOperator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator

import pyarrow.csv as pv
import pyarrow.parquet as pq
from datetime import datetime 

PROJECT_ID = os.getenv('GCP_PROJECT_ID')
BUCKET = os.getenv('GCP_GCS_BUCKET')
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trips_data_all')

URL_PREFIX = 'https://d37ci6vzurychx.cloudfront.net/trip-data'
URL_TEMPLATE = URL_PREFIX + '/green_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
OUTPUT_TEMPLATE = AIRFLOW_HOME + '/output_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
OUTPUT_EDITED_TEMPLATE = AIRFLOW_HOME + '/output_{{ execution_date.strftime(\'%Y-%m\') }}_edited.parquet'
TABLE_TEMPLATE = 'green_taxi_{{ execution_date.strftime(\'%Y_%m\') }}'

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

def remodel_parquet_data_type(src_file, dest_file):
    
        df = pq.read_table(src_file).to_pandas(safe=False)
        df = df.astype(
        {
            'VendorID': 'str',
            'lpep_pickup_datetime': 'datetime64[ns]',
            'lpep_dropoff_datetime': 'datetime64[ns]',
            'store_and_fwd_flag': 'str',
            'RatecodeID': 'float64',
            'PULocationID': 'float64',
            'DOLocationID': 'float64',
            'passenger_count': 'float64',
            'trip_distance': 'float64',
            'fare_amount': 'float64',
            'extra': 'float64',
            'mta_tax': 'float64',
            'tip_amount': 'float64',
            'tolls_amount': 'float64',
            'ehail_fee': 'float64',
            'improvement_surcharge': 'float64',
            'total_amount': 'float64',
            'payment_type': 'float64',
            'trip_type': 'float64',
            'congestion_surcharge': 'float64'
        })
        # To avoid 'ArrowInvalid' Casting from timestamp[ns] to timestamp[us] would lose data: -3787364347419103232
        # Need to add use_deprecated_int96_timestamps=True
        df.to_parquet(dest_file, use_deprecated_int96_timestamps=True)

default_args = {
    "owner": "airflow",
    #"start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1
}

with DAG(
    dag_id="green_taxi_2_bq_dag",
    schedule_interval="0 6 2 * *",
    default_args=default_args,
    start_date=datetime(2019, 1, 1),
    end_date=datetime(2020, 12, 31),
    catchup=True,
    max_active_runs=3
) as dag:

    download_dataset_task = BashOperator(
        task_id="download_dataset_task",
        bash_command=f'curl -sSLf {URL_TEMPLATE} > {OUTPUT_TEMPLATE}'
    )

    remodel_data_type_task = PythonOperator(
        task_id='remodel_data_type_task',
        python_callable=remodel_parquet_data_type,
        op_kwargs={
            'src_file':OUTPUT_TEMPLATE,
            'dest_file':OUTPUT_EDITED_TEMPLATE
        }
    )

    local_to_gcp_task = PythonOperator(
        task_id="local_to_gcp_task",
        python_callable=upload_to_gcs,
        op_kwargs=dict(
            bucket=BUCKET,
            object_name="raw/green_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet",
            local_file=OUTPUT_EDITED_TEMPLATE
        )
    )

    move_files_gcs_task = GCSToGCSOperator(
        task_id='gcs_2_gcs_task',
        source_bucket=BUCKET,
        source_object='raw/green_tripdata_*.parquet',
        destination_bucket=BUCKET,
        destination_object='green/',
        move_object=True
    )

    gcs_2_bq_task = BigQueryCreateExternalTableOperator(
        task_id="gcs_2_bq_ext_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "green_taxi_table",
            },
            "externalDataConfiguration": {
                "autodetect": True,
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/green/*"],
            },
        }
    )

    # CREATE_PART_TBL_QUERY = (
    #     f"""
    #     CREATE OR REPLACE TABLE {BIGQUERY_DATASET}.green_tripdata_partitoned
    #     PARTITION BY DATE(tpep_pickup_datetime) AS
    #     SELECT * FROM {BIGQUERY_DATASET}.external_green_tripdata;
    #     """
    # )

    # bq_2_part_task = BigQueryInsertJobOperator(
    #     task_id="bq_ext_2_part_task",
    #     configuration={
    #         "query": {
    #             "query": CREATE_PART_TBL_QUERY,
    #             "useLegacySql": False
    #         }
    #     }
    # )

    download_dataset_task >> remodel_data_type_task >> local_to_gcp_task >> move_files_gcs_task >> gcs_2_bq_task