import os
from datetime import date

from flask import g, current_app
from flask_httpauth import HTTPBasicAuth
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context

from models.abstract.model_definition import DocumentModel

auth = HTTPBasicAuth()

'''
    account model specially is converted and protected as it were a relational model 
    all attribute are defined here and is a must have value
    account (email, password(encrypted), name, ...)
'''


class AccountModel(DocumentModel):
    """
    class representing account model.
    mongodb - collection called accounts
    """
    __column_names__ = ['email', 'password', 'name',
                        'initial_date', 'photo', 'is_admin', 'likes']

    # columns is a dict where the value for each column are referenced
    email_col_name = __column_names__[0]
    pass_col_name = __column_names__[1]
    name_col_name = __column_names__[2]
    initial_date_col_name = __column_names__[3]
    photo_col_name = __column_names__[4]
    admin_col_name = __column_names__[5]
    likes_col_name = __column_names__[6]

    __password_hashed__ = False

    def __init__(
            self,
            password=None,
            email=None,
            name=None,
            photo='https://source.unsplash.com/random',
            doc=None,
            is_admin=0,
            likes=[]
    ):
        super(AccountModel, self).__init__(doc)
        columns = dict.fromkeys(self.__column_names__)
        if doc:
            dic = dict.fromkeys(self.__column_names__)
            dic.update(self.doc_ref)
            self.set_doc_ref(dic.copy())  # make sure doc_ref have all columns
            try:
                self.doc_ref[u'{0}'.format(self.admin_col_name)] = int(self.doc_ref[u'{0}'.format(self.admin_col_name)])
                # -- check all args are there in case missing args throw exception -- this can omitted --
                for col in self.__column_names__:
                    columns[col] = self.doc_ref[u'{0}'.format(col)]
            except Exception as e:
                raise Exception('missing arguments! \n Error  {0}:{1}'.format(type(e), e))
        else:
            columns['{0}'.format(self.email_col_name)] = str(email)
            columns['{0}'.format(self.pass_col_name)] = str(password)
            columns['{0}'.format(self.name_col_name)] = str(name)
            columns['{0}'.format(self.photo_col_name)] = photo
            columns['{0}'.format(self.initial_date_col_name)] = date.today().strftime("%d/%m/%Y")
            columns['{0}'.format(self.admin_col_name)] = int(is_admin)
            columns['{0}'.format(self.likes_col_name)] = likes
            self.set_doc_ref(columns.copy())

    # Create new document -- private method
    def __create(self):
        """
        if it's not created yet then create it otherwise ignore and return json just to have fun
        :return: void
        """
        if not self.exists:
            if not self.__password_hashed__:
                raise Exception('password not hashed. security issue')
            self.set_created()
            my_json = self.json()
            result = self.collection.insert_one(my_json['value'].copy())
            self.set_doc_ref(my_json['value'].copy())
            self.set_id(result.inserted_id)
            my_json['id'] = result.inserted_id.__str__()
            return my_json
        return self.json()

    def json(self):
        return {
            'id': u'{0}'.format(self.get_id()),
            'value':
                {
                    u'{}'.format(col_name): self.doc_ref[col_name]
                    for col_name in self.__column_names__ if self.created
                }
        }

    def save_to_db(self):
        return self.__create()

    def update_document(
            self, password=None, email=None, name=None,
            photo=None, is_admin=None, likes=None

    ):
        # if it's already exists then update
        if self.exists:
            if email:
                self.__update_column__(self.email_col_name, str(email))
            if password:
                self.__hash_password__(str(password))

            if name:
                self.__update_column__(self.name_col_name, str(name))

            if photo:
                self.__update_column__(self.photo_col_name, str(photo))
            if is_admin:
                self.__update_column__(self.admin_col_name, int(is_admin))

            if likes:
                self.__update_column__(self.likes_col_name, likes)
            self.collection.find_one_and_update(
                {'_id': self.id},
                {
                    '$set': self.doc_ref
                }
            )

    @classmethod
    def update_by_id(
            cls,
            id,
            password=None,
            email=None,
            name=None,
            photo=None,
            is_admin=None
    ):
        account = cls.find_by_id(id)
        if account.exists:
            account.update_document(
                password=password,
                email=email,
                name=name,
                photo=photo,
                is_admin=is_admin
            )

    def delete_from_db(self):
        super(AccountModel, self).delete_from_db()

    def add_like(self, game, rate):
        self.collection.find_one_and_update(
            {'_id': self.id},
            {
                '$push': {
                    "likes": {'game_id': game, 'rating': rate}
                }

            }
        )

    def get_likes(self):
        return self.get_column(col_name='likes', col_type=list)

    def add_or_remove_like(self, game, rate):
        my_likes = self.get_likes()
        my_likes.append({'game_id': game, 'rating': rate})
        self.update_document(likes=my_likes)

    def update_rate(self, game, rate):
        my_likes = self.get_likes()
        new_rate = ([item for item in my_likes if item.get('game_id') != game])
        new_rate.append({'game_id': game, 'rating': rate})
        self.update_document(likes=new_rate)

    def remove_like(self, game):
        my_likes = self.get_likes()
        print(my_likes)
        my_likes.remove({"key": game})

        self.update_document(likes=my_likes)

    @classmethod
    def find_account(cls, email=None, id=None):
        try:
            if email:
                account = cls.find_one_by_column(email, cls.email_col_name)
            elif id:
                account = cls.find_by_id(id)
            else:
                raise ValueError(
                    "You need to give one the following: "
                    "an existing email or existing user id"
                )
        except Exception as e:
            account = AccountModel()
        return account

    def hash_password(self):
        self.__hash_password__(self.doc_ref[u'{0}'.format(self.pass_col_name)])
        self.__password_hashed__ = True

    def __hash_password__(self, password):
        self.doc_ref[u'{0}'.format(self.pass_col_name)] = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.doc_ref[u'{0}'.format(self.pass_col_name)])

    def generate_auth_token(self, expiration=3600):
        s = Serializer(current_app.secret_key, expires_in=expiration)
        return s.dumps({'{}'.format(self.email_col_name): self.doc_ref[self.email_col_name]})

    @classmethod
    def verify_auth_token(cls, token):
        s = Serializer(current_app.secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token

        user = cls.find_one_by_column(value=data[cls.email_col_name], col_name=cls.email_col_name)
        return user


@auth.verify_password
def verify_password(token, password):
    account = AccountModel.verify_auth_token(token)
    if account and account.exists:  # and account.verify_password(password=password):
        g.user = account
        if password and account.verify_password(password=password):
            g.user = account
        return account


@auth.get_user_roles
def get_user_roles(user):
    if user and type(user) is AccountModel:
        if user.doc_ref[user.admin_col_name] == 1:
            return ['admin']
        else:
            return ['user']
