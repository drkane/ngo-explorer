SELECT
    charity_id,
    jsonb_agg(
        jsonb_build_object(
            'name',
            aoo.aooname,
            'id',
            aoo."GSS"
        )
    ) AS areas
FROM
    charity_charity_areas_of_operation caoo
    INNER JOIN charity_areaofoperation aoo ON caoo.areaofoperation_id = aoo.id
WHERE aoo."GSS" IS NOT NULL
    AND aoo.aootype IS NULL
    AND charity_id = ANY(%(charity_ids)s)
GROUP BY
    1