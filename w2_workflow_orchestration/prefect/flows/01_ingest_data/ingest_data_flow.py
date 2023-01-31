import pandas as pd
from datetime import timedelta
import os
from prefect import flow, task
from prefect_sqlalchemy import SqlAlchemyConnector
from prefect.tasks import task_input_hash

@task(log_prints=True, tags=['extract'], cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def extract_data(url: str) -> pd.DataFrame:
    """Extract taxi data from web"""
    
    if url.endswith('.csv.gz'):
        csv_name = 'yellow_tripdata_2021-01.csv.gz'
    else:
        csv_name = 'output.csv'
    
    os.system(f"wget {url} -O {csv_name}")
    
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)
    df = next(df_iter)

    return df
    
@task(log_prints=True, tags=['transform'])
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform the time format and remove missing data """

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    print(f"pre: missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    df = df[df['passenger_count'] != 0]
    print(f"post: missing passenger count: {df['passenger_count'].isin([0]).sum()}")

    return df

@task(log_prints=True, tags=['load'])
def load_data(df: pd.DataFrame, table_name: str) -> None:
    """Load the data into PostgreSQL"""
    
    connection_block = SqlAlchemyConnector.load("zoomcamp-sqlalchemy")
    with connection_block.get_connection(begin=False) as engine:
        df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
        df.to_sql(name=table_name, con=engine, if_exists='append')

@flow(name="Subflow", log_prints=True)
def log_subflow(table_name: str) -> None:
    print(f"Logging Subflow for: {table_name}")

@flow(name="Ingest Data")
def main_flow(table_name: str) -> None:
    """The main ETL function"""

    data = extract_data('https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz')
    clean_data = transform_data(data)
    load_data(clean_data, table_name)

if __name__ == '__main__':
    main_flow('yellow_taxi_2021_01')