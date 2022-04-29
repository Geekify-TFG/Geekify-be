from flask_restful import Resource, reqparse
import requests
from bson import json_util

from lock import lock
from models.accountModel import AccountModel
from models.commentModel import CommentModel

API_KEY = '40f3cb2ff2c94a5889d3d6c865415ec5'
api_rawg = "https://api.rawg.io/api/games?key=" + API_KEY
# api_rawg = "https://api.rawg.io/api/games/lists/main?key=" + API_KEY
response = requests.get(api_rawg)


class Games(Resource):
    def get(self):
        with lock.lock:
            try:
                games = requests.get(api_rawg)
                if games:
                    my_json = games.json()
                    try:
                        return {'games': [my_json]}, 200
                    except Exception as e:
                        return {
                                   'message': 'An error occurred while finding games '
                                              'Error {0}:{1}'.format(type(e), e)
                               }, 404
                return {'message': 'Games does not exists'}, 404
            except Exception as e:
                return {'message': 'Internal server error. Error {0}:{1}'.format(type(e), e)}, 500


class GamesByTitle(Resource):

    def get(self, title):

        with lock.lock:
            try:
                if title is None:
                    return {'games': {}}, 204
                else:
                    api_search = "https://api.rawg.io/api/games?key=" + API_KEY + "&search=" + title + "&ordering=-added&search_exact=true"
                    games = requests.get(api_search).json()
                    return {'games': games}, 200
            except:
                return {'message': 'Collection of games not found'}, 500


class GamesByOrder(Resource):
    # Orders: Popular,release date,rating
    def get(self, order):
        with lock.lock:
            try:
                if order.upper() == "POPULAR":
                    games = requests.get(api_rawg)
                    my_json = games.json()
                    return {'games': my_json}, 200
                if order.upper() == "RELEASED":
                    api_release = "https://api.rawg.io/api/games?ordering=-" + order + "&key=" + API_KEY
                    games = requests.get(api_release)
                    my_json = games.json()
                    return {'games': my_json}, 200
                if order.upper() == "RATING":
                    api_release = "https://api.rawg.io/api/games?ordering=-" + order + "&key=" + API_KEY
                    games = requests.get(api_release)
                    my_json = games.json()
                    return {'games': my_json}, 200
            except:
                return {'message': 'Collection of games not found'}, 500


class GameDetail(Resource):

    def get(self, id):
        with lock.lock:
            try:
                if id is None:
                    return {'games': {}}, 204
                else:
                    api_detail = "https://api.rawg.io/api/games/" + id + "?key=" + API_KEY
                    game_detail = requests.get(api_detail).json()
                    api_achievements = "https://api.rawg.io/api/games/" + id + "/achievements?key=" + API_KEY
                    game_achievements = requests.get(api_achievements).json()
                    api_images = "https://api.rawg.io/api/games/" + id + "/screenshots?key=" + API_KEY
                    game_images = requests.get(api_images).json()
                    list = []
                    list.append(game_detail)
                    achievements = {"achievements: ": game_achievements['results']}
                    images = {"images: ": game_images['results']}
                    list.append(achievements)
                    list.append(images)
                    return {'gameDetail': list}, 200
            except:
                return {'message': 'Collection of games not found'}, 500


class GameFilters(Resource):
    # platform : [playstation,nintendo,xbox,pc,others]
    # genres : [action,adventure,shooter,puzzle,rpg,indie,strategy,family,sports,fighting]
    # num_players : [ 1,2,3]
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dates', action='append', help='<Required> Set flag', required=True)
        parser.add_argument('metacritic', action='append', help='<Required> Set flag', required=True)
        parser.add_argument('parent_platforms', action='append', help='<Required> Set flag', required=False)
        parser.add_argument('genres', action='append', help='<Required> Set flag', required=False)
        parser.add_argument('tags', action='append', help='<Required> Set flag', required=False)
        args = parser.parse_args()

        release_year = args['dates']
        rating = args['metacritic']
        platform = args['parent_platforms']
        genres = args['genres']
        num_players = args['tags']
        a = {}
        if release_year:
            a["dates"] = release_year
        if rating:
            a["metacritic"] = rating
        if platform:
            a["parent_platforms"] = platform
        if genres:
            a["genres"] = genres
        if num_players:
            a["tags"] = num_players
        api_detail = "https://api.rawg.io/api/games?"
        api_url = ""
        for i in a:
            api_url += i + "="
            for v in a[i]:
                if v == a[i][-1]:
                    api_url += v
                else:
                    api_url += v + ","
            api_url += "&"
        api_detail += api_url + "ordering=-metacritic&key=" + API_KEY
        games = requests.get(api_detail).json()
        return {'games': games}, 200


class GameCommentsList(Resource):

    def get(self, id):
        with lock.lock:
            try:
                ret = CommentModel.find_by_game(id)
                if len(ret) == 0:
                    return {'comments': {}}, 204
                return {'comments': {key: ret[key].json()[key] for key in ret.keys()}}, 202
            except Exception as e:
                return {'message': 'Internal server error {0}:{1}'.format(type(e), e)}, 500


class ListMostPopularGames(Resource):

    def get(self, id=4):
        try:
            list_games = []
            for i in range(1, int(id)):
                api_rawg = "https://api.rawg.io/api/games?page={0}&key=".format(i) + API_KEY
                games = requests.get(api_rawg)
                my_json = games.json().get("results")
                for index in range(len(my_json)):
                    list_games.append({'id': my_json[index]['id'], 'name': my_json[index]['name']})
            return {'games': list_games}, 200
        except Exception as e:
            return {'message': 'Internal server error {0}:{1}'.format(type(e), e)}, 500


class GamesAccordingFav(Resource):
    def get(self, email):
        try:
            account = AccountModel.find_account(email=email)
            #Get fav_categories from account
            fav_categories = account.get_fav_categories()
            #Check if fav_categories is empty
            if len(fav_categories) == 0:
                return {'message': 'No categories found'}, 204
            else:
                api_url="genres="
                for i in range(len(fav_categories)):
                    if i == len(fav_categories)-1:
                        api_url += fav_categories[i].lower()
                    else:
                        api_url += fav_categories[i].lower() + ","
                api_detail = "https://api.rawg.io/api/games?" + api_url + "ordering=-metacritic&key=" + API_KEY
                games = requests.get(api_detail)
                my_json = games.json().get("results")
                return {'games': my_json}, 200
        except Exception as e:
            return {'message': 'Internal server error {0}:{1}'.format(type(e), e)}, 500

