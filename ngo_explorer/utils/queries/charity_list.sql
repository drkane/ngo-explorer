WITH classification AS (
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
    GROUP BY
        1
),
"location" AS (
    SELECT
        org_id AS charity_id,
        jsonb_build_object(
            'latitude',
            l.geo_lat,
            'longitude',
            l.geo_long,
            'region',
            rgn."name",
            'country',
            ctry."name",
            'admin_county',
            cty."name",
            'admin_district',
            laua."name",
            'admin_ward',
            ward."name",
            'lsoa',
            lsoa."name",
            'msoa',
            msoa."name",
            'parliamentary_constituency',
            pcon."name",
            'codes',
            jsonb_build_object(
                'region',
                l.geo_rgn,
                'country',
                l.geo_ctry,
                'admin_county',
                l.geo_cty,
                'admin_district',
                l.geo_laua,
                'admin_ward',
                l.geo_ward,
                'parliamentary_constituency',
                l.geo_pcon,
                'lsoa',
                l.geo_lsoa21,
                'msoa',
                l.geo_msoa21
            )
        ) AS geo
    FROM
        ftc_organisationlocation l
        LEFT OUTER JOIN geo_geolookup ctry ON l.geo_ctry = ctry."geoCode"
        LEFT OUTER JOIN geo_geolookup rgn ON l.geo_rgn = rgn."geoCode"
        LEFT OUTER JOIN geo_geolookup cty ON l.geo_cty = cty."geoCode"
        LEFT OUTER JOIN geo_geolookup laua ON l.geo_laua = laua."geoCode"
        LEFT OUTER JOIN geo_geolookup ward ON l.geo_ward = ward."geoCode"
        LEFT OUTER JOIN geo_geolookup pcon ON l.geo_pcon = pcon."geoCode"
        LEFT OUTER JOIN geo_geolookup lsoa ON l.geo_lsoa21 = ward."geoCode"
        LEFT OUTER JOIN geo_geolookup msoa ON l.geo_msoa21 = pcon."geoCode"
    WHERE
        l."locationType" = 'HQ'
),
"areas" AS (
    SELECT
        charity_id,
        jsonb_agg(
            jsonb_build_object(
                'name',
                aoo.aooname,
                'id',
                aoo.aootype || '-' || aoo.aookey
            )
        ) AS areas
    FROM
        charity_charity_areas_of_operation caoo
        INNER JOIN charity_areaofoperation aoo ON caoo.areaofoperation_id = aoo.id
    GROUP BY
        1
),
"all_finances" AS (
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
    GROUP BY
        1
),
"all_names" AS (
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
                geo_iso <> 'GB'
        ) AS countries,
        count(*) fILTER(
            WHERE
                geo_iso <> 'GB'
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
    COALESCE(areas.areas, jsonb_build_array()) AS areas,
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
    COALESCE(all_finances.all_finances, jsonb_build_array()) AS all_finances,
    CASE
        WHEN c.company_number IS NOT NULL THEN jsonb_build_array(
            jsonb_build_object('id', id),
            jsonb_build_object('id', 'GB-COH-' || c.company_number)
        )
        ELSE jsonb_build_array(jsonb_build_object('id', id))
    END AS orgIds,
    COALESCE(classification.operations, jsonb_build_array()) AS operations,
    COALESCE(classification.causes, jsonb_build_array()) AS causes,
    COALESCE(
        classification.beneficiaries,
        jsonb_build_array()
    ) AS beneficiaries,
    "location".geo AS geo,
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
    ) AS contacts,
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
    LEFT OUTER JOIN classification ON c.id = classification.charity_id
    LEFT OUTER JOIN "location" ON c.id = "location".charity_id
    LEFT OUTER JOIN "areas" ON c.id = "areas".charity_id
    LEFT OUTER JOIN "all_finances" ON c.id = "all_finances".charity_id
    LEFT OUTER JOIN "all_names" ON c.id = "all_names".charity_id
    LEFT OUTER JOIN "countries" ON c.id = "countries".charity_id
WHERE
    c."source" = 'ccew'
    AND c."active"
    AND "countries".countries_n > 0