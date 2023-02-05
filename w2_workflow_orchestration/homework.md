# Question 1. Load January 2020 data
   
``prefect deployment build -a hw_etl_web_to_gcs.py:etl_web_to_gcs -n "hw_flow_1"``     
   
`prefect deployment run etl-web-to-gcs/hw_flow_1 -p "color=green" -p "year=2020" -p "month=1"`   

# Question 2. Scheduling with Cron

``prefect deployment build -a hw_etl_web_to_gcs.py:etl_web_to_gcs -n "hw_flow_1" --cron "0 5 1 * *"``     

# Question 3. Loading data to BigQuery

``prefect deployment build -a hw_etl_gcs_to_bq.py:etl_bq_parent_flow -n "hw_flow_3""``   

``prefect deployment run etl-bq-parent-flow/hw_flow_3 -p "color=yellow" -p "year=2019" -p "months=[2,3]"``    