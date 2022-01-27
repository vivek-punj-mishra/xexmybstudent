from flask import Flask, make_response, json, g, request, jsonify, redirect
from flask_restful import Resource, Api, reqparse
import config
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import datetime
import time
import boto3
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
# from pymongo import MongoClient

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# from exmyb_app.helper import Zoho
# from exmyb_app import signals

# migrate=Migrate(app,db,compare_type=True)

api = Api(app)
jwt = JWTManager(app)
mail = Mail(app)
ma = Marshmallow(app)

# mongo_client = MongoClient(app.config['MONGO_SERVER'], app.config['MONGO_PORT'])
# exmyb_mongo_db = mongo_client[app.config['MONGO_DATABASE']]

cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})
# s3 = boto3.resource(
#     's3',
#     region_name=app.config['S3_REGION_NAME'],
#     aws_access_key_id=app.config['AWS_ACCESS_KEY'],
#     aws_secret_access_key=app.config['AWS_SECRET_KEY']
# )

import exmyb_app.routes.routes

if app.config['DEBUG']:
    app.debug = True


def conf_logging(app):
    """
    Setup proper logging
    """

    if app.debug is True:
        from exmyb_app.exmyb_file_handler import ExMyBFileHandler
        import logging
        file_handler = ExMyBFileHandler(app.config['LOG_FILE'],
                                                   maxBytes=1024 * 1024 * 100,
                                                   backupCount=31)
        if app.config['LOG_LEVEL'] == 'INFO':
            file_handler.setLevel(logging.INFO)
        elif app.config['LOG_LEVEL'] == 'DEBUG':
            file_handler.setLevel(logging.DEBUG)
        elif app.config['LOG_LEVEL'] == 'WARNING':
            file_handler.setLevel(logging.WARNING)
        else:
            file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(asctime)s - %(name)s - "
                                      "%(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(file_handler.level)


conf_logging(app)


@app.before_first_request
def crate_tables():
    from exmyb_app.models.users_model import UsersModel
    from exmyb_app.models.usr_verfication_model import UsrVerificationModel
    # from exmyb_app.models.support_comment_model import SupportComments
    db.create_all()


@app.before_request
def start_timer():
    g.start = time.time()


@app.after_request
def log_request(response):
    if request.path == '/favicon.ico':
        return response
    elif request.path.startswith('/static'):
        return response

    now = time.time()
    duration = round(now - g.start, 2)
    dt = datetime.datetime.fromtimestamp(now)

    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    host = request.host.split(':', 1)[0]
    args = dict(request.args)
    log_params = [
        ('method', request.method),
        ('path', request.path),
        ('status', response.status_code),
        ('duration', duration),
        ('ip', ip),
        ('host', host),
    ]

    request_id = request.headers.get('X-Request-ID')
    if request_id:
        log_params.append(('request_id', request_id, 'yellow'))

    app.logger.info(log_params)

    return response


@api.representation('application/json')
def output_json(data, code, headers=None):
    if code == 400 or code == 401:
        data['status'] = 0
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


@jwt.expired_token_loader
def jwt_expired_token_loader(jwt_header, jwt_payload):
    token_type = jwt_header['typ']
    resp = make_response(json.dumps(
        {'status': 0, app.config['JWT_ERROR_MESSAGE_KEY']: 'The {} token has expired'.format(token_type)}), 401)
    resp.headers['Content-Type'] = 'application/json'
    return resp


@jwt.unauthorized_loader
def jwt_unauthorized_loader(t):
    resp = make_response(json.dumps({'status': 0, app.config['JWT_ERROR_MESSAGE_KEY']: t}), 401)
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.before_first_request
def crate_tables():
    from exmyb_app.models.users_model import UsersModel
    # from exmyb_app.models.lead_model import LeadsModel
    db.create_all()
