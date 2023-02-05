from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp.bigquery import bigquery_load_cloud_storage
from prefect_gcp import GcpCredentials
import os
import logging
from google.cloud import bigquery

@task()
def fetch(dataset_url: str) -> pd.DataFrame:
    """Read taxi data from web into DataFrame"""
    
    df = pd.read_csv(dataset_url)

    return df

@task(log_prints=True)
def clean(df: pd.DataFrame, color: str) -> pd.DataFrame:
    """Transform the time format"""
    if color == "yellow":
        df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
        df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    elif color == "green":
        df["lpep_pickup_datetime"] = pd.to_datetime(df["lpep_pickup_datetime"])
        df["lpep_dropoff_datetime"] = pd.to_datetime(df["lpep_dropoff_datetime"])
    
    print(df.head(2))
    print(f"columns: {df.dtypes}")
    print(f"rows: {len(df)}")

    return df

@task(log_prints=True)
def write_local(df: pd.DataFrame, color: str, dataset_file: str) -> Path:
    """Write DataFrame out locally as parquet files"""
    
    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.isdir(f'data/{color}'):
        os.mkdir(f'data/{color}')
    if not os.path.isfile(f"data/{color}/{dataset_file}.parquet"):
        path = Path(f"data/{color}/{dataset_file}.parquet")
        df.to_parquet(path, compression="gzip")
        logging.info("successfully create parquet file")
    else:
        path = Path(f"data/{color}/{dataset_file}.parquet")
        logging.info("Already has this file")

    return path

@task()
def write_gcs(path: Path) -> None:
    gcs_block = GcsBucket.load("zoomcamp")
    gcs_block.upload_from_path(from_path=path, to_path=path)

@flow()
def etl_web_to_gcs(color: str, year: int, month: int) -> None:
    """The main ETL function"""
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"

    df = fetch(dataset_url)
    df_clean = clean(df, color)
    path = write_local(df_clean, color, dataset_file)
    write_gcs(path)
    
    gcp_credentials_block = GcpCredentials.load("zoomcamp")
    
    job_config = bigquery.LoadJobConfig()
    job_config._properties["load"]["preserve_ascii_control_characters"] = True

    schema = [
        bigquery.SchemaField('VendorID', 'STRING', mode="REQUIRED"),
        bigquery.SchemaField('lpep_pickup_datetime', 'TIMESTAMP', mode="REQUIRED"),
        bigquery.SchemaField('lpep_dropoff_datetime', 'TIMESTAMP', mode="REQUIRED"),
        bigquery.SchemaField('store_and_fwd_flag', 'STRING', mode="REQUIRED"),
        bigquery.SchemaField('RatecodeID', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('PULocationID', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('DOLocationID', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('passenger_count', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('trip_distance', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('fare_amount', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('extra', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('mta_tax', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('tip_amount', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('tolls_amount', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('ehail_fee', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('improvement_surcharge', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('total_amount', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('payment_type', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('trip_type', 'FLOAT64', mode="REQUIRED"),
        bigquery.SchemaField('congestion_surcharge', 'FLOAT64', mode="REQUIRED"),
    ]

    bigquery_load_cloud_storage(
        dataset="trips_data_all",
        table="green_taxi_2020",
        uri=f"gs://dtc_data_lake_dtc-de-course-368906/data/{color}/{color}_tripdata_{year}-{month:02}.parquet",
        gcp_credentials=gcp_credentials_block,
        job_config=job_config,
        schema=schema,
        location='asia-east1'
    )

@flow()
def etl_parent_flow(
    color: str = "yellow", year: int = 2021, months: list[int] = [1]
) -> None:
    for month in months:
        etl_web_to_gcs(color, year, month)

if __name__ == "__main__":
    etl_parent_flow(color, year, months)
