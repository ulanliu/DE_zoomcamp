{{ config(materialized='table') }}

WITH fhv_table_2019 AS (
    SELECT * FROM {{ ref('stg_fhv_tripdata') }}
),

zone_lookup AS (
    SELECT * FROM {{ ref('dim_zone') }}
    WHERE Borough != 'Unknown'
)

SELECT f.dispatching_base_num,
    f.pickup_datetime,
    f.pickup_locationid,
    p.Borough AS pickup_borough,
    p.Zone AS pickup_zone,
    p.service_zone AS pickup_service_zone,
    f.dropoff_datetime,
    f.dropoff_locationid,
    d.Borough AS dropoff_borough,
    d.Zone AS dropoff_zone,
    d.service_zone AS dropoff_service_zone,
    f.sr_flag,
    f.affiliated_base_number

FROM fhv_table_2019 as f
INNER JOIN zone_lookup as p
ON f.pickup_locationid = p.LocationID
INNER JOIN zone_lookup as d
ON f.dropoff_locationid = d.LocationID

{% if var('is_test_run', default=true) %}

limit 100

{% endif %}