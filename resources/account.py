from flask_restful import Resource, reqparse

from lock import lock
from models.accountModel import AccountModel, auth, g
from models.collectionModel import CollectionModel


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
                    #accounts.add_or_remove_like(id,rate)
                    accounts.add_or_remove_like(id,rate)
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
                    #accounts.add_or_remove_like(id,rate)
                    accounts.update_rate(id,rate)
                return {'message': 'Liked added successfully'}, 201





