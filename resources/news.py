from flask_restful import Resource, reqparse
import requests
from bson import json_util

from lock import lock

API_KEY = '7c832cfb4078497f87bc53eec73c90d1'
api_news = "https://newsapi.org/v2/everything?apiKey=" + API_KEY
# api_rawg = "https://api.rawg.io/api/games/lists/main?key=" + API_KEY
response = requests.get(api_news)



class News(Resource):
    def get(self):
        with lock.lock:
            try:
                filter_news = api_news + "&q=videogames&language=en&sortBy=popularity"
                news = requests.get(filter_news)
                if news:
                    my_json = news.json()
                    try:
                        return {'news': my_json}, 200
                    except Exception as e:
                        return {
                                   'message': 'An error occurred while finding news '
                                              'Error {0}:{1}'.format(type(e), e)
                               }, 404
                return {'message': 'news does not exists'}, 404
            except Exception as e:
                return {'message': 'Internal server error. Error {0}:{1}'.format(type(e), e)}, 500
