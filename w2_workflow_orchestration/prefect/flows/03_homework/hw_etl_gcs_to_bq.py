import pandas as pd
from prefect import task, flow
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
from pathlib import Path
from prefect_gcp.bigquery import bigquery_query

@task(retries=3, log_prints=True)
def extract_data(color: str, year: int, month: int) -> Path:
    """Extract data from GCS"""
    gcs_path = f"data/{color}/{color}_tripdata_{year}-{month:02}.parquet"
    gcs_block = GcsBucket.load("zoomcamp-2")
    gcs_block.get_directory(from_path=gcs_path, local_path=f"../")
    return Path(f"../{gcs_path}")

@task(log_prints=True)
def transform_data(path: Path) -> pd.DataFrame:
    """Data cleaning example"""
    df = pd.read_parquet(path)
    print(f"loading data count: {df['passenger_count'].sum()}")
    return df

@task(log_prints=True)
def load_data(df: pd.DataFrame, color, year) -> None:
    """Write DataFrame to Big Query"""
    gcp_credentials_block = GcpCredentials.load("zoomcamp-2")
    
    df.to_gbq(
        destination_table=f"trips_data_all.{color}_taxi_{year}",
        project_id="de-zoomcamp-378315",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500000,
        if_exists="append",
        location="asia-east1"
    )


@flow(log_prints=True)
def etl_gcs_to_bq(color, year, month) -> None:
    """The main flow to load data from bucket to Big Query"""

    path = extract_data(color, year, month)
    data = transform_data(path)
    load_data(data, color, year)

@flow(log_prints=True)
def etl_bq_parent_flow(color: str = "yellow", years: list[int] = [2021], months: list[int] = [1]):
    for year in years:
        for month in months:
            etl_gcs_to_bq(color, year, month)
    
    # gcp_credentials_block = GcpCredentials.load("zoomcamp")
    # query = '''
    #     SELECT COUNT(*)
    #     FROM `dtc-de-course-368906.trips_data_all.yellow_taxi_2019`
    # '''
    # result = bigquery_query(
    #     query, 
    #     gcp_credentials=gcp_credentials_block,
    #     location='asia-east1'
    # )
    # print(result)

if __name__ == '__main__':
    etl_bq_parent_flow(color, year, months)