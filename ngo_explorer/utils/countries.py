import json
import os
from typing import Optional

from flask import url_for
from flask_babel import _
from slugify import slugify

from ngo_explorer.classes.countries import (
    Country,
    CountryGroup,
    CountryGroupItem,
    CountryGroupItemList,
    CountryGroupValue,
    Initiative,
)

with open(
    os.path.join(os.path.dirname(__file__), "countries.json"), encoding="utf-8"
) as a:
    countries_raw = sorted(json.load(a)["countries"], key=lambda k: k["name"])
    COUNTRIES: list[Country] = [
        Country(**c) for c in countries_raw if c["iso"] != "GBR"
    ]
    print([c for c in COUNTRIES if c.iso2 == "TR"])


def get_country_sets() -> tuple[set[str], set[str], set[str]]:
    continents: set[str] = set()
    undp: set[str] = set()
    dac: set[str] = set()
    for country in COUNTRIES:
        continents.add(country.continent)
        if country.undp:
            undp.add(country.undp)
        if country.dac_status:
            dac.add(country.dac_status)
    return continents, undp, dac


def get_country_groups_lists() -> dict[str | tuple[str, str], CountryGroupItem]:
    continents, undp, dac = get_country_sets()

    areas: dict[str | tuple[str, str], CountryGroupItem] = {}
    areas["all"] = CountryGroupItem(name=_("all countries"), countries=COUNTRIES)
    for c in COUNTRIES:
        areas[slugify(c.iso)] = CountryGroupItem(name=c.name, countries=[c])

    for con in continents:
        areas[("continent", slugify(con))] = CountryGroupItem(
            name=con,
            countries=[country for country in COUNTRIES if country.continent == con],
        )

    for key, lookup, title, values in [
        ("undp", "undp", _("all UNDP countries"), undp),
        ("dac", "dac_status", _("all DAC countries"), dac),
    ]:
        areas[(key, "all")] = CountryGroupItem(
            name=title,
            countries=[
                country for country in COUNTRIES if getattr(country, lookup, None)
            ],
        )
        for con in values:
            areas[(key, slugify(con))] = CountryGroupItem(
                name=con,
                countries=[
                    country
                    for country in COUNTRIES
                    if getattr(country, lookup, None) == con
                ],
            )
    return areas


def get_country_groups() -> list[CountryGroup]:
    continents, undp, dac = get_country_sets()

    return [
        CountryGroup(
            values=[
                CountryGroupValue(
                    id=url_for("data.country", countryid="all"),
                    name="all countries",
                )
            ],
            title=None,
            show_initial=True,
        ),
        CountryGroup(
            values=[
                CountryGroupValue(
                    id=url_for(
                        "data.region", regiontype="continent", regionid=slugify(c)
                    ),
                    name=c,
                )
                for c in continents
            ],
            title=_("Continents"),
            show_initial=True,
        ),
        CountryGroup(
            values=(
                [
                    CountryGroupValue(
                        id=url_for("data.region", regiontype="undp", regionid="all"),
                        name=_("all UNDP regions"),
                    )
                ]
                + [
                    CountryGroupValue(
                        id=url_for(
                            "data.region", regiontype="undp", regionid=slugify(c)
                        ),
                        name=c,
                    )
                    for c in undp
                    if c
                ]
            ),
            title=_(
                '<abbr title="United Nations Development Programme">UNDP</abbr> regions'
            ),
            show_initial=True,
        ),
        CountryGroup(
            values=[
                CountryGroupValue(
                    id=url_for("data.region", regiontype="dac", regionid="all"),
                    name=_("all DAC groups"),
                )
            ]
            + [
                CountryGroupValue(
                    id=url_for("data.region", regiontype="dac", regionid=slugify(c)),
                    name=c,
                )
                for c in dac
                if c
            ],
            title=_(
                '<abbr title="OECD Development Assistance Committee">DAC</abbr> groups'
            ),
            show_initial=True,
        ),
    ] + [
        CountryGroup(
            [
                CountryGroupValue(
                    id=url_for("data.country", countryid=slugify(country.iso)),
                    name=country.name,
                )
                for country in COUNTRIES
                if country.continent == con
            ],
            title=con,
            show_initial=False,
        )
        for con in sorted(continents)
    ]


def get_multiple_countries(countryid: str) -> Optional[CountryGroupItemList]:
    countryids = countryid.lower().split("+")
    area = CountryGroupItemList(names=[], countries=[])
    for i in countryids:
        this_area = get_country_groups_lists().get(i)
        if this_area:
            area.names.append(this_area.name)
            area.countries.extend(this_area.countries)
    if not area.countries:
        return None

    return area


def get_country_by_id(id: str) -> Optional[Country]:
    for country in COUNTRIES:
        if country.id == id or country.iso == id or country.iso2 == id:
            return country
    return None


SIMILAR_INITIATIVE: dict[str, list[Initiative]] = {
    "sen": [
        Initiative(
            homepage="https://pfongue.org/",
            title=_("Platform of European NGOs in Senegal"),
            directlink="https://pfongue.org/-Cartographie-.html",
            directlinktext=_("Map of projects"),
        ),
        Initiative(
            title="CONGAD - Conseil des ONG d’Appui au Développement",
            homepage="http://www.congad.org/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        ),
    ],
    "uga": [
        Initiative(
            homepage="https://ugandanetworks.org/",
            title="Uganda Networks",
            directlink="https://ugandanetworks.org/groups/250421/directory_search.aspx",
            directlinktext=_("Directory search"),
        ),
        Initiative(
            homepage="http://www.uwasnet.org/Elgg/",
            title="Uganda Water and Sanitation NGO Network",
            directlink="http://www.uwasnet.org/Elgg/network/",
            directlinktext=_("Members directory"),
        ),
        Initiative(
            title="UNNGOF - Uganda National NGO Forum",
            homepage="http://ngoforum.or.ug/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        ),
    ],
    "bra": [
        Initiative(
            homepage="http://www.abong.org.br",
            title="Abong - Associaçao Brasileira de ONGs",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "hti": [
        Initiative(
            homepage="http://coeh.eu/members/", title="Coordination Europe-Haiti"
        )
    ],
    "chl": [
        Initiative(
            title="ACCIÓN - Asociación Chilena de ONG",
            homepage="http://www.accionag.cl",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "bdi": [
        Initiative(
            title="ADIR - Action Développement et Intégration Régionale",
            homepage="https://adirplateform.wordpress.com/adir/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "dom": [
        Initiative(
            title="Alianza ONG",
            homepage="http://alianzaong.org.do",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "per": [
        Initiative(
            title="ANC - Asociación Nacional de Centros",
            homepage="http://www.anc.org.pe",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "ury": [
        Initiative(
            title="ANONG - Asociación Nacional de ONG",
            homepage="http://www.anong.org.uy",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "hnd": [
        Initiative(
            title="ASONOG - Asociacion De Organismos No Gubernamentales",
            homepage="http://www.asonog.hn/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "bwa": [
        Initiative(
            title="Bocongo - Botswana Council of Non-Governmental Organisations",
            homepage="http://www.bocongo.org/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "gbr": [
        Initiative(
            title="Bond - British Overseas NGOs for Development",
            homepage="http://www.bond.org.uk",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "chn": [
        Initiative(
            title="CANGO - China Association for NGO Cooperation",
            homepage="http://www.cango.org",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "khm": [
        Initiative(
            title="CCC - Cooperation Committee for Cambodia",
            homepage="http://www.ccc-cambodia.org",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "can": [
        Initiative(
            title="CCIC - Canadian council for international co-operation",
            homepage="http://www.ccic.ca",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "rwa": [
        Initiative(
            title="CCOAIB - Conseil de Concertation des Organisations d’Appui aux Initiatives de Base",
            homepage="http://www.ccoaib.org.rw",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "cog": [
        Initiative(
            title="CCOD - Conseil de Concertation des ONG de développement",
            homepage="https://pcpacongo.org/ccod/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "col": [
        Initiative(
            title="CCONG - Confederación Colombiana de ONG",
            homepage="http://www.ccong.org.co",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "syc": [
        Initiative(
            title="CEPS - Citizens Engagement Platform Seychelles",
            homepage="http://www.civilsociety.sc",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "ben": [
        Initiative(
            title="CFRONG - Collectif des Fédérations et Réseaux d’ONG du Bénin",
            homepage="http://www.cfrong.org/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "cok": [
        Initiative(
            title="CICSO - Cook Islands Association of NGOs",
            homepage="",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "nzl": [
        Initiative(
            title="CID - Council for International Development",
            homepage="http://www.cid.org.nz",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "tcd": [
        Initiative(
            title="CILONG - Centre d’information et de Liaison des ONG",
            homepage="",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "caf": [
        Initiative(
            title="CIONGCA - Conseil Inter ONG de Centrafrique",
            homepage="https://www.facebook.com/ciongcarca/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "cod": [
        Initiative(
            title="CNONGD - Conseil National des ONGD de Développement",
            homepage="http://www.cnongdrdc.org/cnongd.php",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "phl": [
        Initiative(
            title="CODE - Caucus of Development NGO Networks",
            homepage="http://www.code-ngo.org/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "cmr": [
        Initiative(
            title="CONGAC - Collectif des ONG Agréées du Cameroun",
            homepage="",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "gtm": [
        Initiative(
            title="CONGCOOP - Coordinación de ONG y Cooperativas",
            homepage="http://www.congcoop.org.gt",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "esp": [
        Initiative(
            title="Coordinadora - NGO Coordinator for Development",
            homepage="http://www.coordinadoraongd.org/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "fra": [
        Initiative(
            title="Coordination SUD - Coordination SUD – Solidarité Urgence Développement",
            homepage="http://www.coordinationsud.org",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    # "civ": [Initiative('title': 'CSCI - Convention de la Société Civile Ivoirienne',
    #          'homepage': 'http://www.cs-ci.com/',
    #          'source': 'Forus',
    #          'source_link': 'http://forus-international.org/en/about-us/who-we-are')],
    "irl": [
        Initiative(
            title="Dochas",
            homepage="https://dochas.ie/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "arg": [
        Initiative(
            title="EENGD - Red Encuentro",
            homepage="http://www.encuentrodeongs.org.ar",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "mar": [
        Initiative(
            title="Espace Associatif",
            homepage="http://www.espace-associatif.ma",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "fji": [
        Initiative(
            title="FCOSS - Fiji Council of Social Services",
            homepage="",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "mli": [
        Initiative(
            title="FECONG - Fédération des Collectif d’ONG du Mali",
            homepage="http://www.fecong.org",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "fin": [
        Initiative(
            title="FINGO - Finnish NGO Platform",
            homepage="https://www.fingo.fi/english",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "rou": [
        Initiative(
            title="FOND - Romanian NGDOs Platform",
            homepage="http://www.fondromania.org/pagini/index.php",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "ago": [
        Initiative(
            title="FONGA - Foro das ONGs Angolanas",
            homepage="https://www.facebook.com/plateformeFonga",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "gin": [
        Initiative(
            title="FONGDD - Forum des ONG pour le Développement Durable",
            homepage="",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "stp": [
        Initiative(
            title="FONG-STP - Federaçao das ONGs de Sao Tomé e Principe",
            homepage="http://fong-stp.net",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "tgo": [
        Initiative(
            title="FONGTO - Fédération des Organisations Non Gouvernementales au Togo",
            homepage="http://fongto.org/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "cze": [
        Initiative(
            title="FoRS - Czech Forum for Development Co-operation",
            homepage="http://www.fors.cz",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "dnk": [
        Initiative(
            title="Global Focus",
            homepage="http://www.globaltfokus.dk/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "hun": [
        Initiative(
            title="HAND - Hungarian Association of NGOs for Development and Humanitarian Aid",
            homepage="http://hand.org.hu/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "idn": [
        Initiative(
            title="INFID - International NGO Forum on Indonesian Development",
            homepage="http://www.infid.org",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "usa": [
        Initiative(
            title="InterAction",
            homepage="http://www.interaction.org",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "jpn": [
        Initiative(
            title="JANIC - Japan NGO Center for International Cooperation",
            homepage="http://www.janic.org",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "moz": [
        Initiative(
            title="Joint - League For NGOs in Mozambique",
            homepage="http://www.joint.org.mz/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "kir": [
        Initiative(
            title="KANGO - Kiribati Association of NGOs",
            homepage="http://www.kango.org.ki",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "kor": [
        Initiative(
            title="KCOC - Korea NGO Council for Overseas Development Cooperations",
            homepage="http://www.ngokcoc.or.kr",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "lva": [
        Initiative(
            title="LAPAS - Latvijas Platforma attīstības sadarbībai",
            homepage="http://lapas.lv/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "ltu": [
        Initiative(
            title="Lithuanian National Non-Governmental Development Cooperation Organisations’ Platform",
            homepage="http://www.vbplatforma.org",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "mus": [
        Initiative(
            title="MACOSS - Mauritius Council of Social Service",
            homepage="http://www.macoss.intnet.mu/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "npl": [
        Initiative(
            title="NFN - NGO Federation of Nepal",
            homepage="http://www.ngofederation.org/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        ),
        Initiative(
            title="British and Nepal NGO Network (BRANNGO)",
            homepage="https://www.branngo.org/",
        ),
    ],
    "nga": [
        Initiative(
            title="NNNGO - Nigeria Network of NGOs",
            homepage="http://www.nnngo.org",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "mdg": [
        Initiative(
            title="PFNOSCM - Plateforme Nationale des Organisations de la Société Civile de Madagascar",
            homepage="http://societecivilemalgache.com/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "prt": [
        Initiative(
            title="Plataforma ONGD - Portuguese Platform NGOD",
            homepage="http://www.plataformaongd.pt/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "bel": [
        Initiative(
            title="Plateforme belge des ONG de développement et d’urgence",
            homepage="",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "cpv": [
        Initiative(
            title="PLATONG - Plataforma das ONGs de Cabo Verde",
            homepage="http://www.platongs.org.cv/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "pry": [
        Initiative(
            title="POJOAJU - Asociación de ONGs del Paraguay",
            homepage="http://www.pojoaju.org.py",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "mlt": [
        Initiative(
            title="SKOP - National Platform of Maltese NGDOs",
            homepage="http://www.skopmalta.org/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "svn": [
        Initiative(
            title="SLOGA - Slovenian Global Action",
            homepage="http://www.sloga-platform.org/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "bfa": [
        Initiative(
            title="SPONG - Secrétariat Permanent des ONG du Burkina Faso",
            homepage="http://www.spong.bf/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "twn": [
        Initiative(
            title="Taiwan Alliance in International Development",
            homepage="http://www.taiwanaid.org/en",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "gmb": [
        Initiative(
            title="TANGO - The Association of Non-Governmental Organizations",
            homepage="http://www.tangogambia.org/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "bol": [
        Initiative(
            title="UNITAS - Red Unitas",
            homepage="http://www.redunitas.org",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "ind": [
        Initiative(
            title="VANI - Voluntary Action Network India",
            homepage="http://www.vaniindia.org",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
    "zmb": [
        Initiative(
            title="ZCSD - Zambia Council for Social Development",
            homepage="http://www.zcsdev.org.zm/",
            source="Forus",
            source_link="http://forus-international.org/en/about-us/who-we-are",
        )
    ],
}
