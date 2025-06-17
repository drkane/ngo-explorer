SELECT
    'GB-CHC-' || cc.registered_charity_number AS charity_id,
    jsonb_agg(
        jsonb_build_object('id', cc.classification_code)
    ) FILTER (
        WHERE
            classification_type = 'How'
    ) AS operations,
    jsonb_agg(
        jsonb_build_object('id', cc.classification_code)
    ) FILTER (
        WHERE
            classification_type = 'What'
    ) AS causes,
    jsonb_agg(
        jsonb_build_object('id', cc.classification_code)
    ) FILTER (
        WHERE
            classification_type = 'Who'
    ) AS beneficiaries
FROM
    charity_ccewcharityclassification cc
WHERE 'GB-CHC-' || cc.registered_charity_number = ANY(%(charity_ids)s)
GROUP BY
    1