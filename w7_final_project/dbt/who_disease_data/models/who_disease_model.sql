{{ config(materialized='table') }}

{%- set cols = adapter.get_columns_in_relation(source('staging', 'monkeypox')) -%}

WITH monkeypox AS (
    SELECT
        {% for col in cols %}
            monkeypox.{{col.name}} AS monkeypox_{{col.name}},
        {% endfor %}
    FROM {{ source('staging', 'monkeypox') }}
),

covid_19 AS (
    SELECT 
        location,
        iso_code,
        date,
        total_cases,
        total_deaths,
        new_cases,
        new_deaths,
        new_cases_smoothed,
        new_deaths_smoothed,
        new_cases_per_million,
        total_cases_per_million,
        new_cases_smoothed_per_million,
        new_deaths_per_million,
        total_deaths_per_million,
        new_deaths_smoothed_per_million
    FROM {{ source('staging', 'covid-19') }}
)

SELECT * 
FROM covid_19 AS c
LEFT JOIN monkeypox AS m
    ON c.iso_code = m.monkeypox_iso_code AND c.date = m.monkeypox_date

