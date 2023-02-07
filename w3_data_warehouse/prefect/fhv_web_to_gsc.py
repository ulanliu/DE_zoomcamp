from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
import os

@task()
def fetch(dataset_url: str) -> pd.DataFrame:
    """Read taxi data from web into DataFrame"""
    
    df = pd.read_csv(dataset_url)

    return df

@task(log_prints=True)
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Transform the time format"""
    
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
    df['dropOff_datetime'] = pd.to_datetime(df['dropOff_datetime'])
    df = df.astype({'PUlocationID': 'Int64', 'DOlocationID': 'Int64'})
    print(df.head(2))
    print(f"columns: {df.dtypes}")
    print(f"rows: {len(df)}")

    return df

@task(log_prints=True)
def write_local(df: pd.DataFrame, dataset_file: str) -> Path:
    """Write DataFrame out locally as parquet files"""
    
    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.isdir(f'data/fhv'):
        os.mkdir(f'data/fhv')

    path = Path(f"data/fhv/{dataset_file}.parquet")
    df.to_parquet(path, compression="gzip")

    return path

@task()
def write_gcs(path: Path) -> None:
    gcs_block = GcsBucket.load("zoomcamp")
    gcs_block.upload_from_path(from_path=path, to_path=path)

@flow()
def etl_web_to_gcs(year: int, month: int) -> None:
    """The main ETL function"""
    
    dataset_file = f"fhv_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/{dataset_file}.csv.gz"

    df = fetch(dataset_url)
    df_clean = clean(df)
    path = write_local(df_clean, dataset_file)
    write_gcs(path)

@flow()
def etl_parent_flow(year: int, months: list[int]) -> None:
    for month in months:
        etl_web_to_gcs(year, month)

if __name__ == "__main__":
    etl_parent_flow()