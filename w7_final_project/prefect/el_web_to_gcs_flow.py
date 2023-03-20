import requests
from datetime import date
from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
from prefect_gcp.bigquery import bigquery_load_cloud_storage
import os
import logging

@task(log_prints=True)
def extract(url: str) -> Path:
    
    # monkeypox_url = 'https://raw.githubusercontent.com/owid/monkeypox/main/owid-monkeypox-data.csv'
    # covid_url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'

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
    gcs_block = GcsBucket.load("zoomcamp-2")
    gcs_block.upload_from_path(from_path=path, to_path=path)

@task(log_prints=True)
def load_data_to_bq(path: Path, url: str) -> None:
    gcp_credentials_block = GcpCredentials.load("zoomcamp-2")

    df = pd.read_csv(path)
    if 'monkeypox' in url:
        table_name = 'monkeypox'
    if 'covid-19' in url:
        table_name = 'covid-19'
    
    df.to_gbq(
        destination_table=f"who_disease_data.{table_name}",
        project_id="de-zoomcamp-378315",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        if_exists="replace"
    )

@flow()
def el_web_to_gcs(url: str) -> None:
    path = extract(url)
    load_data_to_gcs(path)
    load_data_to_bq(path, url)

@flow()
def el_parent_flow(url_list: list[str]) -> None:
    for url in url_list:
        el_web_to_gcs(url)


if __name__ == "__main__":
    el_parent_flow()
