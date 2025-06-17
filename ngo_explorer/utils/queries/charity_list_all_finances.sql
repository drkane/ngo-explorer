SELECT
    charity_id,
    jsonb_agg(
        jsonb_build_object(
            'income',
            c.income,
            'spending',
            c.spending,
            'financialYear',
            jsonb_build_object('end', c.fyend)
        )
        ORDER BY
            c.fyend DESC
    ) AS all_finances
FROM
    charity_charityfinancial c
WHERE charity_id = ANY(%(charity_ids)s)
GROUP BY
    1