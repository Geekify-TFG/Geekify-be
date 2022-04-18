import requests
from flask_restful import Resource, reqparse

from lock import lock
from models.accountModel import AccountModel, auth
from models.commentModel import CommentModel

from models.publicationModel import PublicationModel

from models.forumModel import ForumModel

API_KEY = '40f3cb2ff2c94a5889d3d6c865415ec5'


class Publications(Resource):

    def get(self, id=None):
        with lock.lock:
            try:
                if id:
                    publication = PublicationModel.find_by_id(id)
                    if publication.exists:
                        my_json = publication.json()
                        try:
                            return {'publication': my_json}, 200
                        except Exception as e:
                            return {
                                       'message': 'An error ocurred while finding the publication. '
                                                  'Error {}:{}'.format(type(e), e)
                                   }, 404
                    return {'message': 'Comment does not exists'}, 404
                return {'message': 'No id were provided!'}, 400
            except Exception as e:
                return {'message': 'Internal server error. Error {}:{}'.format(type(e), e)}, 500

    # @auth.login_required(role=['user', 'admin'])
    def post(self, id=None):
        with lock.lock:
            parser = reqparse.RequestParser()

            parser.add_argument('date', type=str, required=True, help="This field cannot be left blank.")
            parser.add_argument('content', type=str, required=True, help="This field cannot be left blank.")
            parser.add_argument('user', type=str, required=True, help="This field cannot be left blank.")
            # parser.add_argument('forum_id', type=str, required=True, help="This field cannot be left blank.")

            data = parser.parse_args()
            if data:
                date = data['date']
                content = data['content']
                user = data['user']
                forum_id = id
                if user:
                    accounts = AccountModel.find_account(email=user)
                    username = accounts.json().get('value').get('name')
                    image_user = accounts.json().get('value').get('photo')

                    if accounts.exists:
                        try:
                            publication = PublicationModel(date, content, username, forum_id, image_user)
                            forum = ForumModel.find_forum(id=forum_id)
                            my_json = publication.save_to_db()
                            forum.add_or_remove_publication(publication=my_json)

                            if publication and publication.exists:
                                try:
                                    return {'comment': my_json}, 201
                                except Exception as e:
                                    publication.delete_from_db()
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
                    PublicationModel.delete_by_id(id)
                return {'message': 'Comment deleted successfully'}, 200
            except Exception as e:
                return {'message': 'Internal server error. Error {}:{}'.format(type(e), e)}, 500


class ForumPublications(Resource):

    def get(self, id):
        with lock.lock:
            try:
                ret = PublicationModel.find_by_forum(id)
                if len(ret) == 0:
                    return {'publications': {}}, 204
                return {'publications': {key: ret[key].json()[key] for key in ret.keys()}}, 202
            except Exception as e:
                return {'message': 'Internal server error {0}:{1}'.format(type(e), e)}, 500


class ForumPublicationLike(Resource):

    def post(self, id):
        with lock.lock:
            parser = reqparse.RequestParser()

            parser.add_argument('email', type=str, required=True, help="This field cannot be left blank.")

            data = parser.parse_args()
            try:
                user = data['email']
                ret = PublicationModel.find_publication(id)
                ret.add_or_remove_like_publication(user)

                return {'publications': ret.json()}, 202
            except Exception as e:
                return {'message': 'Internal server error {0}:{1}'.format(type(e), e)}, 500
