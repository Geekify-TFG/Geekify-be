import requests
from flask_restful import Resource, reqparse

from lock import lock
from models.accountModel import  AccountModel, auth
from models.commentModel import CommentModel

API_KEY = '40f3cb2ff2c94a5889d3d6c865415ec5'


class Comments(Resource):

    def get(self, id=None):
        with lock.lock:
            try:
                if id:
                    comment = CommentModel.find_by_id(id)
                    if comment.exists:
                        my_json = comment.json()
                        try:
                            return {'comment': my_json}, 200
                        except Exception as e:
                            return {
                                       'message': 'An error ocurred while finding the comment. '
                                                  'Error {}:{}'.format(type(e), e)
                                   }, 404
                    return {'message': 'Comment does not exists'}, 404
                return {'message': 'No id were provided!'}, 400
            except Exception as e:
                return {'message': 'Internal server error. Error {}:{}'.format(type(e), e)}, 500

    @auth.login_required(role=['user', 'admin'])
    def post(self, id=None):
        with lock.lock:
            parser = reqparse.RequestParser()

            parser.add_argument('date', type=str, required=True, help="This field cannot be left blank.")
            parser.add_argument('content', type=str, required=True, help="This field cannot be left blank.")
            parser.add_argument('user', type=str, required=True, help="This field cannot be left blank.")
            parser.add_argument('game_id', type=str, required=True, help="This field cannot be left blank.")

            data = parser.parse_args()
            if data:
                date = data['date']
                content = data['content']
                user = data['user']
                game_id = data['game_id']

                if user:
                    accounts = AccountModel.find_account(email=user)
                    username = accounts.json().get('value').get('name')
                    image_user = accounts.json().get('value').get('photo')

                    if accounts.exists:
                        api_game = "https://api.rawg.io/api/games/" + id + "?key=" + API_KEY
                        response = requests.get(api_game)
                        if response.status_code == 200:
                            try:
                                comment = CommentModel(date, content, username, game_id,image_user)
                                my_json = comment.save_to_db()
                                if comment and comment.exists:
                                    try:
                                        return {'comment': my_json}, 201
                                    except Exception as e:
                                        comment.delete_from_db()
                                        return {
                                                   'message': 'Internal server error. Could not create comment due an '
                                                              'Error. '
                                                              'Error {0}:{1}'.format(type(e), e)
                                               }, 500
                                else:
                                    return {
                                               'message': 'Internal server error. Could not create comment. Unknown '
                                                          'error'
                                           }, 500
                            except Exception as e:

                                return {
                                           'message': 'Internal server error. Could not create comment due an Error. '
                                                      'Error {0}:{1}'.format(type(e), e)
                                       }, 500
                        else:
                            return {'message': 'Game not found.'}, 403
                return {'message': 'User not found.'}, 404
            return

    def delete(self, id):
        with lock.lock:
            try:
                if id:
                    CommentModel.delete_by_id(id)
                return {'message': 'Comment deleted successfully'}, 200
            except Exception as e:
                return {'message': 'Internal server error. Error {}:{}'.format(type(e), e)}, 500

    def put(self, id):
        with lock.lock:
            parser = reqparse.RequestParser()

            parser.add_argument('date', type=str, required=True, help="This field cannot be left blank.")
            parser.add_argument('content', type=str, required=True, help="This field cannot be left blank.")
            parser.add_argument('user', type=str, required=True, help="This field cannot be left blank.")
            parser.add_argument('publication_id', type=str, required=True, help="This field cannot be left blank.")

            data = parser.parse_args()
            if data:
                date = data['date']
                content = data['content']
                user = data['user']
                publication_id = data['publication_id']

                if user:
                    accounts = AccountModel.find_account(email=user)
                    if accounts.exists:
                        publication = PublicationModel.find_by_id(publication_id)
                        if publication.exists:
                            try:
                                comment = CommentModel(date, content, user, publication_id)
                                my_json = comment.save_to_db()
                                if comment and comment.exists:
                                    try:
                                        comment_replied = CommentModel.find_by_id(id)
                                        if comment_replied and comment_replied.exists:
                                            comment_replied.add_reply_comment_id(comment.get_id())
                                            return {'comment': my_json}, 201
                                        else:
                                            return {
                                                       'message': 'The comment you are replying to does not exist'
                                                                  'error'
                                                   }, 500
                                    except Exception as e:
                                        comment.delete_from_db()
                                        return {
                                                   'message': 'Internal server error. Could not create comment due an '
                                                              'Error. '
                                                              'Error {0}:{1}'.format(type(e), e)
                                               }, 500
                                else:
                                    return {
                                               'message': 'Internal server error. Could not create comment. Unknown '
                                                          'error'
                                           }, 500
                            except Exception as e:

                                return {
                                           'message': 'Internal server error. Could not create comment due an Error. '
                                                      'Error {0}:{1}'.format(type(e), e)
                                       }, 500
                        else:
                            return {'message': 'Publication not found.'}, 403
                return {'message': 'User not found.'}, 404
            return


class CommentsList(Resource):

    def get(self):
        with lock.lock:
            try:
                ret = CommentModel.get_all()
                if len(ret) == 0:
                    return {'comments': {}}, 204
                return {'comments': {key: ret[key].json()[key] for key in ret.keys()}}, 202
            except Exception as e:
                return {'message': 'Internal server error {0}:{1}'.format(type(e), e)}, 500
