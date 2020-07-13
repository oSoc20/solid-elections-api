from sanic import Sanic, response
from playhouse.shortcuts import model_to_dict
import models
import os
import json

app = Sanic('Test API')


@app.route('/store/', methods=['POST'])
async def r_store(req):
	uri = req.json['uri']
	wid = models.WebID(uri=uri)
	wid.save()
	return response.text('WebID succesfully added to the database!')



@app.route('/get')
async def r_get(req):
	webids = models.WebID.select()

	webids = [model_to_dict(wid) for wid in webids]  # Convert list of ModelSelect objects to Python dicts
	for wid in webids:
		wid['date_created'] = wid['date_created'].isoformat()  # Convert Python datetime object to ISO 8601 string

	return response.json(webids)



if __name__ == '__main__':
	models.db.create_tables([models.WebID])  # Connect to database & create tables if necessary
	app.run(host='0.0.0.0', port=8000, debug=os.environ.get('DEBUG'))