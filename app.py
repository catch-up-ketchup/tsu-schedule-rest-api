import json

from flask import Flask, request
from flask_cors import CORS, cross_origin

from scraper import get_schedule
from utils import quote_text
from test_schedule import test_schedule


application = Flask(__name__)
CORS(application)
application.config['CORS_HEADERS'] = 'Content-Type'


@application.route('/')
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def say_hello():
    return 'Hello! It is simple API for tsu schedule :)'


@application.route('/schedule/', methods=['GET'])
@cross_origin(origin='https://tsu-schedule.space', headers=['Content-Type', 'Authorization'])
def send_schedule():
    group = request.args.get('group')
    response_data = {
        'schedule': get_schedule(group),
        'group': quote_text(group, reverse=True)
    }
    return json.dumps(response_data)


@application.route('/test-schedule/', methods=['GET'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def send_test_schedule():
    return json.dumps(test_schedule)


if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=False)
