from sanic import Sanic, response
import models
import os
import json

app = Sanic('Test API')


@app.route('/store/<name>')
async def r_store(req, name):
	p = models.Person(name=name)
	p.save()
	return response.text('Person added')



@app.route('/get')
async def r_get(req):
	people = models.Person.select()
	res = [(p.id, p.name) for p in people]
	return response.json(res)



if __name__ == '__main__':
	models.db.create_tables([models.Person])
	app.run(host='0.0.0.0', port=8000, debug=os.environ.get('DEBUG'))