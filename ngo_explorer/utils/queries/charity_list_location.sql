SELECT
    org_id AS charity_id,
    jsonb_build_object(
        'latitude',
        NULL,
        'longitude',
        NULL,
        'region',
        NULL,
        'country',
        NULL,
        'admin_county',
        NULL,
        'admin_district',
        NULL,
        'admin_ward',
        NULL,
        'lsoa',
        NULL,
        'msoa',
        NULL,
        'parliamentary_constituency',
        NULL,
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
            NULL,
            'parliamentary_constituency',
            l.geo_pcon,
            'lsoa',
            NULL,
            'msoa',
            NULL
        )
    ) AS geo
FROM
    ftc_organisationlocation l
WHERE
    l."locationType" = 'HQ'
    AND l.org_id = ANY(%(charity_ids)s)