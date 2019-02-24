DOWNLOAD_OPTIONS = {
    "main": {
        "options": [
            {'label': 'Charity number', 'value': 'ids.GB-CHC', 'checked': True},
            {'label': 'Charity name', 'value': 'name', 'checked': True},
            {'label': 'Governing document', 'value': 'governingDoc'},
            {'label': 'Description of activities',
             'value': 'activities'},
            {'label': 'Charitable objects', 'value': 'objectives'},
            {'label': 'Causes served', 'value': 'causes'},
            {'label': 'Beneficiaries', 'value': 'beneficiaries'},
            {'label': 'Activities', 'value': 'operations'},
        ],
        "name": "Charity information"
    },
    "financial": {
        "options": [
            {'label': 'Latest income', 'value': 'income.latest.total', 'checked': True},
            {'label': 'Company number', 'value': 'companiesHouseNumber'},
            {'label': 'Financial year end', 'value': 'fyend'},
            {'label': 'Number of trustees',
             'value': 'people.trustees'},
            {'label': 'Number of employees',
             'value': 'people.employees'},
            {'label': 'Number of volunteers',
             'value': 'people.volunteers'},
        ],
        "name": "Financial"
    },
    "contact": {
        "options": [
            {'label': 'Email', 'value': 'contact.email'},
            {'label': 'Address', 'value': 'contact.address'},
            {'label': 'Postcode', 'value': 'contact.postcode'},
            {'label': 'Phone number', 'value': 'contact.phone'},
        ],
        "name": "Contact details"
    },
    "geo": {
        "options": {
            "aoo": [
                {'label': 'Description of area of benefit', 'value': 'areaOfBenefit'},
                {'label': 'Area of operation',
                 'value': 'areasOfOperation'},
                {'label': 'Countries where this charity operates',
                 'value': 'countries'},
            ],
            "geo": [
                {'label': 'Country', 'value': 'contact.geo.country'},
                {'label': 'Region', 'value': 'contact.geo.region'},
                {'label': 'County', 'value': 'contact.geo.admin_county'},
                {'label': 'County [code]',
                 'value': "contact.geo.codes.admin_county"},
                {'label': 'Local Authority',
                 'value': 'contact.geo.admin_district'},
                {'label': 'Local Authority [code]',
                 'value': "contact.geo.codes.admin_district"},
                {'label': 'Ward', 'value': 'contact.geo.admin_ward'},
                {'label': 'Ward [code]',
                 'value': 'contact.geo.codes.admin_ward'},
                {'label': 'Parish', 'value': 'contact.geo.parish'},
                {'label': 'Parish [code]',
                 'value': 'contact.geo.codes.parish'},
                {'label': 'LSOA', 'value': 'contact.geo.lsoa'},
                {'label': 'MSOA', 'value': 'contact.geo.msoa'},
                {'label': 'Parliamentary Constituency',
                 'value': 'contact.geo.parliamentary_constituency'},
                {'label': 'Parliamentary Constituency [code]',
                 'value': 'contact.geo.codes.parliamentary_constituency'},
            ],
        },
        "description": "The following fields are based on the postcode of the charities' UK registered office",
        "name": "Geography fields"
    },
}
