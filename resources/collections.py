from flask_restful import Resource, reqparse
import requests

from lock import lock
from models.accountModel import AccountModel, auth, g

from models.collectionModel import CollectionModel

API_KEY = '40f3cb2ff2c94a5889d3d6c865415ec5'


class Collections(Resource):
    @auth.login_required(role=['user', 'admin'])
    def get(self, id=None):
        with lock.lock:
            try:
                if id:
                    collection = CollectionModel.find_by_id(id)
                    if collection.exists:
                        my_json = collection.json()
                        try:
                            return {'collection': my_json}, 200
                        except Exception as e:
                            return {
                                       'message': 'An error occurred while finding the content of collection. '
                                                  'Error {0}:{1}'.format(type(e), e)
                                   }, 404
                    return {'message': 'Collection does not exists'}, 404
                return {'message': 'No id were provided!'}, 400
            except Exception as e:
                return {'message': 'Internal server error. Error {0}:{1}'.format(type(e), e)}, 500

    @auth.login_required(role=['user', 'admin'])
    def post(self, title=None, id=None):
        with lock.lock:
            parser = reqparse.RequestParser()
            parser.add_argument(CollectionModel.title_col_name, type=str, required=True)
            parser.add_argument(CollectionModel.user_email_col_name, type=str, required=True)
            data = parser.parse_args()
            if data:
                try:
                    title = data[CollectionModel.title_col_name]
                    user_email = data[CollectionModel.user_email_col_name]
                    # email region
                    if title:
                        collection = CollectionModel.find_one_by_column(value=title,
                                                                        col_name=CollectionModel.title_col_name)
                        if collection and collection.exists:
                            # resource already exists
                            return {'message': 'Collection with title [{0}] already exists'.format(title)}, 409
                    else:
                        raise Exception('Error. no email were specified for this account!')
                    # password region

                    try:
                        # create new collection
                        collection = CollectionModel(title=title, user_email=user_email)
                        my_json = collection.save_to_db()
                        return {"collection": my_json}, 201
                    except Exception as e:
                        return {
                                   'message': 'An error occurred creating the collection. {0}:{1}'.format(type(e), e)
                               }, 500
                except Exception as e:
                    return {'message': 'An error occurred you send a bad request. {0}:{1}'.format(type(e), e)}, 400
            return {'message': 'An error occurred parsing arguments.'}, 400

    def delete(self, id=None):
        with lock.lock:
            try:
                if id:
                    collection = CollectionModel.find_by_id(id)

                    try:
                        collection.delete_from_db()
                        return {'message': 'Collection deleted successfully'}, 200
                    except Exception as e:
                        return {
                                   'message': 'An error occurred while finding the content of collection. '
                                              'Error {0}:{1}'.format(type(e), e)
                               }, 404
            except Exception as e:
                return {'message': 'Internal server error. Error {0}:{1}'.format(type(e), e)}, 500

    def put(self, email=None, id=None):
        with lock.lock:
            parser = reqparse.RequestParser()
            parser.add_argument(CollectionModel.title_col_name, type=str, required=False)
            parser.add_argument(CollectionModel.image_col_name, type=str, required=False)
            parser.add_argument(CollectionModel.num_games_col_name, type=str, required=False)
            parser.add_argument(CollectionModel.games_col_name, type=str, required=False)
            parser.add_argument(CollectionModel.user_email_col_name, type=str, required=False)

            parser.add_argument('title', type=str, required=False)
            parser.add_argument('image', type=str, required=False)

            data = parser.parse_args()

            if data:
                try:
                    title = data[CollectionModel.title_col_name] if data[CollectionModel.title_col_name] else None
                    image = data[CollectionModel.image_col_name] if data[CollectionModel.image_col_name] else None

                    collection = CollectionModel.find_collection(user_email=email, id=id)
                    if collection and collection.exists:

                        collection.update_document(
                            title=title, image=image
                        )
                        return {'collection': collection.json()}, 201
                    else:
                        return {'collection': {}}, 404
                except Exception as e:
                    return {'message': 'An error occurred you send a bad request. {}:{}'.format(type(e), e)}, 400
            return {'message': 'An error occurred parsing arguments.'}, 404


class CollectionsList(Resource):
    @auth.login_required(role=['user', 'admin'])
    def get(self, user_email):
        with lock.lock:
            account = AccountModel.find_account(email=user_email)
            if account.exists:
                try:
                    if not (
                            g.user.doc_ref[
                                AccountModel.email_col_name
                            ]
                            ==
                            account.doc_ref[
                                AccountModel.email_col_name
                            ]
                    ):
                        raise PermissionError('Error. User not allowed!')
                except PermissionError as e:
                    return {'message': f'{type(e)}:{e}'}, 403  # forbidden
                except Exception as e:
                    return {'message': f'Error: {type(e)}:{e}'}, 500
                try:
                    ret = CollectionModel.find_by_useremail(user_email=user_email)
                    return {'collections': [ret[key].json() for key in ret.keys()]}, 200
                except:
                    return {'message': 'Collection of collections not found'}, 400
            else:
                return {'message': 'Account with given email does not exist'}, 404


class CollectionGame(Resource):
    def post(self, id=None):
        with lock.lock:
            try:
                parser = reqparse.RequestParser()
                parser.add_argument('game_id', type=str, required=False)
                data = parser.parse_args()
                game_id = data['game_id']
                api_detail = "https://api.rawg.io/api/games/" + game_id + "?key=" + API_KEY
                game_detail = requests.get(api_detail).json()
                collection = CollectionModel.find_collection(id=id)
                # Get values of the dic
                #Check if the game_id is already in the collection
                if any(d['id'] == int(game_id) for d in collection.json()['value']['games']):
                        return {'message': 'Game already in collection'}, 409
                else:
                    collection.add_game_collection( game_detail=game_detail)
                    return {'message': 'Collection updated successfully'}, 201
            except Exception as e:
                return {'message': 'Internal server error. Error {0}:{1}'.format(type(e), e)}, 500

    def put(self, id=None):
        with lock.lock:
            try:
                parser = reqparse.RequestParser()
                parser.add_argument('game_id', type=str, required=False)
                data = parser.parse_args()
                game_id = data['game_id']
                api_detail = "https://api.rawg.io/api/games/" + game_id + "?key=" + API_KEY
                game_detail = requests.get(api_detail).json()
                collection = CollectionModel.find_collection(id=id)
                # Get values of the dic
                #Check if the game_id is already in the collection
                
                collection.delete_game_collection(game_detail=game_detail)
                return {'message': 'Game deleted successfully'}, 201
            except Exception as e:
                return {'message': 'Internal server error. Error {0}:{1}'.format(type(e), e)}, 500