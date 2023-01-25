-- Question 3
SELECT COUNT(*) FROM green_taxi_2019_trips
WHERE lpep_pickup_datetime::date = '2019-01-15'
AND lpep_dropoff_datetime::date = '2019-01-15';

-- Question 4
SELECT trip_distance, lpep_pickup_datetime AS date FROM green_taxi_2019_trips
ORDER BY 1 DESC
LIMIT 2;

-- Question 5
SELECT passenger_count, COUNT(*) FROM green_taxi_2019_trips
WHERE lpep_pickup_datetime::date = '2019-01-01'
GROUP BY 1;

--Question 6
SELECT tip_amount, tp."Zone", td."Zone"
FROM green_taxi_2019_trips g
LEFT JOIN taxi_zone_lookup tp
	ON g."PULocationID" = tp."LocationID"
LEFT JOIN taxi_zone_lookup AS td
	ON g."DOLocationID" = td."LocationID"
WHERE tp."Zone" = 'Astoria'
ORDER BY 1 DESC
LIMIT 2;