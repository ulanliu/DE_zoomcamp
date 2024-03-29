{{ config(materialized='table') }}

WITH green_taxi_2019 AS (
    SELECT * FROM {{ source('staging', 'green_taxi_2019') }}
),

green_taxi_2020 AS (
    SELECT cast(vendorid as integer) as vendorid, * EXCEPT(vendorid) FROM {{ source('staging', 'green_taxi_2020') }}
),

green_taxi_2019_2020 AS (
    SELECT * FROM green_taxi_2019
    UNION ALL
    SELECT * FROM green_taxi_2020
),

tripdata AS (
  SELECT *,
    row_number() OVER (PARTITION BY vendorid, lpep_pickup_datetime) AS rn
  FROM green_taxi_2019_2020
  WHERE vendorid IS NOT NULL
)

select
    -- identifiers
    {{ dbt_utils.surrogate_key(['vendorid', 'lpep_pickup_datetime']) }} as trip_id,
    cast(vendorid as integer) as vendorid,
    cast(ratecodeid as numeric) as ratecodeid,
    cast(pulocationid as integer) as  pickup_locationid,
    cast(dolocationid as integer) as dropoff_locationid,
    
    -- timestamps
    cast(lpep_pickup_datetime as timestamp) as pickup_datetime,
    cast(lpep_dropoff_datetime as timestamp) as dropoff_datetime,
    
    -- trip info
    store_and_fwd_flag,
    cast(passenger_count as integer) as passenger_count,
    cast(trip_distance as numeric) as trip_distance,
    -- cast(trip_type as integer) as trip_type,
    
    -- payment info
    cast(fare_amount as numeric) as fare_amount,
    cast(extra as numeric) as extra,
    cast(mta_tax as numeric) as mta_tax,
    cast(tip_amount as numeric) as tip_amount,
    cast(tolls_amount as numeric) as tolls_amount,
    cast(ehail_fee as numeric) as ehail_fee,
    cast(improvement_surcharge as numeric) as improvement_surcharge,
    cast(total_amount as numeric) as total_amount,
    cast(payment_type as integer) as payment_type,
    cast(congestion_surcharge as numeric) as congestion_surcharge,
    {{ get_payment_type_description('payment_type') }} as payment_type_description
    
from tripdata
where rn = 1

-- dbt build --m <model.sql> --var 'is_test_run: false'
{% if var('is_test_run', default=true) %}

  limit 100

{% endif %}