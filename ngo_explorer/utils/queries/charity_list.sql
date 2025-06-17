WITH "all_names" AS (
    SELECT
        charity_id,
        coalesce(
            jsonb_agg(
                jsonb_build_object('value', n.name, 'primary', false)
            ) FILTER (
                WHERE
                    upper(c.name) != upper(n.name)
            ),
            jsonb_build_array()
        ) AS all_names
    FROM
        charity_charity c
        INNER JOIN charity_charityname n ON c.id = n.charity_id
    GROUP BY
        1
),
"countries" AS (
    SELECT
        org_id AS charity_id,
        jsonb_agg(geo_iso) fILTER(
            WHERE
                geo_iso not in ('GB', 'GG', 'JE', 'IM')
        ) AS countries,
        count(*) fILTER(
            WHERE
                geo_iso not in ('GB', 'GG', 'JE', 'IM')
        ) AS countries_n
    FROM
        ftc_organisationlocation l
    GROUP BY
        1
)
SELECT
    replace(id, 'GB-CHC-', '') AS id,
    "name" AS name,
    jsonb_build_array(
        jsonb_build_object('value', name, 'primary', true)
    ) AS names,
    jsonb_build_array(
        jsonb_build_object('value', name, 'primary', true)
    ) || all_names.all_names AS all_names,
    c.activities AS activities,
    jsonb_build_array() AS areas,
    jsonb_build_array(
        jsonb_build_object(
            'income',
            c.income,
            'spending',
            c.spending,
            'financialYear',
            jsonb_build_object(
                'end',
                c.latest_fye
            )
        )
    ) AS finances,
    jsonb_build_array() AS all_finances,
    CASE
        WHEN c.company_number IS NOT NULL THEN jsonb_build_array(
            jsonb_build_object('id', id),
            jsonb_build_object('id', 'GB-COH-' || c.company_number)
        )
        ELSE jsonb_build_array(jsonb_build_object('id', id))
    END AS orgIds,
    jsonb_build_array() AS operations,
    jsonb_build_array() AS causes,
    jsonb_build_array() AS beneficiaries,
    NULL AS geo,
    jsonb_build_array(
        jsonb_build_object(
            'registrationDate',
            c.date_registered,
            'removalDate',
            c.date_removed
        )
    ) AS registrations,
    c.web AS website,
    jsonb_build_object(
        'email',
        c.email,
        'address',
        c.address,
        'phone',
        c.phone,
        'postcode',
        c.postcode
    ) AS contact,
    jsonb_build_object(
        'trustees',
        c.trustees,
        'volunteers',
        c.volunteers,
        'employees',
        c.employees
    ) AS "numPeople",
    c.constitution AS "governingDoc",
    c.geographical_spread AS "areaOfBenefit",
    "countries"."countries" AS "countries"
FROM
    charity_charity c
    LEFT OUTER JOIN "all_names" ON c.id = "all_names".charity_id
    LEFT OUTER JOIN "countries" ON c.id = "countries".charity_id
WHERE
    c."source" = 'ccew'
    AND c."active"
    AND "countries".countries_n > 0