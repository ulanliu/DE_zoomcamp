import pandas as pd
from prefect import task, flow
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
from pathlib import Path

@task(retries=3)
def extract_data(color: str, year: int, month: int) -> Path:
    """Extract data from GCS"""
    gcs_path = f"data/{color}/{color}_tripdata_{year}-{month:02}.parquet"
    gcs_block = GcsBucket.load("zoomcamp")
    gcs_block.get_directory(from_path=gcs_path, local_path=f"../")
    return Path(f"../{gcs_path}")

@task()
def transform_data(path: Path) -> pd.DataFrame:
    """Data cleaning example"""
    df = pd.read_parquet(path)
    print(f"pre: missing passenger count: {df['passenger_count'].isna().sum()}")
    df["passenger_count"].fillna(0, inplace=True)
    print(f"post: missing passenger count: {df['passenger_count'].isna().sum()}")
    return df

@task()
def load_data(df: pd.DataFrame) -> None:
    """Write DataFrame to Big Query"""
    gcp_credentials_block = GcpCredentials.load("zoomcamp")
    
    df.to_gbq(
        destination_table="trips_data_all.yellow_taxi_2021",
        project_id="dtc-de-course-368906",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500000,
        if_exists="append"
    )


@flow()
def etl_gcs_to_bq(color: str, year: int, month: int):
    """The main flow to load data from bucket to Big Query"""

    path = extract_data(color, year, month)
    data = transform_data(path)
    load_data(data)

if __name__ == '__main__':
    color = "yellow"
    year = 2021
    month = 1
    etl_gcs_to_bq(color, year, month)