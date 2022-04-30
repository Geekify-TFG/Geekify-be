from flask_restful import Resource, reqparse
import requests

from lock import lock
from models.accountModel import AccountModel, auth, g
from models.collectionModel import CollectionModel
from models.forumModel import ForumModel

from models.commentModel import CommentModel

API_KEY = '40f3cb2ff2c94a5889d3d6c865415ec5'


class AccountsInfo(Resource):

    def get(self, email=None):
        with lock.lock:
            try:
                account = AccountModel.find_account(email=email)
                if account.exists:
                    my_json = account.json()
                    email = my_json['value']['email']
                    photo = my_json['value']['photo']
                    return {'account': {'email': email, 'photo': photo}}, 200
                else:
                    return {'account': {}}, 404  # not found
            except Exception as e:
                return {'message': 'Account with email [{0}] doesn\'t exists'.format(email)}, 404


class Accounts(Resource):

    def get(self, email=None, id=None):
        with lock.lock:
            try:
                account = AccountModel.find_account(email=email, id=id)

                my_json = account.json().get('value')
                return {'account': my_json}, 200
            except Exception as e:
                return {'message': 'Account with email [{0}] doesn\'t exists'.format(email)}, 404

    def post(self, email=None, id=None):
        with lock.lock:
            parser = reqparse.RequestParser()
            parser.add_argument(AccountModel.email_col_name, type=str, required=True)
            parser.add_argument(AccountModel.pass_col_name, type=str, required=True)
            parser.add_argument(AccountModel.name_col_name, type=str, required=True)
            data = parser.parse_args()
            if data:
                try:
                    eml = data[AccountModel.email_col_name]
                    password = data[AccountModel.pass_col_name]
                    name = data[AccountModel.name_col_name]
                    # email region
                    if eml:
                        account = AccountModel.find_one_by_column(value=eml, col_name=AccountModel.email_col_name)
                        if account and account.exists:
                            # resource already exists
                            return {'message': 'Account with email [{0}] already exists'.format(eml)}, 409
                    else:
                        raise Exception('Error. no email were specified for this account!')
                    # password region
                    if password:
                        # check password (if completes out rules)
                        # password region
                        try:
                            # create new account
                            account = AccountModel(email=eml, password=password, name=name)
                            collection = CollectionModel(title="Favorites", user_email=eml)
                            collection.save_to_db()
                            account.hash_password()
                            my_json = account.save_to_db()
                            return {"account": my_json}, 201
                        except Exception as e:
                            return {
                                       'message': 'An error occurred creating the account. {0}:{1}'.format(type(e), e)
                                   }, 500
                    else:
                        raise Exception('Error. no password were specified for this account!')
                except Exception as e:
                    return {'message': 'An error occurred you send a bad request. {0}:{1}'.format(type(e), e)}, 400
            return {'message': 'An error occurred parsing arguments.'}, 400


class AccountLike(Resource):

    def post(self, id=None):
        with lock.lock:
            parser = reqparse.RequestParser()

            parser.add_argument('rate', type=int, required=False, help="This field cannot be left blank.")
            parser.add_argument('user', type=str, required=False, help="This field cannot be left blank.")

            data = parser.parse_args()
            if data:
                rate = data['rate']
                user = data['user']
                if user:
                    accounts = AccountModel.find_account(email=user)
                    # accounts.add_or_remove_like(id,rate)
                    accounts.add_or_remove_like(id, rate)
                return {'message': 'Liked added successfully'}, 201

    def put(self, id=None):
        with lock.lock:
            parser = reqparse.RequestParser()

            parser.add_argument('rate', type=int, required=False, help="This field cannot be left blank.")
            parser.add_argument('user', type=str, required=False, help="This field cannot be left blank.")

            data = parser.parse_args()
            if data:
                rate = data['rate']
                user = data['user']
                if user:
                    accounts = AccountModel.find_account(email=user)
                    # accounts.add_or_remove_like(id,rate)
                    accounts.update_rate(id, rate)
                return {'message': 'Liked added successfully'}, 201


class AccountForums(Resource):

    # @auth.login_required(role=['user', 'admin'])
    def get(self, email=None):
        with lock.lock:
            try:
                account = AccountModel.find_account(email=email)
                forums_followed = account.get_forums_followed()
                forums_followeds = []
                for i in forums_followed:
                    a = ForumModel.find_forum(id=i)
                    # if a.json().get('id') != 'None':
                    forums_followeds.append(a.json())
                    # else:
                    #   account.remove_forum_followed(forum=i)

                return {'forums_followed': forums_followeds}, 200
            except Exception as e:
                return {'message': 'An error occurred you send a bad request. {0}:{1}'.format(type(e), e)}, 400

    # @auth.login_required(role=['user', 'admin'])
    def post(self, email=None):
        with lock.lock:
            email_name = AccountModel.email_col_name
            forums_followed = AccountModel.forums_followed_col_name
            parser = reqparse.RequestParser()
            parser.add_argument(email_name, type=str, required=False, help='This field cannot be left blank')
            parser.add_argument(forums_followed, type=str, required=True, help='This field cannot be left blank')
            data = parser.parse_args()
            if data:
                try:
                    eml = data[email_name] if data[email_name] else None
                    new_forum = data[forums_followed] if data[forums_followed] else None

                    if new_forum:
                        try:
                            accounts = AccountModel.find_account(email=email)
                            forum = ForumModel.find_forum(id=new_forum)
                            forum.add_or_remove_user_followed(user=email)
                            accounts.add_or_remove_forum_followed(forum=new_forum)
                            return {"account": accounts.json()}, 201
                        except Exception as e:
                            return {'message': 'Error {0}: {1}'.format(type(e), e)}, 404
                    else:
                        raise Exception('Error. No Author Email were specified!')

                except Exception as e:
                    return {'message': 'An error occurred you send a bad request. {0}:{1}'.format(type(e), e)}, 400
            return {'message': 'An error occurred parsing arguments.'}, 404


class AccountInfo(Resource):
    def get(self, email=None):
        with lock.lock:
            try:
                account = AccountModel.find_account(email=email)
                if account.exists:
                    my_json = account.json()
                    email = my_json['value']['email']
                    photo = my_json['value']['photo']
                    user = email.split('@')[0]
                    if (my_json['value']['gender'] != None):
                        # Know game of the comment
                        comment = CommentModel.find_by_user(user)
                        if comment.json() != None:
                            b = comment.json()
                            game_id = list(b.values())[0].get('game_id')
                            api_detail = "https://api.rawg.io/api/games/" + game_id + "?key=" + API_KEY
                            game_detail = requests.get(api_detail).json()
                            list(b.values())[0]['game_comment'] = game_detail
                            my_json.get('value')['comment'] = b
                        # Know collections
                        ret = CollectionModel.find_by_useremail(user_email=email)
                        a = ([ret[key].json() for key in ret.keys()])
                        my_json.get('value')['collections'] = a

                        top_games = my_json.get('value')['top_games']
                        all_games = []
                        for i in top_games:
                            game = requests.get("https://api.rawg.io/api/games/" + i + "?key=" + API_KEY).json()
                            all_games.append(game)

                        my_json.get('value')['all_games'] = all_games
                        del my_json.get('value')['password']
                    return {'account': my_json}, 200
                else:
                    return {'account': {}}, 404  # not found
            except Exception as e:
                return {'message': 'Account with email [{0}] doesn\'t exists'.format(email)}, 404

    def put(self, email=None):
        with lock.lock:
            parser = reqparse.RequestParser()
            parser.add_argument(AccountModel.photo_col_name, type=str, required=False,
                                help="This field cannot be left blank.")
            parser.add_argument(AccountModel.name_col_name, type=str, required=False,
                                help="This field cannot be left blank.")
            parser.add_argument(AccountModel.gender_col_name, type=str, required=False,
                                help="This field cannot be left blank.")
            parser.add_argument(AccountModel.birthday_col_name, type=str, required=False,
                                help="This field cannot be left blank.")
            parser.add_argument(AccountModel.location_col_name, type=str, required=False,
                                help="This field cannot be left blank.")
            parser.add_argument(AccountModel.fav_categories_col_name, action='append', help='<Required> Set flag',
                                required=False)
            parser.add_argument(AccountModel.top_games_col_name, action='append', help='<Required> Set flag',
                                required=False)

            data = parser.parse_args()
            if data:
                name = data[AccountModel.name_col_name] if data[AccountModel.name_col_name] else None
                photo = data[AccountModel.photo_col_name] if data[AccountModel.photo_col_name] else None
                gender = data[AccountModel.gender_col_name] if data[AccountModel.gender_col_name] else None
                birthday = data[AccountModel.birthday_col_name] if data[AccountModel.birthday_col_name] else None
                location = data[AccountModel.location_col_name] if data[AccountModel.location_col_name] else None
                fav_categories = data[AccountModel.fav_categories_col_name] if data[AccountModel.fav_categories_col_name] else None
                top_games = data[AccountModel.top_games_col_name] if data[AccountModel.top_games_col_name] else None
                try:
                    account = AccountModel.find_account(email=email)
                    if account and account.exists:
                        account.update_document(photo=photo,name=name, gender=gender, birthday=birthday, location=location,
                                                fav_categories=fav_categories, top_games=top_games)
                    return {'message': 'Account updated successfully'}, 201
                except Exception as e:
                    return {'message': 'An error occurred you send a bad request. {}:{}'.format(type(e), e)}, 400


class AccountCalendar(Resource):

    # @auth.login_required(role=['user', 'admin'])
    def get(self, email=None):
        with lock.lock:
            try:
                account = AccountModel.find_account(email=email)
                calendar_releases = account.get_calendar_releases()

                return {'calendar_releases': calendar_releases}, 200
            except Exception as e:
                return {'message': 'An error occurred you send a bad request. {0}:{1}'.format(type(e), e)}, 400

    # @auth.login_required(role=['user', 'admin'])
    def post(self, email=None):
        with lock.lock:
            parser = reqparse.RequestParser()
            parser.add_argument('game_id', type=str, required=False, help='This field cannot be left blank')
            parser.add_argument('game_title', type=str, required=True, help='This field cannot be left blank')
            parser.add_argument('game_image', type=str, required=True, help='This field cannot be left blank')
            parser.add_argument('game_date', type=str, required=True, help='This field cannot be left blank')
            data = parser.parse_args()
            if data:
                game_id = int(data['game_id'])
                game_title = data['game_title']
                game_image = data['game_image']
                game_date = data['game_date']

                try:
                    accounts = AccountModel.find_account(email=email)
                    accounts.add_or_remove_calendar_releases(game_id=game_id, game_title=game_title,
                                                             game_image=game_image, game_date=game_date)
                    calendar_releases = accounts.get_calendar_releases()
                    return {"account": calendar_releases}, 201

                except Exception as e:
                    return {'message': 'An error occurred you send a bad request. {0}:{1}'.format(type(e), e)}, 400
            return {'message': 'An error occurred parsing arguments.'}, 404
