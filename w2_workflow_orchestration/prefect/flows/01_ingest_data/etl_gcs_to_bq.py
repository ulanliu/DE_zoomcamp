from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials

@flow()
def etl_gcs_to_bq() -> None:
    """The main function to load data from storage into Big query"""
    color = 'yellow'
    year = 2021
    month = 1

    