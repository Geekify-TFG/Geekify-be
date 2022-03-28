from flask_restful import Resource, reqparse
from api.lock import lock
from api.models.accountModel import AccountModel


class LogIn(Resource):

    def get(self, email=None, password=None, id=None):
        with lock.lock:
            account = AccountModel.find_account(email=email, id=id)
            if account.exists:
                if account.verify_password(password=password):
                    token = account.generate_auth_token()
                    return {'token': token.decode('ascii')}, 200
                return {'message': 'Incorrect password for email [{}] '.format(email)}, 400
            return {'message': "An error occurred. email not found"}, 404

    def post(self, email=None, password=None, id=None):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='This field cannot be left blank')
        parser.add_argument('password', type=str, required=True, help='This field cannot be left blank')
        parser.add_argument('id', type=str, required=False)
        data = parser.parse_args()
        if data:
            try:
                # if any of them not given = fail and the code will raise and exception
                eml = data['email']
                password = data['password']
                # check if optional args are given
                _id = None
                try:
                    _id = data['id']
                except:
                    _id = None

                account = AccountModel.find_account(email=eml, id=_id)
                if account and account.exists:
                    if account.verify_password(password=password):
                        token = account.generate_auth_token()
                        return {'token': token.decode('ascii')}, 200
                    return {'message': 'Incorrect password for email [{}] '.format(eml)}, 400
                return {'message': "An error occurred. Account not found"}, 404
            except Exception as e:
                return {'message': 'An error occurred you send a bad request. {}:{}'.format(type(e), e)}, 400
        return {'message': 'An error occurred parsing arguments.'}, 400

    def delete(self, email=None, id=None, password=None):
        return {'message': "Not developed yet"}, 404

    def put(self, email=None, id=None, password=None):
        return {'message': "Not developed yet"}, 404
