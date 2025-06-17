SELECT
    org_id AS charity_id,
    jsonb_build_object(
        'latitude',
        l.geo_lat,
        'longitude',
        l.geo_long,
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
WHERE
    l."locationType" = 'HQ'
    AND l.org_id = ANY(%(charity_ids)s)