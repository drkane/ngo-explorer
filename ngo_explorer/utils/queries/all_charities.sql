SELECT
    CASE
        WHEN c.spending >= 1000000000 THEN 9
        WHEN c.spending >= 316227766 THEN 8.5
        WHEN c.spending >= 100000000 THEN 8
        WHEN c.spending >= 31622777 THEN 7.5
        WHEN c.spending >= 10000000 THEN 7
        WHEN c.spending >= 3162278 THEN 6.5
        WHEN c.spending >= 1000000 THEN 6
        WHEN c.spending >= 316228 THEN 5.5
        WHEN c.spending >= 100000 THEN 5
        WHEN c.spending >= 31623 THEN 4.5
        WHEN c.spending >= 10000 THEN 4
        WHEN c.spending >= 3162 THEN 3.5
        WHEN c.spending >= 1000 THEN 3
        WHEN c.spending >= 316 THEN 2.5
        WHEN c.spending >= 100 THEN 2
        WHEN c.spending >= 32 THEN 1.5
        WHEN c.spending >= 10 THEN 1
        WHEN c.spending >= 3 THEN 0.5
        WHEN c.spending >= 1 THEN 0
        ELSE NULL
    END AS key,
    CASE
        WHEN c.spending >= 1000000000 THEN 'Min. £1000000000'
        WHEN c.spending >= 316227766 THEN 'Min. £316227766'
        WHEN c.spending >= 100000000 THEN 'Min. £100000000'
        WHEN c.spending >= 31622777 THEN 'Min. £31622777'
        WHEN c.spending >= 10000000 THEN 'Min. £10000000'
        WHEN c.spending >= 3162278 THEN 'Min. £3162278'
        WHEN c.spending >= 1000000 THEN 'Min. £1000000'
        WHEN c.spending >= 316228 THEN 'Min. £316228'
        WHEN c.spending >= 100000 THEN 'Min. £100000'
        WHEN c.spending >= 31623 THEN 'Min. £31623'
        WHEN c.spending >= 10000 THEN 'Min. £10000'
        WHEN c.spending >= 3162 THEN 'Min. £3162'
        WHEN c.spending >= 1000 THEN 'Min. £1000'
        WHEN c.spending >= 316 THEN 'Min. £316'
        WHEN c.spending >= 100 THEN 'Min. £100'
        WHEN c.spending >= 32 THEN 'Min. £32'
        WHEN c.spending >= 10 THEN 'Min. £10'
        WHEN c.spending >= 3 THEN 'Min. £3'
        WHEN c.spending >= 1 THEN 'Min. £1'
        ELSE NULL
    END AS name,
    count(*) AS count,
    sum(c.spending) AS sum
FROM
    charity_charity c
WHERE
    c.active
    AND c."source" = 'ccew'
GROUP BY
    1,
    2
ORDER BY
    1