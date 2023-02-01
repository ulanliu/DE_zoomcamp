from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp.bigquery import bigquery_load_cloud_storage
from prefect_gcp import GcpCredentials
import os
import logging

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
def write_gcs(path: Path) -> Path:
    gcs_block = GcsBucket.load("zoomcamp")
    gcs_block.upload_from_path(from_path=path, to_path=path)
    gcs_path = path

    return gcs_path

@task()
def load_data_from_gcs_to_bq(gcs_path) -> None:
    gcp_credentials_block = GcpCredentials.load("zoomcamp")

    bigquery_load_cloud_storage(
        dataset="trips_data_all",
        table="green_taxi_2020",
        uri=gcs_path,
        gcp_credentials=gcp_credentials_block.get_credentials_from_service_account()
    )

@flow()
def etl_web_to_gcs(color: str, year: int, month: int) -> None:
    """The main ETL function"""
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"

    df = fetch(dataset_url)
    df_clean = clean(df, color)
    path = write_local(df_clean, color, dataset_file)
    gcs_path = write_gcs(path)
    load_data_from_gcs_to_bq(gcs_path)

@flow()
def etl_parent_flow(
    color: str = "yellow", year: int = 2021, months: list[int] = [1]
) -> None:
    for month in months:
        etl_web_to_gcs(color, year, month)

if __name__ == "__main__":
    etl_parent_flow(color, year, months)