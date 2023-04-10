> This repository records the studying progress of Data Engineering Zoomcamp

## [Week 1: Introduction & Prerequisites](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_1_basics_n_setup)
  
In the first week, I set up the PostgreSQL and PGadmin via Docker Compose and build a simple data pipeline ingesting the NYC taxi data into PostgreSQL, and use PGadmin to explore the data. Also, I learn how to set up the virtual machine at Google Cloud Platform (GCP) and connect with local network via ssh and manage GCP services via Terraform.
  
## [Week 2: Workflow Orchestration](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_2_workflow_orchestration)

In the second week, the courses are focusing on work orchestration. There are many workflow orchestration tools, and Airflow is the most famous one which 2022 DE-zoomcamp used. However, 2023 DE-zoomcamp decided to use Prefect instead of Airflow. The main reason is getting started with Airflow is a challenge for many beginners and I was one of them. I did complete the courses with Airflow, but I spent a lot of time on setting up the Airflow environment. Compared to Airflow, Prefect is more lightweight and easy to set up. The flaw is Prefect is relatively new product and this means it's more difficult to find someone who has done a blog that answers your question. But I think the Prefect community will help you.
Below is the article talking about Airflow vs Prefect:
https://lnkd.in/gGxj99a2
  
Week 2 Recap:
- Prefect concept
- Builds ETL python scripts to load data into Google Cloud storage  and Google BigQuery with Prefect
- Build parameterized flows and create deployments
- Deploy flows remotely by Github Storage Block
- Create slack Notifications and connect to personal slack

## [Week 3: Data Warehouse](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_3_data_warehouse)
  
In the third week, DEzoomcamp is focusing on data warehouse. There are several data warehouse options such as Google BigQuery, Amazon Redshift, Azure Synapse Analytics, etc. The course chose BigQuery. 
I load the NYC taxi data from data lake which is google cloud storage to BigQuery, and create non-partitioned, partitioned, clustered tables for testing the query performance.

Week 3 Recap:
- Partitioning and Clustering
- BigQuery Best Practices
- Internals of Big Query
  
## [Week 4: Analytics Engineering](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_4_analytics_engineering)

This week is about analytics engineering, which is willing to fill the gap between data engineer and data analyst/data scientist. Data analysts or data scientists can use data modeling tools like dbt (data build tool) or Dataform to transform the data using SQL. This course is focusing on dbt. dbt is a SQL-first transform workflow that works on data warehouse, so it is fit for ELT (Extract-Load-Transform). With ELT, we can avoid the data missing in the ETL process.

Week 4 Recap:
• dbt core
• dbt cloud
• Data modeling
• ETL vs ELT
• Looker

## [Week 5: Batch processing](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_5_batch_processing)
  
Week 5 Recap:
• Batch processing
• Spark
• Spark Dataframes
• Spark SQL
• Internals: GroupBy and joins
  

## [Week 6: Streaming](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_5_batch_processing)
  
Week 6 Recap:
• Introduction to Kafka
• Schemas (avro)
• Kafka Streams
• Kafka Connect and KSQL

## [Week 7: Course Project](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_7_project)

Comparison between Covid-19 and Monkeypox Cases: https://github.com/ulanliu/Covid_n_Monkeypox

This project is related to covid-19 and monkeypox diseases. ​​Which area has the highest prevalence rate? Does a high covid-19 prevalence rate area also have a high monkeypox prevalence rate? How is the case fatality rate between covid-19 and monkeypox?

In this project, I build an end-to-end data pipeline via prefect, extract data from owid, load data to gcs and bigquery, transform via dbt and then visualize data by Looker.
