import pymongo
import requests
from decouple import config as config_decouple
from flask import Flask, request, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util
from bson.objectid import ObjectId
from flask_restful import Api
from config import config
from flask_cors import CORS

from db import db
# models imports
from api.models.accountModel import AccountModel
# resources imports
from resources.account import Accounts
from resources.login import LogIn
from resources.games import Games, GamesByTitle, GamesByOrder,GameDetail,GameFilters

app = Flask(__name__)
environment = config['development']
if config_decouple('PRODUCTION', cast=bool, default=False):
    environment = config['production']

app.config.from_object(environment)

api = Api(app)
CORS(app, resources={r'/*': {'origins': '*'}})

db.get_instance().init_app(app)
AccountModel.collection = db.get_database.accounts

CONNECTION_STRNG = "mongodb+srv://jromero:050899@geekify.q6113.mongodb.net/test?retryWrites=true&w=majority"
mongo = pymongo.MongoClient(CONNECTION_STRNG, tls=True, tlsAllowInvalidCertificates=True)


@app.errorhandler(404)
def not_found(error=None):
    message = jsonify({
        'message': 'Resource not found: ' + request.url,
        'status': 404,
    })
    message.status_code = 404
    return message


api.add_resource(Accounts, '/account/email/<string:email>', '/account/id/<string:id>', '/account/user')
api.add_resource(LogIn, '/login')

api.add_resource(Games, '/games')
api.add_resource(GameDetail, '/game/<string:id>')
api.add_resource(GamesByTitle, '/games/title/<string:title>')
api.add_resource(GamesByOrder, '/games/filter/<string:order>')
api.add_resource(GameFilters, '/games/filters')
if __name__ == "__main__":
    app.run(port=5000, debug=True)
