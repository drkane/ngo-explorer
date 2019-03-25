import json
import os

from flask import url_for
from slugify import slugify

with open(os.path.join(os.path.dirname(__file__), 'countries.json'), encoding='utf8') as a:
    COUNTRIES = sorted(json.load(a)["countries"], key=lambda k: k['name'])
    COUNTRIES = [c for c in COUNTRIES if c["iso"]!='GBR']

def get_country_groups(as_dict=False):
    continents = set()
    undp = set()
    dac = set()
    for c in COUNTRIES:
        continents.add(c["continent"])
        if c['undp']:
            undp.add(c['undp'])
        if c['dac_status']:
            dac.add(c['dac_status'])

    if as_dict:
        areas = {}
        areas["all"] = {
            "name": "all countries",
            "countries": COUNTRIES
        }
        for c in COUNTRIES:
            areas[slugify(c["iso"])] = {
                "name": c["name"],
                "countries": [c]
            }

        for con in continents:
            areas[("continent", slugify(con))] = {
                "name": con,
                "countries": [c for c in COUNTRIES if c["continent"] == con]
            }

        for i in [("undp", "undp", "all UNDP countries", undp), ("dac", "dac_status", "all DAC countries", dac)]:
            areas[(i[0], "all")] = {
                "name": i[2],
                "countries": [c for c in COUNTRIES if c[i[1]]]
            }
            for con in i[3]:
                areas[(i[0], slugify(con))] = {
                    "name": con,
                    "countries": [c for c in COUNTRIES if c[i[1]] == con]
                }
        return areas

    return [
        (None, [{"id": url_for("data.country", countryid="all"), "name": "all countries"}], True),
        ("Continents", [
            {"id": url_for("data.region", regiontype="continent", regionid= slugify(c)), "name": c} for c in continents
        ], True),
        ('<abbr title="United Nations Development Programme">UNDP</abbr> regions', [
            {"id": url_for("data.region", regiontype="undp", regionid="all"), "name": "all UNDP regions"}
        ] + [
            {"id": url_for("data.region", regiontype="undp", regionid=slugify(c)), "name": c} for c in undp if c
        ], True),
        ('<abbr title="OECD Development Assistance Committee">DAC</abbr> groups', [
            {"id": url_for("data.region", regiontype="dac", regionid="all"), "name": "all DAC groups"}
        ] + [
            {"id": url_for("data.region", regiontype="dac", regionid=slugify(c)), "name": c} for c in dac if c
        ], True),
    ] + [
        (con, [
            {"id": url_for("data.country", countryid=slugify(c["iso"])), "name": c["name"]}
            for c in COUNTRIES if c["continent"] == con
        ], False)
        for con in sorted(continents)
    ]


def get_multiple_countries(countryid):
    countryids = countryid.lower().split("+")
    area = {
        "name": [],
        "countries": []
    }
    for i in countryids:
        this_area = get_country_groups(as_dict=True).get(i)
        if this_area:
            area["name"].append(this_area["name"])
            area["countries"].extend(this_area["countries"])
    if not area["countries"]:
        return None

    area["name"] = ", ".join(area["name"])
    return area

def get_country_by_id(id):
    for c in COUNTRIES:
        if c['id'] == id or c['iso'] == id or c['iso2'] == id:
            return c
    return None


SIMILAR_INITIATIVE = {
    "sen": [{
        "homepage": "https://pfongue.org/",
        "title": "Platform of European NGOs in Senegal",
        "directlink": "https://pfongue.org/-Cartographie-.html",
        "directlinktext": "Map of projects",
    }, {'title': 'CONGAD - Conseil des ONG d’Appui au Développement',
        'homepage': 'http://www.congad.org/',
        'source': 'Forus',
        'source_link': 'http://forus-international.org/en/about-us/who-we-are'
    }],
    "uga": [{
        "homepage": "https://ugandanetworks.org/",
        "title": "Uganda Networks",
        "directlink": "https://ugandanetworks.org/groups/250421/directory_search.aspx",
        "directlinktext": "Directory search",
    }, {
        "homepage": "http://www.uwasnet.org/Elgg/",
        "title": "Uganda Water and Sanitation NGO Network",
        "directlink": "http://www.uwasnet.org/Elgg/network/",
        "directlinktext": "Members directory",
    },{
        'title': 'UNNGOF - Uganda National NGO Forum',
        'homepage': 'http://ngoforum.or.ug/',
        'source': 'Forus',
        'source_link': 'http://forus-international.org/en/about-us/who-we-are'
    }],
    "bra": [{
        "homepage": "http://www.abong.org.br",
        "title": "Abong - Associaçao Brasileira de ONGs",
        'source': 'Forus',
        'source_link': 'http://forus-international.org/en/about-us/who-we-are'
    }],
    "hti": [{
        "homepage": "http://coeh.eu/members/",
        "title": "Coordination Europe-Haiti"
    }],
    'chl': [{'title': 'ACCIÓN - Asociación Chilena de ONG',
             'homepage': 'http://www.accionag.cl',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'bdi': [{'title': 'ADIR - Action Développement et Intégration Régionale',
             'homepage': 'https://adirplateform.wordpress.com/adir/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'dom': [{'title': 'Alianza ONG',
             'homepage': 'http://alianzaong.org.do',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'per': [{'title': 'ANC - Asociación Nacional de Centros',
             'homepage': 'http://www.anc.org.pe',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'ury': [{'title': 'ANONG - Asociación Nacional de ONG',
             'homepage': 'http://www.anong.org.uy',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'hnd': [{'title': 'ASONOG - Asociacion De Organismos No Gubernamentales',
             'homepage': 'http://www.asonog.hn/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'bwa': [{'title': 'Bocongo - Botswana Council of Non-Governmental Organisations',
             'homepage': 'http://www.bocongo.org/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'gbr': [{'title': 'Bond - British Overseas NGOs for Development',
             'homepage': 'http://www.bond.org.uk',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'chn': [{'title': 'CANGO - China Association for NGO Cooperation',
             'homepage': 'http://www.cango.org',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'khm': [{'title': 'CCC - Cooperation Committee for Cambodia',
             'homepage': 'http://www.ccc-cambodia.org',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'can': [{'title': 'CCIC - Canadian council for international co-operation',
             'homepage': 'http://www.ccic.ca',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'rwa': [{'title': 'CCOAIB - Conseil de Concertation des Organisations d’Appui aux Initiatives de Base',
             'homepage': 'http://www.ccoaib.org.rw',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'cog': [{'title': 'CCOD - Conseil de Concertation des ONG de développement',
             'homepage': 'https://pcpacongo.org/ccod/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'col': [{'title': 'CCONG - Confederación Colombiana de ONG',
             'homepage': 'http://www.ccong.org.co',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'syc': [{'title': 'CEPS - Citizens Engagement Platform Seychelles',
             'homepage': 'http://www.civilsociety.sc',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'ben': [{'title': 'CFRONG - Collectif des Fédérations et Réseaux d’ONG du Bénin',
             'homepage': 'http://www.cfrong.org/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'cok': [{'title': 'CICSO - Cook Islands Association of NGOs',
             'homepage': '',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'nzl': [{'title': 'CID - Council for International Development',
             'homepage': 'http://www.cid.org.nz',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'tcd': [{'title': 'CILONG - Centre d’information et de Liaison des ONG',
             'homepage': '',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'caf': [{'title': 'CIONGCA - Conseil Inter ONG de Centrafrique',
             'homepage': 'https://www.facebook.com/ciongcarca/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'cod': [{'title': 'CNONGD - Conseil National des ONGD de Développement',
             'homepage': 'http://www.cnongdrdc.org/cnongd.php',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'phl': [{'title': 'CODE - Caucus of Development NGO Networks',
             'homepage': 'http://www.code-ngo.org/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'cmr': [{'title': 'CONGAC - Collectif des ONG Agréées du Cameroun',
             'homepage': '',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'gtm': [{'title': 'CONGCOOP - Coordinación de ONG y Cooperativas',
             'homepage': 'http://www.congcoop.org.gt',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'esp': [{'title': 'Coordinadora - NGO Coordinator for Development',
             'homepage': 'http://www.coordinadoraongd.org/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'fra': [{'title': 'Coordination SUD - Coordination SUD – Solidarité Urgence Développement',
             'homepage': 'http://www.coordinationsud.org',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    # "civ": [{'title': 'CSCI - Convention de la Société Civile Ivoirienne',
    #          'homepage': 'http://www.cs-ci.com/',
    #          'source': 'Forus',
    #          'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'irl': [{'title': 'Dochas',
             'homepage': 'https://dochas.ie/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'arg': [{'title': 'EENGD - Red Encuentro',
             'homepage': 'http://www.encuentrodeongs.org.ar',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'mar': [{'title': 'Espace Associatif',
             'homepage': 'http://www.espace-associatif.ma',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'fji': [{'title': 'FCOSS - Fiji Council of Social Services',
             'homepage': '',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'mli': [{'title': 'FECONG - Fédération des Collectif d’ONG du Mali',
             'homepage': 'http://www.fecong.org',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'fin': [{'title': 'FINGO - Finnish NGO Platform',
             'homepage': 'https://www.fingo.fi/english',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'rou': [{'title': 'FOND - Romanian NGDOs Platform',
             'homepage': 'http://www.fondromania.org/pagini/index.php',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'ago': [{'title': 'FONGA - Foro das ONGs Angolanas',
             'homepage': 'https://www.facebook.com/plateformeFonga',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'gin': [{'title': 'FONGDD - Forum des ONG pour le Développement Durable',
             'homepage': '',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'stp': [{'title': 'FONG-STP - Federaçao das ONGs de Sao Tomé e Principe',
             'homepage': 'http://fong-stp.net',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'tgo': [{'title': 'FONGTO - Fédération des Organisations Non Gouvernementales au Togo',
             'homepage': 'http://fongto.org/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'cze': [{'title': 'FoRS - Czech Forum for Development Co-operation',
             'homepage': 'http://www.fors.cz',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'dnk': [{'title': 'Global Focus',
             'homepage': 'http://www.globaltfokus.dk/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'hun': [{'title': 'HAND - Hungarian Association of NGOs for Development and Humanitarian Aid',
             'homepage': 'http://hand.org.hu/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'idn': [{'title': 'INFID - International NGO Forum on Indonesian Development',
             'homepage': 'http://www.infid.org',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'usa': [{'title': 'InterAction',
             'homepage': 'http://www.interaction.org',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'jpn': [{'title': 'JANIC - Japan NGO Center for International Cooperation',
             'homepage': 'http://www.janic.org',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'moz': [{'title': 'Joint - League For NGOs in Mozambique',
             'homepage': 'http://www.joint.org.mz/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'kir': [{'title': 'KANGO - Kiribati Association of NGOs',
             'homepage': 'http://www.kango.org.ki',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'kor': [{'title': 'KCOC - Korea NGO Council for Overseas Development Cooperations',
             'homepage': 'http://www.ngokcoc.or.kr',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'lva': [{'title': 'LAPAS - Latvijas Platforma attīstības sadarbībai',
             'homepage': 'http://lapas.lv/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'ltu': [{'title': 'Lithuanian National Non-Governmental Development Cooperation Organisations’ Platform',
             'homepage': 'http://www.vbplatforma.org',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'mus': [{'title': 'MACOSS - Mauritius Council of Social Service',
             'homepage': 'http://www.macoss.intnet.mu/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'npl': [{'title': 'NFN - NGO Federation of Nepal',
             'homepage': 'http://www.ngofederation.org/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'},
            {'title': 'British and Nepal NGO Network (BRANNGO)',
             'homepage': 'https://www.branngo.org/'}],
    'nga': [{'title': 'NNNGO - Nigeria Network of NGOs',
             'homepage': 'http://www.nnngo.org',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'mdg': [{'title': 'PFNOSCM - Plateforme Nationale des Organisations de la Société Civile de Madagascar',
             'homepage': 'http://societecivilemalgache.com/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'prt': [{'title': 'Plataforma ONGD - Portuguese Platform NGOD',
             'homepage': 'http://www.plataformaongd.pt/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'bel': [{'title': 'Plateforme belge des ONG de développement et d’urgence',
             'homepage': '',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'cpv': [{'title': 'PLATONG - Plataforma das ONGs de Cabo Verde',
             'homepage': 'http://www.platongs.org.cv/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'pry': [{'title': 'POJOAJU - Asociación de ONGs del Paraguay',
             'homepage': 'http://www.pojoaju.org.py',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'mlt': [{'title': 'SKOP - National Platform of Maltese NGDOs',
             'homepage': 'http://www.skopmalta.org/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'svn': [{'title': 'SLOGA - Slovenian Global Action',
             'homepage': 'http://www.sloga-platform.org/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'bfa': [{'title': 'SPONG - Secrétariat Permanent des ONG du Burkina Faso',
             'homepage': 'http://www.spong.bf/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'twn': [{'title': 'Taiwan Alliance in International Development',
             'homepage': 'http://www.taiwanaid.org/en',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'gmb': [{'title': 'TANGO - The Association of Non-Governmental Organizations',
             'homepage': 'http://www.tangogambia.org/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'bol': [{'title': 'UNITAS - Red Unitas',
             'homepage': 'http://www.redunitas.org',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'ind': [{'title': 'VANI - Voluntary Action Network India',
             'homepage': 'http://www.vaniindia.org',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}],
    'zmb': [{'title': 'ZCSD - Zambia Council for Social Development',
             'homepage': 'http://www.zcsdev.org.zm/',
             'source': 'Forus',
             'source_link': 'http://forus-international.org/en/about-us/who-we-are'}]
}
