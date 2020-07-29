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
    A JSON object that is a list of objects with keys "cityURI", "cityName" and "locationLabel".
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


def get_lblod_lists(city_uri):
    """
    Get all the lists in the database that are acitve in a city with given uri.

    Keyword arguments:
    city_uri -- string that represents the uri of the city of which all the lists will be searched.

    Returns:
    A JSON object that is a list of objects with keys "listURI" and "listName".
        "listURI" contains the uri of the list which can be used to identify the list.
        "listName" contains the name of the list.

        Example:
            [
                {
                    "listURI": {
                        "type": "uri",
                        "value": "http://data.lblod.info/id/kandidatenlijsten/091e6c1f-39b7-4ab4-8779-2f8ce77096b5"
                    },
                    "listName": {
                        "type": "literal",
                        "value": "OK"
                }
            ]
    """
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
        }""" % city_uri

    return make_query(query)


def get_lblod_candidates(list_uri):
    """
    Get all the candidates in the database that campaign(ed) for a list with given uri.

    Keyword arguments:
    list_uri -- string that represents the uri of the list of which all the candidates will be searched.

    Returns:
    A JSON object that is a list of objects with keys "personURI", "name" and "familyName".
        "personURI" contains the uri of the person which can be used to identify the list.
        "name" contains the name of the person.
        "familyName" contains the family name of the person.

        Example:
            [
                {
                    "personURI": {
                        "type": "uri",
                        "value": "http://data.lblod.info/id/personen/ed820a7da8c187ddb58a662737d9171d7522740b1c7727501d44d17c09b9afa8"
                    },
                    "name": {
                        "type": "literal",
                        "value": "Bart"
                    },
                    "familyName": {
                        "type": "literal",
                        "value": "Tommelein"
                    }
                }
            ]
    """
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
        }""" % list_uri

    return make_query(query)


def get_lblod_person_info(person_uri):
    """
    Get info about the person in the database with given uri.

    Keyword arguments:
    person -- string that represents the uri of the person of which the info will be searched.

    Returns:
    A JSON object that is a list of objects with keys "name", "familyName", "listURI", "listName" and "trackingNb".
        The list can contain multiple entries when the person campaigned for multiple lists.

        "name" contains the name of the person.
        "familyName" contains the family name of the person.
        "listURI" contains uri of a list where the person is on.
        "listName" contains the name of the list.
        "trackingNb" contains the tracking number of the list.

        Example:
            [
                {
                    "name": {
                        "type": "literal",
                        "value": "Nabilla"
                    },
                    "familyName": {
                        "type": "literal",
                        "value": "Ait Daoud"
                    },
                    "listURI": {
                        "type": "uri",
                        "value": "http://data.lblod.info/id/kandidatenlijsten/078a1ef8-0875-48b2-b8fc-6167f5cfa3c0"
                    },
                    "listName": {
                        "type": "literal",
                        "value": "N-VA"
                    },
                    "trackingNb": {
                        "type": "literal",
                        "value": "2"
                    }
                }
            ]
    """
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
    """
    Make a query to the SPARQL database.

    Keyword arguments:
    query -- string that satisfies the SPARQL query language syntax.

    Returns:
    A JSON object that represents the result of the query.
    """
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
