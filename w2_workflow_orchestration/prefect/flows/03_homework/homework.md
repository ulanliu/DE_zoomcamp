# Question 1. Load January 2020 data
   
`prefect deployment build -a hw_etl_web_to_gcs.py:etl_web_to_gcs -n "hw_flow_1"`     
   
`prefect deployment run etl-web-to-gcs/hw_flow_1 -p "color=green" -p "year=2020" -p "month=1"`   

Logs:
```
Downloading flow code from storage at '/Users/peter/DE_zoomcamp/w2_workflow_orchestration/prefect'
04:14:23 PM
Created task run 'fetch-ba00c645-0' for task 'fetch'
04:14:24 PM
Executing 'fetch-ba00c645-0' immediately...
04:14:24 PM
Finished in state Completed()
04:14:29 PM
fetch-ba00c645-0
Created task run 'clean-2c6af9f6-0' for task 'clean'
04:14:29 PM
Executing 'clean-2c6af9f6-0' immediately...
04:14:29 PM
   VendorID lpep_pickup_datetime  ... trip_type congestion_surcharge
0       2.0  2019-12-18 15:52:30  ...       1.0                  0.0
1       2.0  2020-01-01 00:45:58  ...       2.0                  0.0

[2 rows x 20 columns]
04:14:30 PM
clean-2c6af9f6-0
columns: VendorID                        float64
lpep_pickup_datetime     datetime64[ns]
lpep_dropoff_datetime    datetime64[ns]
store_and_fwd_flag               object
RatecodeID                      float64
PULocationID                      int64
DOLocationID                      int64
passenger_count                 float64
trip_distance                   float64
fare_amount                     float64
extra                           float64
mta_tax                         float64
tip_amount                      float64
tolls_amount                    float64
ehail_fee                       float64
improvement_surcharge           float64
total_amount                    float64
payment_type                    float64
trip_type                       float64
congestion_surcharge            float64
dtype: object
04:14:30 PM
clean-2c6af9f6-0
rows: 447770
04:14:30 PM
clean-2c6af9f6-0
Finished in state Completed()
04:14:30 PM
clean-2c6af9f6-0
Created task run 'write_local-09e9d2b8-0' for task 'write_local'
04:14:30 PM
Executing 'write_local-09e9d2b8-0' immediately...
04:14:30 PM
Finished in state Completed()
04:14:31 PM
write_local-09e9d2b8-0
Created task run 'write_gcs-67f8f48e-0' for task 'write_gcs'
04:14:31 PM
Executing 'write_gcs-67f8f48e-0' immediately...
04:14:31 PM
Getting bucket 'dtc_data_lake_dtc-de-course-368906'.
04:14:31 PM
write_gcs-67f8f48e-0
Uploading from PosixPath('data/green/green_tripdata_2020-01.parquet') to the bucket 'dtc_data_lake_dtc-de-course-368906' path 'data/green/green_tripdata_2020-01.parquet'.
04:14:32 PM
write_gcs-67f8f48e-0
Finished in state Completed()
04:14:34 PM
write_gcs-67f8f48e-0
Finished in state Completed('All states completed.')
04:14:34 PM
```
# Question 2. Scheduling with Cron

`prefect deployment build -a hw_etl_web_to_gcs.py:etl_web_to_gcs -n "hw_flow_1" --cron "0 5 1 * *"`     

# Question 3. Loading data to BigQuery

`prefect deployment build -a hw_etl_gcs_to_bq.py:etl_bq_parent_flow -n "hw_flow_3""`   

`prefect deployment run etl-bq-parent-flow/hw_flow_3 -p "color=yellow" -p "year=2019" -p "months=[2,3]"`    

Logs:
```
Downloading flow code from storage at '/Users/peter/DE_zoomcamp/w2_workflow_orchestration/prefect'
02:00:47 PM
Created subflow run 'quirky-adder' for flow 'etl-gcs-to-bq'
02:00:47 PM
Created subflow run 'fierce-chamois' for flow 'etl-gcs-to-bq'
02:02:07 PM
Created task run 'bigquery_query-28c346fe-0' for task 'bigquery_query'
02:03:39 PM
Executing 'bigquery_query-28c346fe-0' immediately...
02:03:39 PM
Running BigQuery query
02:03:39 PM
bigquery_query-28c346fe-0
Finished in state Completed()
02:03:44 PM
bigquery_query-28c346fe-0
[Row((14851920,), {'f0_': 0})]
02:03:44 PM
Finished in state Completed('All states completed.')
02:03:44 PM
```
# Question 4. Github Storage Block

`prefect deployment build -n "hw_flow_4" -sb github/ulanliu w2_workflow_orchestration/prefect/flows/03_homework/hw_etl_web_to_gcs.py:etl_parent_flow --apply`

Logs:
```
Created task run 'fetch-ba00c645-0' for task 'fetch'
08:50:52 AM
Executing 'fetch-ba00c645-0' immediately...
08:50:52 AM
Finished in state Completed()
08:50:54 AM
fetch-ba00c645-0
Created task run 'clean-2c6af9f6-0' for task 'clean'
08:50:54 AM
Executing 'clean-2c6af9f6-0' immediately...
08:50:54 AM
   VendorID lpep_pickup_datetime  ... trip_type congestion_surcharge
0       2.0  2020-11-01 00:08:23  ...       1.0                 2.75
1       2.0  2020-11-01 00:23:32  ...       1.0                 0.00

[2 rows x 20 columns]
08:50:55 AM
clean-2c6af9f6-0
columns: VendorID                        float64
lpep_pickup_datetime     datetime64[ns]
lpep_dropoff_datetime    datetime64[ns]
store_and_fwd_flag               object
RatecodeID                      float64
PULocationID                      int64
DOLocationID                      int64
passenger_count                 float64
trip_distance                   float64
fare_amount                     float64
extra                           float64
mta_tax                         float64
tip_amount                      float64
tolls_amount                    float64
ehail_fee                       float64
improvement_surcharge           float64
total_amount                    float64
payment_type                    float64
trip_type                       float64
congestion_surcharge            float64
dtype: object
08:50:55 AM
clean-2c6af9f6-0
rows: 88605
08:50:55 AM
clean-2c6af9f6-0
Finished in state Completed()
08:50:55 AM
clean-2c6af9f6-0
Created task run 'write_local-09e9d2b8-0' for task 'write_local'
08:50:55 AM
Executing 'write_local-09e9d2b8-0' immediately...
08:50:55 AM
Finished in state Completed()
08:50:55 AM
write_local-09e9d2b8-0
Created task run 'write_gcs-67f8f48e-0' for task 'write_gcs'
08:50:55 AM
Executing 'write_gcs-67f8f48e-0' immediately...
08:50:55 AM
Getting bucket 'dtc_data_lake_dtc-de-course-368906'.
08:50:55 AM
write_gcs-67f8f48e-0
Uploading from PosixPath('data/green/green_tripdata_2020-11.parquet') to the bucket 'dtc_data_lake_dtc-de-course-368906' path 'data/green/green_tripdata_2020-11.parquet'.
08:50:56 AM
write_gcs-67f8f48e-0
Finished in state Completed()
08:50:56 AM
write_gcs-67f8f48e-0
Finished in state Completed('All states completed.')
```
# Question 5. Email or Slack notifications

Logs:
```
Created task run 'fetch-ba00c645-0' for task 'fetch'
11:46:40 AM
Executing 'fetch-ba00c645-0' immediately...
11:46:40 AM
Finished in state Completed()
11:46:43 AM
fetch-ba00c645-0
Created task run 'clean-2c6af9f6-0' for task 'clean'
11:46:43 AM
Executing 'clean-2c6af9f6-0' immediately...
11:46:43 AM
   VendorID lpep_pickup_datetime  ... trip_type congestion_surcharge
0         2  2019-04-01 00:18:40  ...         1                 2.75
1         2  2019-04-01 00:18:24  ...         1                 0.00

[2 rows x 20 columns]
11:46:44 AM
clean-2c6af9f6-0
columns: VendorID                          int64
lpep_pickup_datetime     datetime64[ns]
lpep_dropoff_datetime    datetime64[ns]
store_and_fwd_flag               object
RatecodeID                        int64
PULocationID                      int64
DOLocationID                      int64
passenger_count                   int64
trip_distance                   float64
fare_amount                     float64
extra                           float64
mta_tax                         float64
tip_amount                      float64
tolls_amount                    float64
ehail_fee                       float64
improvement_surcharge           float64
total_amount                    float64
payment_type                      int64
trip_type                         int64
congestion_surcharge            float64
dtype: object
11:46:44 AM
clean-2c6af9f6-0
rows: 514392
11:46:44 AM
clean-2c6af9f6-0
Finished in state Completed()
11:46:44 AM
clean-2c6af9f6-0
Created task run 'write_local-09e9d2b8-0' for task 'write_local'
11:46:44 AM
Executing 'write_local-09e9d2b8-0' immediately...
11:46:44 AM
Finished in state Completed()
11:46:46 AM
write_local-09e9d2b8-0
Created task run 'write_gcs-67f8f48e-0' for task 'write_gcs'
11:46:46 AM
Executing 'write_gcs-67f8f48e-0' immediately...
11:46:46 AM
Getting bucket 'dtc_data_lake_dtc-de-course-368906'.
11:46:46 AM
write_gcs-67f8f48e-0
Uploading from PosixPath('data/green/green_tripdata_2019-04.parquet') to the bucket 'dtc_data_lake_dtc-de-course-368906' path 'data/green/green_tripdata_2019-04.parquet'.
11:46:46 AM
write_gcs-67f8f48e-0
Finished in state Completed()
11:46:48 AM
write_gcs-67f8f48e-0
Finished in state Completed('All states completed.')
```

> Prefect flow run notification  
> Flow run etl-parent-flow/sceptical-dalmatian entered state Completed at 2023-02-06T03:46:48.452304+00:00.  
> Flow ID: 6ca87494-e422-45b9-ace6-fc9fbbc9e999  
> Flow run ID: 8b0a8ad9-dcc3-4d02-8421-48b848f8010c  
> Flow run URL: http://127.0.0.1:4200/flow-runs/flow-run/8b0a8ad9-dcc3-4d02-8421-48b848f8010c  
> State message: All states completed.  
> Prefect NotificationsPrefect Notifications |  11:46  
