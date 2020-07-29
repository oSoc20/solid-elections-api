from sanic_openapi import doc


class StoreRequestBody:
    uri = doc.String("The uri of the webID.", required=True)
    lblod_id = doc.String("The uri of the lblod person.", required=True)


class StoreResponse:
    success = doc.Boolean("Boolean reflecting if the right query parameters were available in the request and if they are valid.")
    updated = doc.Boolean("Boolean reflecting whether the webID uri and lblod uri pair is stored in the database.")
    message = doc.String("String that clarifies the response.")


class GetResponseEntry:
    id = doc.Integer("The id of the entry.")
    uri = doc.String("Uri of the web ID of the entry")
    lblod_id = doc.String("Uri of the lblod id of this entry.")
    date_created = doc.Date("The date on which the entry was added to the database.")


class TypeValuePair:
    type = doc.String("The type of the entry.")
    value = doc.String("The value of the entry.")


class CityResponseEntry:
    cityURI = TypeValuePair
    cityName = TypeValuePair
    locationLabel = TypeValuePair


class CityResponse:
    success = doc.Boolean("Boolean")
    result = doc.List(CityResponseEntry, "List of all the cities.")
