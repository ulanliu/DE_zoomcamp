{{ config(materialized='view') }}

with tripdata as (
  SELECT *,
    row_number() OVER (PARTITION BY vendorid, tpep_pickup_datetime) AS rn
  FROM {{ source('staging', 'yellow_taxi_2019_2020') }}
  WHERE vendorid IS NOT NULL
)

SELECT 
    -- identifiers
    {{ dbt_utils.surrogate_key(['vendorid', 'tpep_pickup_datetime'])}} as trip_id,
    cast(vendorid as integer) as vendorid,
    cast(ratecodeid as numeric) as ratecodeid,
    cast(pulocationid as integer) as  pickup_locationid,
    cast(dolocationid as integer) as dropoff_locationid,
    -- timestamps
    cast(tpep_pickup_datetime as timestamp) as pickup_datetime,
    cast(tpep_dropoff_datetime as timestamp) as dropoff_datetime,
    
    -- trip info
    store_and_fwd_flag,
    cast(passenger_count as integer) as passenger_count,
    cast(trip_distance as numeric) as trip_distance,

    -- payment info
    cast(fare_amount as numeric) as fare_amount,
    cast(extra as numeric) as extra,
    cast(mta_tax as numeric) as mta_tax,
    cast(tip_amount as numeric) as tip_amount,
    cast(tolls_amount as numeric) as tolls_amount,
    cast(0 as numeric) as ehail_fee,
    -- cast(airport_fee as numeric) as airport_fee,
    cast(improvement_surcharge as numeric) as improvement_surcharge,
    cast(total_amount as numeric) as total_amount,
    cast(payment_type as integer) as payment_type,
    {{ get_payment_type_description('payment_type')}} as get_payment_type_description,
    cast(congestion_surcharge as numeric) as congestion_surcharge

FROM tripdata
WHERE rn = 1

{% if var('is_test_run', default=true) %}

  LIMIT 100

{% endif %}