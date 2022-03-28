from decouple import config


class Config:
    pass


class ProductionConfig(Config):
    DEBUG = False
    STATIC_FOLDER = "/static"
    TEMPLATE_FOLDER = "/templates"
    SECRET_KEY = config('SECRET_KEY', default='localhost')
    DB_USER = config('DB_USER', default='localhost')
    DB_PASSWORD = config('DB_PASSWORD', default='localhost')
    DB_HOST = config('DB_HOST', default='localhost')
    DB_NAME = config('DB_NAME', default='localhost')
    DB_RIGHTS_WRITE = config('DB_RIGHTS_WRITE', default='localhost')
    DB_RIGHTS_MAJORITY = config('DB_RIGHTS_MAJORITY', default='localhost')
    DB_RIGHTS_SSL = config('DB_RIGHTS_SSL', default='localhost')
    DB_RIGHTS_SSL_CERT = config('DB_RIGHTS_SSL_CERT', default='localhost')


class DevelopmentConfig(Config):
    DEBUG = True
    STATIC_FOLDER = "/static"
    TEMPLATE_FOLDER = "/templates"
    SECRET_KEY = "kdsfklsmfakfmafmadslvsdfasdf"
    DB_USER = "jromero"
    DB_PASSWORD = "050899"
    DB_HOST = "geekify.q6113.mongodb.net"
    DB_NAME = "test"
    DB_RIGHTS_WRITE = "retryWrites=true"
    DB_RIGHTS_MAJORITY = "w=majority"
    DB_RIGHTS_SSL = "ssl=true"
    DB_RIGHTS_SSL_CERT = "ssl_cert_reqs=CERT_NONE"


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
