from sanic import Sanic, response
import models
import os
import json

app = Sanic('Test API')


@app.route('/store/<name>')
async def r_store(req, name):
	wid = models.WebID(
		name=name,
		uri='https://samvdkris.inrupt.net/profile/card#me'
	)
	wid.save()
	return response.text('WebID succesfully added to the database!')



@app.route('/get')
async def r_get(req):
	webids = models.WebID.select()
	res = [(wid.name, wid.uri, str(wid.uploaded_date)) for wid in webids]  # Return a user's name, WebID URI and the date+time it was added in ISO 8601 format
	return response.json(res)



if __name__ == '__main__':
	models.db.create_tables([models.WebID])
	app.run(host='0.0.0.0', port=8000, debug=os.environ.get('DEBUG'))