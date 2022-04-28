from flask_restful import Resource, reqparse
import requests
from bson import json_util

from lock import lock

API_KEY = '40f3cb2ff2c94a5889d3d6c865415ec5'
api_rawg = "https://api.rawg.io/api/games?key=" + API_KEY
# api_rawg = "https://api.rawg.io/api/games/lists/main?key=" + API_KEY
response = requests.get(api_rawg)


class Calendar(Resource):
    def post(self):
        with lock.lock:
            parser = reqparse.RequestParser()
            parser.add_argument('startMonth', type=str, required=False)
            parser.add_argument('endMonth', type=str, required=False)
            data = parser.parse_args()
            startMonth = data['startMonth'].split('T')[0]
            endMonth = data['endMonth'].split('T')[0]
            api_detail = "https://api.rawg.io/api/games?"
            a = "dates={},{}".format(startMonth, endMonth)
            api_detail += a + '&key=' + API_KEY
            games = requests.get(api_detail).json()
            dataList = games.get('results')
            listFinal = []
            for index in range(len(dataList)):
                game = {'title': dataList[index]['name'], 'date': dataList[index]['released'],
                        'url': dataList[index]['background_image'], 'id': dataList[index]['id']}
                listFinal.append(game)

            try:
                return {'games': listFinal}, 200
            except Exception as e:
                return {
                           'message': 'An error occurred while finding games '
                                      'Error {0}:{1}'.format(type(e), e)
                       }, 404
                return {'message': 'Games does not exists'}, 404
            except Exception as e:
                return {'message': 'Internal server error. Error {0}:{1}'.format(type(e), e)}, 500
