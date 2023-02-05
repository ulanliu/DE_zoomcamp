from prefect import flow, task
from prefect_gcp.bigquery import bigquery_load_cloud_storage
from prefect_gcp import GcpCredentials
from google.cloud import bigquery

@flow()
def etl_web_to_gcs(color: str, year: int, month: int) -> None:
    """The main ETL function"""
    gcp_credentials_block = GcpCredentials.load("zoomcamp")

    job_config = bigquery.LoadJobConfig(autodetect=True)
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
        uri=f"gs://dtc_data_lake_dtc-de-course-368906/data/{color}/{color}_tripdata_{year}-{month:02}",
        gcp_credentials=gcp_credentials_block,
        job_config=job_config,
        schema=schema,
        location='asia-east1'
    )

    
if __name__ == "__main__":
    color = "green"
    year = 2020
    month = 1
    etl_web_to_gcs(color, year, month)