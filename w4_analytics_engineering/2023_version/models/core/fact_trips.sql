{{ config(materialized='table') }}

WITH green_data AS (
    SELECT *,
        'Green' AS service_type
    from {{ ref('stg_green_tripdata') }}
),

yellow_data AS (
    SELECT *,
        'Yellow' AS service_type
    from {{ ref('stg_yellow_tripdata') }}
),

trips_unioned AS (
    SELECT * FROM green_data
    UNION ALL
    SELECT * FROM yellow_data
),

dim_zones AS (
    SELECT * FROM {{ ref('dim_zone') }}
    WHERE Borough != 'Unknown'
)

SELECT 
    trips_unioned.trip_id, 
    trips_unioned.vendorid, 
    trips_unioned.service_type,
    trips_unioned.ratecodeid, 
    trips_unioned.pickup_locationid, 
    pickup_zone.borough as pickup_borough, 
    pickup_zone.zone as pickup_zone, 
    trips_unioned.dropoff_locationid,
    dropoff_zone.borough as dropoff_borough, 
    dropoff_zone.zone as dropoff_zone,  
    trips_unioned.pickup_datetime, 
    trips_unioned.dropoff_datetime, 
    trips_unioned.store_and_fwd_flag, 
    trips_unioned.passenger_count, 
    trips_unioned.trip_distance, 
    -- trips_unioned.trip_type, 
    trips_unioned.fare_amount, 
    trips_unioned.extra, 
    trips_unioned.mta_tax, 
    trips_unioned.tip_amount, 
    trips_unioned.tolls_amount, 
    trips_unioned.ehail_fee, 
    trips_unioned.improvement_surcharge, 
    trips_unioned.total_amount, 
    trips_unioned.payment_type, 
    trips_unioned.payment_type_description, 
    trips_unioned.congestion_surcharge
FROM trips_unioned
INNER JOIN dim_zones AS pickup_zone
ON trips_unioned.pickup_locationid = pickup_zone.locationid
INNER JOIN dim_zones AS dropoff_zone
ON trips_unioned.dropoff_locationid = dropoff_zone.locationid