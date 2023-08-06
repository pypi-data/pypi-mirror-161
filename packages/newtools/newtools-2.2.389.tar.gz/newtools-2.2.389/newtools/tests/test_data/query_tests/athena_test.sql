WITH dates AS
(
SELECT current_date as dt, CAST(current_date as varchar) as day)
SELECT *
FROM dates
WHERE day in {day_list}

