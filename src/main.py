from sanic import Sanic, response
import os
import json

app = Sanic('Test API')

DATABASE_FILE = 'database.json'


def load_db():
	with open(DATABASE_FILE) as f:
		return json.load(f)


@app.route('/store', methods=['POST'])
async def r_store(req):
	name = req.json['name']
	webid = req.json['webid']

	db = load_db()
	db.append({
		'name': name,
		'webid': webid
	})
	with open(DATABASE_FILE, 'w') as f:
		json.dump(db, f)

	return response.empty()


@app.route('/get')
async def r_get(req):
	db = load_db()
	return response.json(db)



if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000, debug=os.environ.get('DEBUG'))