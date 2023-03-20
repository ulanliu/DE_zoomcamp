{{ config(materialized='view') }}

{%- set cols = adapter.get_columns_in_relation(source('staging', 'monkeypox')) -%}

WITH monkeypox AS (
    SELECT
        {% for col in cols %}
            monkeypox.{{col.name}} AS monkeypox_{{col.name}},
        {% endfor %}
    FROM {{ source('staging', 'monkeypox') }}
),

covid_19 AS (
    SELECT * FROM {{ source('staging', 'covid-19') }}
)

SELECT * 
FROM covid_19 AS c
LEFT JOIN monkeypox AS m
    ON c.iso_code = m.monkeypox_iso_code AND c.date = m.monkeypox_date
LIMIT 1000
