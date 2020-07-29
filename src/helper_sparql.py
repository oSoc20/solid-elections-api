import requests
from os import environ


def lblod_id_exists(lblod_id):
    """
    Check if a lblod id exists in the SPARQL database.

    Keyword arguments:
    lblod_id -- string that represents the lblod ID of whicht the existence in the database will be checked.

    Returns:
    Boolean reflecting whether or not the lblod ID is stored in the database.
    """
    sparql_url = environ.get('SPARQL_URL')

    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX ns1: <http://www.w3.org/ns/person#>
    ASK  {
    <%s> rdf:type ns1:Person.
    }""" % lblod_id

    res = requests.get(
        sparql_url,
        params={
            "default-graph-uri": "http://api.sep.osoc.be/mandatendatabank",
            "format": "json",
            "query": query
        }
    )
    results = res.json()
    print(results['boolean'])
    return bool(results['boolean'])


def get_lblod_cities():
    """
    Get all the cities in the database.

    Returns:
    A JSON object that is a list of objects with keys "cityURI", "cityName", "lacationLabel".
        "cityURI" contains the uri of the city which can be used to identify the city.
        "cityName" contains the name of the city.
        "locationLabel" denotes the type of location (Gemeente/Provincie/District).

        Example:
            [
                {
                    "cityURI": {
                        "type": "uri",
                        "value": "http://data.lblod.info/id/bestuurseenheden/81a6c688-9d4e-4905-b5af-c8b2386516e5"
                    },
                    "cityName": {
                        "type": "literal",
                        "value": "Puurs-Sint-Amands"
                    },
                    "locationLabel": {
                        "type": "literal",
                        "value": "Gemeente"
                }
            ]
    """
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX org: <http://www.w3.org/ns/org#>
    PREFIX core: <http://www.w3.org/2004/02/skos/core#>
    PREFIX ns1: <http://data.vlaanderen.be/ns/mandaat#>
    PREFIX ns2: <http://data.vlaanderen.be/ns/besluit#>
    SELECT DISTINCT ?cityURI ?cityName ?locationLabel
    WHERE {
        ?list rdf:type ns1:Kandidatenlijst;
        ns1:behoortTot ?election.
        ?election ns1:steltSamen ?bestuursOrgaan.
        ?bestuursOrgaan ns1:isTijdspecialisatieVan ?bestuursOrgaan2.
        ?bestuursOrgaan2 ns2:bestuurt ?bestuursEenheid.
        ?bestuursEenheid ns2:werkingsgebied ?cityURI;
        ns2:classificatie ?classificationCode.
        ?classificationCode core:prefLabel ?locationLabel.
        ?cityURI rdfs:label ?cityName.
        FILTER NOT EXISTS {
            ?classificationCode core:prefLabel "OCMW"
        }
    }"""

    return make_query(query)


def get_lblod_lists(city_url):
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX core: <http://www.w3.org/2004/02/skos/core#>
        PREFIX ns1: <http://data.vlaanderen.be/ns/mandaat#>
        PREFIX ns2: <http://data.vlaanderen.be/ns/besluit#>
        SELECT DISTINCT ?listURI ?listName
        WHERE {
            ?listURI rdf:type ns1:Kandidatenlijst;
            core:prefLabel ?listName;
            ns1:behoortTot ?election.
            ?election ns1:steltSamen ?bestuursOrgaan.
            ?bestuursOrgaan ns1:isTijdspecialisatieVan ?bestuursOrgaan2.
            ?bestuursOrgaan2 ns2:bestuurt ?bestuursEenheid.
            ?bestuursEenheid ns2:werkingsgebied <%s>;
            ns2:classificatie ?classificationCode.
            ?classificationCode core:prefLabel ?locationLabel.
            FILTER NOT EXISTS {
                ?classificationCode core:prefLabel "OCMW"
            }
        }""" % city_url

    return make_query(query)


def get_lblod_candidates(list_url):
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX ns1: <http://data.vlaanderen.be/ns/mandaat#>
        PREFIX ns2: <http://data.vlaanderen.be/ns/persoon#>
        SELECT DISTINCT ?personURI ?name ?familyName
        WHERE {
            <%s> ns1:heeftKandidaat ?personURI.
            ?personURI ns2:gebruikteVoornaam ?name;
            foaf:familyName ?familyName.
        }""" % list_url

    return make_query(query)


def get_lblod_person_info(person_uri):
    query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX core: <http://www.w3.org/2004/02/skos/core#>
            PREFIX ns1: <http://data.vlaanderen.be/ns/mandaat#>
            PREFIX ns2: <http://data.vlaanderen.be/ns/persoon#>
            SELECT DISTINCT ?name ?familyName ?listURI ?listName ?trackingNb
            WHERE {
                <%s> ns2:gebruikteVoornaam ?name;
                foaf:familyName ?familyName.
                ?listURI ns1:heeftKandidaat <%s>;
                core:prefLabel ?listName;
                ns1:lijstnummer ?trackingNb.
            }""" % (person_uri, person_uri)

    return make_query(query)


def make_query(query):
    sparql_url = environ.get('SPARQL_URL')

    res = requests.get(
        sparql_url,
        params={
            "default-graph-uri": "http://api.sep.osoc.be/mandatendatabank",
            "format": "json",
            "query": query
        }
    )
    results = res.json()['results']['bindings']
    return results
