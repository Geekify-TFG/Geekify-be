import threading
import pymongo
from flask import Flask


class DataBase(object):
    db = None
    app = None
    __lock = threading.Lock()
    __instance = None

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            with cls.__lock:
                if not cls.__instance:
                    cls.__instance = cls()
        return cls.__instance

    def __init__(self):
        if DataBase.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            DataBase.__instance = self

    def init_app(self, app):
        if not app or not isinstance(app, Flask):
            raise TypeError("Invalid Flask application instance")
        self.app = app
        app.extensions = getattr(app, "extensions", {})
        if not self.db:
            self.__connect_db()

    @property
    def get_database(self):
        if not self.db:
            self.__connect_db()
        return self.db

    def __connect_db(self):
        user = self.app.config.get('DB_USER')
        password = self.app.config.get('DB_PASSWORD')
        host = self.app.config.get('DB_HOST')
        db_name = self.app.config.get('DB_NAME')
        rights = self.app.config.get('DB_RIGHTS_WRITE') + "&" \
                 + self.app.config.get('DB_RIGHTS_MAJORITY') + "&" \
                 + self.app.config.get('DB_RIGHTS_SSL') + "&" \
                 + self.app.config.get('DB_RIGHTS_SSL_CERT')
        uri = "mongodb+srv://" + user + ":" + password + "@" + host + "/" + db_name + "?" + rights
       # uri = "mongodb+srv://jromero:050899@geekify.q6113.mongodb.net/test?retryWrites=true&w=majority"
        self.db = pymongo.MongoClient(uri, connect=False).get_database()
        #self.db = pymongo.MongoClient(uri, connect=False,tls=True, tlsAllowInvalidCertificates=True).get_database()


db = DataBase.get_instance()
