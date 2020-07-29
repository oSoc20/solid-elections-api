"""
This module defines and implements all the endpoints of the API.
"""

from sanic import Sanic, response
from sanic_openapi import doc, swagger_blueprint
from sanic_cors import CORS
from playhouse.shortcuts import model_to_dict
from peewee import IntegrityError, DoesNotExist
from os import environ

import models
import helper_sparql

app = Sanic('Test API')
app.blueprint(swagger_blueprint)
app.config["API_TITLE"] = "Solid Elections API"
app.config["API_DESCRIPTION"] = "API documentation of the Solid Elections API"
CORS(app)


# Middleware to automatically open/close a database connection for every request
@app.middleware('request')
async def handle_request(request):
    """Open database connection before each request is handled."""
    models.db.connect()


@app.middleware('response')
async def handle_response(request, response):
    """Close database connection after each request is handled."""
    if not models.db.is_closed():
        models.db.close()


@app.route('/store/', methods=['POST'])
@doc.summary("Store a new webID in the database given a valid webID uri and a lblod uri.")
async def r_store(req):
    """
    Store a new webID in the database given a valid webID uri and a lblod uri.

    Keyword arguments:
    The request should contain valid json parameters for "uri" and "lblod".
        Example:
            {
                "uri": "https://jonasvervloet.inrupt.net/profile/card#me",
                "lblod_id": "http://data.lblod.info/id/personen/41e449eafddf2c0c2365a294376780293d92fb401241589a1f403cdff8d2ce5a"
            }

    Returns:
    The response contains json name/value pairs "success", "updated" and "message".
        "success" denotes if the right query parameters are available and if they are valid.
        "updated" denotes if the webID uri and lblod uri pair is stored in the database.
            This is set to False when the webID uri is already used in the database.
        "message" clarifies the response.

        Example:
            {
                "success": True,
                "updated": True,
                "message": "WebID successfully added to the database!"
            }
    """

    # Get 'uri' and 'lblod_id' from JSON body and throw HTTP/400 if one of them is missing
    uri = req.json.get('uri')
    lblod_id = req.json.get('lblod_id')
    if not uri or not lblod_id:
        return response.json({'success': False, 'updated': False, 'message': 'Please set the "uri" and "lblod_id" fields in your JSON body'}, status=400)

    if not helper_sparql.lblod_id_exists(lblod_id):
        return response.json({'success': False, 'updated': False, 'message': 'This lblod ID does not exist in our dataset'}, status=400)

    # Try to add the data to the database, throw HTTP/400 if user tries to add an existing value
    web_id = models.WebID(uri=uri, lblod_id=lblod_id)
    try:
        web_id.save()
    except IntegrityError:
        return response.json({'success': True, 'updated': False, 'message': 'WebID or lblod ID already exists in database'}, status=400)

    return response.json({'success': True, 'updated': True, 'message': 'WebID succesfully added to the database!'})


@app.route('/get')
@doc.summary("Get all stored webIDs in the database.")
@doc.description("This endpoints can be used to retrieve all the web id's that are stored in the database")
async def r_get(req):
    """
    Get all stored webIDs in the database.

    Returns:
    The response contains a list of json objects with fields "id", "uri", "lblod_id", "date_created".
    Each object corresponds with an entry stored in the database.
        "id" represents the id of the entry.
        "uri" contains the uri of the webID.
        "lblod" contains the uri of a person in the database.
        "date_created" contains the date on which the entry was added to the database.

        Example:
            [
                {
                    "id": 1,
                    "uri": "https://jonasvervloet.inrupt.net/profile/card#me",
                    "lblod_id": "http://data.lblod.info/id/personen/41e449eafddf2c0c2365a294376780293d92fb401241589a1f403cdff8d2ce5a",
                    "date_created": "2020-07-27T16:44:10.177264"
                }
            ]
    """
    return response.json(get_web_ids())


@app.route('/cities', methods=['GET'])
@doc.summary("Get all the cities in the database.")
async def get_handler(req):
    """
    Get all the cities in the database.

    Returns:
    The result contains two value/name pairs: "success" and "result".
        "success" denotes whether the request was handled successfully.
        "result" contains the actual result that is a list of json objects that contain "cityURI", "cityName" and "locationLabel".
            "cityURI" contains the uri of the city which can be used to identify the city.
            "cityName" contains the name of the city.
            "locationLabel" denotes the type of location (Gemeente/Provincie/District).

        Example:
            {
                "success": true,
                "result": [
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
            }
    """
    cities = helper_sparql.get_lblod_cities()
    return response.json(
        {
            'success': True,
            'result': cities
        }
    )


@app.route('/lists', methods=['GET'])
@doc.summary("Get all lists that are active for a given city.")
async def get_handler(req):
    """
    Get all lists that are active for a given city.

    Keyword arguments:
    The request should contain a valid parameter for "cityURI".
        Example:
            /lists?cityURI=http://data.lblod.info/id/werkingsgebieden/39173049fa95c468999d3862c3e6d22184c604d0864d6e56d1660886e17ca3c7

    Returns:
    The result contains two value/name pairs: "success" and "result".
        "success" denotes whether the request was handled successfully.
            This is set to False when the required parameters are not present.
        "result" contains the actual result that is a list of json objects that contain "listURI" and "listName".
            "listURI" contains the uri of the list which can be used to identify the list.
            "listName" contains the name of the list.

        Example:
            {
                "success": true,
                "result": [
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
            }
    """
    try:
        city_uri = req.args['cityURI'][0]
    except KeyError:
        return response.json(
            {
                'message': 'Wrong query parameters',
                'succes': False
            },
            status=400
        )
    lists = helper_sparql.get_lblod_lists(city_uri)
    return response.json(
        {
            'success': True,
            'result': lists
        }
    )


@app.route('/candidates', methods=['GET'])
@doc.summary("Get all candidates that are on a given list.")
async def get_handler(req):
    """
    Get all candidates that are on a given list.

    Keyword arguments:
    The request should contain a valid parameter for "listURI".
        Example:
            /candidates?listURI=http://data.lblod.info/id/kandidatenlijsten/078a1ef8-0875-48b2-b8fc-6167f5cfa3c0

    Returns:
    The result contains two value/name pairs: "success" and "result".
        "success" denotes whether the request was handled successfully.
            This is set to False when the required parameters are not present.
        "result" contains the actual result that is a list of json objects that contain "personURI", "name", "familyName", <optional>"webID".
            "personURI" contains the uri of the person which can be used to identify the list.
            "name" contains the name of the person.
            "familyName" contains the family name of the person.
            "webID"<optional> contains the webID uri that is linked to the person.
                This webID field is only present if there is an entry in our database with the personURI.

        Example:
            {
                "success": true,
                "result": [
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
                        },
                        "webID": {
                            "type": "literal",
                            "value": "https://bert1.solid.community/profile/card#me"
                        }
                    }
                ]
            }
    """
    try:
        list_uri = req.args['listURI'][0]
    except KeyError:
        return response.json(
            {
                'message': 'Wrong query parameters',
                'succes': False,
            },
            status=400
        )
    candidates = helper_sparql.get_lblod_candidates(list_uri)
    for candidate in candidates:
        try:
            web_id_uri = get_web_id(candidate['personURI']['value'])
            candidate['webID'] = {
                'type': 'literal',
                'value': web_id_uri
            }
        except DoesNotExist:
            continue
    return response.json(
        {
            'success': True,
            'result': candidates
        }
    )


@app.route('/person', methods=['GET'])
@doc.summary("Get info about a person given the persons' uri.")
async def get_handler(req):
    """
    Get info about a person given the persons' uri.

    Keyword arguments:
    The request should contain a valid parameter for "personURI".
        Example:
            /person?lblodURI=http://data.lblod.info/id/personen/4bfe62e576c4f955a3080ad38a213a66a8896e7ac9e6029b5185947b1c8427cc

    Returns:
    The result contains two value/name pairs: "success" and "result".
        "success" denotes whether the request was handled successfully.
            This is set to False when the required parameters are not present.
        "result" contains the actual result that is a list of json objects that contain "name", "familyName", "familyName", "listURI", "listName", "trackingNb".
            The list can contain multiple entries when the person campaigned for multiple lists.

            "name" contains the name of the person.
            "familyName" contains the family name of the person.
            "listURI" contains uri of a list where the person is on.
            "listName" contains the name of the list.
            "trackingNb" contains the tracking number of the list.

        Example:
            {
                "success": true,
                "result": [
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
            }
    """
    try:
        person_uri = req.args['personURI'][0]
    except KeyError:
        return response.json(
            {
                'message': 'Wrong query parameters',
                'succes': False,
            },
            status=400
        )
    info = helper_sparql.get_lblod_person_info(person_uri)
    return response.json(
        {
            'success': True,
            'result': info
        }
    )


def get_web_ids():
    """
    Get all the webIDs in the database.

    Returns:
    A list of dictionaries with keys "id", "uri", "lblod_id" and "date_created".
        "id" contains the id of the entry.
        "uri" contains the webID  uri of the entry.
        "lblod_id" contains the uri of the person to which the entry links.
        "date_created" contains the date on which the entry was added to the database.

        Example:
            [
                {
                    "id": 46,
                    "uri": "https://bert1.solid.community/profile/card#me",
                    "lblod_id": "http://data.lblod.info/id/personen/ed820a7da8c187ddb58a662737d9171d7522740b1c7727501d44d17c09b9afa8",
                    "date_created": "2020-07-27T15:43:23.874075"
                },
                {
                    "id": 73,
                    "uri": "https://kakumi.inrupt.net/profile/card#me",
                    "lblod_id": "http://data.lblod.info/id/personen/8fc807a40c2b8a67726f490272ca72256fa944e4bdcc29c846a1498abfebe034",
                    "date_created": "2020-07-28T12:11:03.584871"
                },
            ]
    """
    web_ids = models.WebID.select()

    # Convert list of ModelSelect objects to Python dicts
    web_ids = [model_to_dict(web_id) for web_id in web_ids]
    for web_id in web_ids:
        # Convert Python datetime object to ISO 8601 string
        web_id['date_created'] = web_id['date_created'].isoformat()
    return web_ids


def get_web_id(lblod_id):
    """
    Get the webID uri for a given lblod id.

    Keyword arguments:
    lblod_id -- string that represents the lblod ID that is stored in the database.
        This function will raise a "DoesNotExist" exception when no entry in the database contains the ID.

    Returns
    A string that contains the webID uri of the entry in the database that matches the given lblod ID.
    """
    web_id = models.WebID.get(models.WebID.lblod_id == lblod_id)
    return web_id.uri


if __name__ == '__main__':
    # Connect to database & create tables if necessary
    models.db.create_tables([models.WebID])
    models.db.close()
    app.run(host='0.0.0.0', port=8000, debug=environ.get('DEBUG'))
