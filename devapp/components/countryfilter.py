import dash_core_components as dcc
import dash_html_components as html
from slugify import slugify

# http://hdr.undp.org/en/content/developing-regions
UNDP_GROUPS = {
    "Arab States": [
        "DZA", "BHR", "DJI", "EGY", "IRQ", "JOR", "KWT", "LBN", "LBY", "MAR", "PSE", 
        "OMN", "QAT", "SAU", "SOM", "SDN", "SYR", "TUN", "ARE", "YEM"
    ],
    "East Asia and the Pacific": [
        "KHM", "CHN", "FJI", "IDN", "KIR", "PRK", "LAO", "MYS", "MHL", "FSM", "MNG",
        "MMR", "NRU", "MNG", "PLW", "PNG", "PHL", "WSM", "SLB", "THA", "TLS", "TON",
        "TUV", "VUT", "VNM"
    ],
    "Europe and Central Asia": [
        "ALB", "ARM", "AZE", "AZE", "BIH", "GEO", "KAZ", "KGZ", "MDA", "MNE", "SRB",
        "TJK", "MKD", "TUR", "TKM", "UKR", "UZB",
    ],
    "Latin America and the Caribbean": [
        "ATG", "ARG", "BHS", "BRB", "BLZ", "BOL", "BRA", "CHL", "COL", "CRI", "CUB",
        "DMA", "DOM", "ECU", "SLV", "GRD", "GTM", "GUY", "HTI", "HND", "JAM", "MEX",
        "NIC", "PAN", "PRY", "PER", "KNA", "LCA", "VCT", "SUR", "TTO", "URY", "VEN",
    ],
    "South Asia": [
        "AFG", "BGD", "BTN", "IND", "IRN", "MDV", "NPL", "PAK", "LKA",
    ],
    "Sub-Saharan Africa": [
        "AGO", "BEN", "BWA", "BFA", "BDI", "CPV", "CMR", "CAF", "TCD", "COM", "COG",
        "COD", "CIV", "GNQ", "ERI", "ETH", "GAB", "GMB", "GHA", "GIN", "GNB", "KEN",
        "LSO", "LBR", "MDG", "MWI", "MLI", "MRT", "MUS", "MOZ", "NAM", "NER", "NGA",
        "RWA", "STP", "SEN", "SYC", "SLE", "ZAF", "SSD", "SWZ", "TZA", "TGO", "UGA",
        "ZMB", "ZWE",
    ]
}
# http://www.oecd.org/dac/financing-sustainable-development/development-finance-standards/daclist.htm
DAC_OPTIONS = ["All", "Least Developed", "Lower Middle Income"]

COUNTRY_GROUPS = [
    (slugify("dac-{}".format(g)), "DAC", g) for g in DAC_OPTIONS
] + [
    (slugify("undp-{}".format(g)), "UNDP", g) for g in UNDP_GROUPS.keys()
]

def countryfilter():
    return html.Div(children=[
        html.P(id='simple-filter', className='mb4 f4 flex items-center', children=[
            "Show charities operating in ",
            dcc.Dropdown(
                options=[{
                    "label": "All countries",
                    "value": "__all"
                }],
                multi=True,
                id='area-of-operation-dropdown',
                className='bb-light-yellow',
                placeholder='Country',
                value='__all',
            ),
            html.Span(' or ', className='ph2'),
            html.Button(
                className='link underline bg-inherit bn pa0 pointer',
                children='upload a list of charities',
                id='open-upload-modal',
            ),
            '.',
        ]),
        # html.P(className='', children=[
        #     html.Abbr("ODA", title="Overseas Development Assistance"),
        #     " Recipient Countries: ",
        # ] + [
        #     html.A(id="country-group-dac-{}".format(slugify(g)), href='#', className='mr2', children=g)
        #     for g in DAC_OPTIONS
        # ]),
        # html.P(className='', children=[
        #     html.Abbr("UNDP", title="United Nations Development Programme"),
        #     " regions: ",
        # ] + [
        #     html.A(id="country-group-undp-{}".format(slugify(g)), href='#', className='mr2', children=g)
        #     for g in UNDP_GROUPS.keys()
        # ]),
    ])
