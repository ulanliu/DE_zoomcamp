import requests
from datetime import date
from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
from prefect_gcp.bigquery import bigquery_load_cloud_storage
from prefect_gcp.bigquery import bigquery_load_file
import os
import logging

@task(log_prints=True)
def extract(url: str) -> Path:
    """
    Download monkeypox and covid-19 daily data from Our World In Data into local
    """
    day = date.today().strftime('%Y%m%d')
    if 'monkeypox' in url:
        path = Path(f'data/monkeypox_{day}.csv')
        r = requests.get(url)
        if not os.path.isdir('data'):
            os.mkdir('data')
        with open(path, 'w+') as f:
            f.write(r.text)
        logging.info("successfully download latest monkeypox data")
    
    if 'covid-19' in url:
        path = Path(f'data/covid-19_{day}.csv')
        r = requests.get(url)
        if not os.path.isdir('data'):
            os.mkdir('data')
        with open(path, 'w+') as f:
            f.write(r.text)
        logging.info("successfully download latest covid-19 data")

    return path

@task(log_prints=True)
def load_data_to_gcs(path: Path) -> None:
    """
    Load the data into GCS
    """
    gcs_block = GcsBucket.load("zoomcamp-2")
    gcs_block.upload_from_path(from_path=path, to_path=path)
    gcs_path = path
    return gcs_path

@flow()
def load_data_to_bq(gcs_path: Path):
    """
    Transfer data from GCS to BQ
    """
    gcp_credentials_block = GcpCredentials.load("zoomcamp-2")
    
    if 'monkeypox' in str(gcs_path):
        table_name = 'monkeypox'
    if 'covid-19' in str(gcs_path):
        table_name = 'covid-19'    
    result = bigquery_load_file(
        dataset='who_disease_data',
        table=table_name,
        path=gcs_path,
        gcp_credentials=gcp_credentials_block
    )

    return result

@flow()
def el_web_to_gcs(url: str) -> None:
    path = extract(url)
    gcs_path = load_data_to_gcs(path)
    load_data_to_bq(gcs_path)

@flow()
def el_parent_flow(url_list: list[str]=["https://raw.githubusercontent.com/owid/monkeypox/main/owid-monkeypox-data.csv", "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"]) -> None:
    """ The main flow function """
    for url in url_list:
        el_web_to_gcs(url)

if __name__ == "__main__":
    el_parent_flow()
