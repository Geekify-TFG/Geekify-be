from flask_restful import Resource, reqparse
import requests

from lock import lock
from models.accountModel import AccountModel, auth, g

from models.forumModel import ForumModel


class Forum(Resource):
    #@auth.login_required(role=['user', 'admin'])
    def get(self, id=None):
        with lock.lock:
            try:
                if id:
                    collection = ForumModel.find_by_id(id)
                    if collection.exists:
                        my_json = collection.json()
                        try:
                            return {'forum': my_json}, 200
                        except Exception as e:
                            return {
                                       'message': 'An error occurred while finding the content of forum. '
                                                  'Error {0}:{1}'.format(type(e), e)
                                   }, 404
                    return {'message': 'Forum does not exists'}, 404
                return {'message': 'No id were provided!'}, 400
            except Exception as e:
                return {'message': 'Internal server error. Error {0}:{1}'.format(type(e), e)}, 500

    #@auth.login_required(role=['user', 'admin'])
    def post(self, title=None, id=None):
        with lock.lock:
            parser = reqparse.RequestParser()
            parser.add_argument(ForumModel.title_col_name, type=str, required=True)
            parser.add_argument(ForumModel.description_col_name, type=str, required=True)
            parser.add_argument(ForumModel.image_col_name, type=str, required=False)
            parser.add_argument(ForumModel.tag_col_name, type=str, required=True)
            parser.add_argument(ForumModel.game_col_name, type=str, required=True)
            parser.add_argument(ForumModel.admin_col_name, type=str, required=True)
            data = parser.parse_args()
            if data:
                try:
                    title = data[ForumModel.title_col_name]
                    description = data[ForumModel.description_col_name]
                    image = data[ForumModel.image_col_name]
                    tag = data[ForumModel.tag_col_name]
                    game = data[ForumModel.game_col_name]
                    admin = data[ForumModel.admin_col_name]
                    # email region
                    if title:
                        forum = ForumModel.find_one_by_column(value=title,
                                                              col_name=ForumModel.title_col_name)
                        if forum and forum.exists:
                            # resource already exists
                            return {'message': 'Forum with title [{0}] already exists'.format(title)}, 409
                    else:
                        raise Exception('Error. no email were specified for this account!')
                    # password region

                    try:
                        # create new collection
                        forum = ForumModel(title=title, description=description, image=image, tag=tag, game=game,
                                           admin=admin)
                        my_json = forum.save_to_db()
                        return {"forum": my_json}, 201
                    except Exception as e:
                        return {
                                   'message': 'An error occurred creating the forum. {0}:{1}'.format(type(e), e)
                               }, 500
                except Exception as e:
                    return {'message': 'An error occurred you send a bad request. {0}:{1}'.format(type(e), e)}, 400
            return {'message': 'An error occurred parsing arguments.'}, 400

    def delete(self, id=None):
        with lock.lock:
            try:
                if id:
                    forum = ForumModel.find_by_id(id)

                    try:
                        forum.delete_from_db()
                        return {'message': 'Forum deleted successfully'}, 200
                    except Exception as e:
                        return {
                                   'message': 'An error occurred while finding the content of forum. '
                                              'Error {0}:{1}'.format(type(e), e)
                               }, 404
            except Exception as e:
                return {'message': 'Internal server error. Error {0}:{1}'.format(type(e), e)}, 500




class ForumsList(Resource):
    def get(self):
        with lock.lock:
            try:
                ret = ForumModel.get_all()
                if len(ret) == 0:
                    return {'forums': {}}, 204
                return {'forums': {key: ret[key].json()['value'] for key in ret.keys()}}, 202
            except Exception as e:
                return {'message': 'Internal server error {0}:{1}'.format(type(e), e)}, 500


