{{ config(materialized='table') }}

SELECT LocationID,
    Borough,
    Zone,
    replace(service_zone, 'Boro', 'Green') as service_zone
FROM {{ ref('taxi_zone_lookup') }}