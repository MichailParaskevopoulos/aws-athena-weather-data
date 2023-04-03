"""
    SQL queries used to get the data from the Athena table
"""

QUERY_1 = """
SELECT
    MAX(max_temp_c) AS max_temp_c,
    MIN(min_temp_c) AS min_temp_c
FROM weather_data
WHERE 
    year = {year_0}
"""

QUERY_2 = """
WITH cte_year AS (
	SELECT
		year,
		AVG(mean_temp_c) AS avg_temp
	FROM weather_data
	GROUP BY year
),

rolling_avg AS (
    SELECT
        year,
        avg_temp,
        AVG(avg_temp) OVER (
            ORDER BY year
            ROWS BETWEEN 2 PRECEDING AND 1 PRECEDING
        ) avg_temp_past_two_years
    FROM cte_year a
)

SELECT
    100.0 * ABS(avg_temp - avg_temp_past_two_years) / avg_temp_past_two_years AS pct_diff
FROM rolling_avg
WHERE
    year = {year_0}
"""

QUERY_3 = """
WITH temp_year AS (
    SELECT
        year,
        AVG(mean_temp_c) AS mean_temp_year
    FROM weather_data
    WHERE
        year = {year_0}
    GROUP BY
        year
),

temp_month AS (
    SELECT
        year,
        month,
        AVG(mean_temp_c) AS mean_temp_month
    FROM weather_data
    WHERE
        year = {year_0}
    GROUP BY
        year, month
)

SELECT 
    month,
    100.0 * ABS(mean_temp_month - mean_temp_year) / mean_temp_year AS pct_diff_year,
    mean_temp_month - LAG(mean_temp_month) OVER (
        PARTITION BY year
        ORDER BY month
    ) AS diff_month_lag
FROM temp_month
LEFT JOIN temp_year
    USING(year)
ORDER BY
    month
"""