import json

from flask import Flask
from flask_cors import CORS, cross_origin

from scraper import get_schedule
from utils import quote_text
from test_schedule import test_schedule


application = Flask(__name__)
CORS(application)
application.config['CORS_HEADERS'] = 'Content-Type'


@application.route('/')
def say_hello():
    return 'Hello! It is simple API for tsu schedule :)'


@application.route('/schedule/<string:group>', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def send_schedule(group):
    response_data = {
        'schedule': get_schedule(group),
        'group': quote_text(group, reverse=True)
    }
    return json.dumps(response_data)


@application.route('/test-schedule/<string:group>', methods=['GET'])
def send_test_schedule(group):
    return json.dumps(test_schedule)


if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=False)
