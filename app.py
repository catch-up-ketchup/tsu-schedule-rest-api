import json

from flask import Flask
from flask_cors import CORS, cross_origin

from scraper import get_schedule


app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
def say_hello():
    return 'Hello! It is simple API for tsu schedule :)'


@app.route('/schedule/<string:group>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def send_schedule(group):
    return json.dumps(get_schedule(group))


if __name__ == '__main__':
    app.run(debug=False)
