import pymongo
from decouple import config as config_decouple
from flask import Flask
from flask_restful import Api

from models.forumModel import ForumModel
from models.publicationModel import PublicationModel
from resources.collections import Collections, CollectionsList, CollectionGame
from config import config
from flask_cors import CORS

from db import db
# models imports
from models.accountModel import AccountModel
from models.collectionModel import CollectionModel
from models.commentModel import CommentModel

# resources imports
from resources.account import AccountStateGame, Accounts, AccountLike, AccountForums, AccountInfo, AccountCalendar, FollowUser
from resources.comments import CommentLike, CommentsList, Comments
from resources.forums import Forum, ForumsList
from resources.login import LogIn
from resources.games import Games, GamesAccordingFav, GamesByTitle, GamesByOrder, GameDetail, GameFilters, GameCommentsList, \
    ListMostPopularGames
from resources.news import News
from resources.publications import ForumPublications, Publications, ForumPublicationLike
from resources.calendar import Calendar
app = Flask(__name__)
environment = config['development']
if config_decouple('PRODUCTION', cast=bool, default=False):
    environment = config['production']

app.config.from_object(environment)

api = Api(app)
CORS(app, resources={r'/*': {'origins': '*'}})

db.get_instance().init_app(app)
AccountModel.collection = db.get_database.accounts
CollectionModel.collection = db.get_database.collections
CommentModel.collection = db.get_database.comments
ForumModel.collection = db.get_database.forums
PublicationModel.collection = db.get_database.publications

CONNECTION_STRING = "mongodb+srv://jromero:050899@geekify.q6113.mongodb.net/test?retryWrites=true&w=majority"
mongo = pymongo.MongoClient(CONNECTION_STRING, tls=True, tlsAllowInvalidCertificates=True)

# Account

api.add_resource(Accounts, '/account/email/<string:email>', '/account/id/<string:id>', '/account/user')
api.add_resource(LogIn, '/login')
api.add_resource(AccountLike, '/account/like/<string:id>')
api.add_resource(AccountStateGame, '/account/state/<string:id>')
api.add_resource(AccountForums, '/account/forums/<string:email>')
api.add_resource(AccountInfo, '/account/info/<string:email>')
api.add_resource(AccountCalendar, '/account/calendar/<string:email>')
api.add_resource(FollowUser, '/account/followUser/<string:email>')

# Games
api.add_resource(Games, '/games')
api.add_resource(GameDetail, '/game/<string:id>')
api.add_resource(GamesByTitle, '/games/title/<string:title>')
api.add_resource(GamesByOrder, '/games/filter/<string:order>')
api.add_resource(GameFilters, '/games/filters')
api.add_resource(GameCommentsList, '/gameComments/<string:id>')
api.add_resource(ListMostPopularGames, '/listGames/<string:id>', '/listGames')
api.add_resource(GamesAccordingFav, '/gamesFavCategories/<string:email>')

# Comments
api.add_resource(CommentsList, '/comments')
api.add_resource(Comments, '/comment/<string:id>')
api.add_resource(CommentLike, '/commentLike/<string:id>')

# Collections
api.add_resource(Collections, '/collection', '/collection/<string:id>', '/collections/<string:email>/')
api.add_resource(CollectionsList, '/collections/user_email/<string:user_email>')
api.add_resource(CollectionGame, '/collectionGame/<string:id>')

# News
api.add_resource(News, '/news')

# Forums
api.add_resource(Forum, '/forum', '/forum/<string:id>')
api.add_resource(ForumsList, '/forums')

# Publications
api.add_resource(ForumPublications, '/forum/<string:id>/publications')
api.add_resource(Publications, '/forum/<string:id>/publication', '/publication/<string:id>')
api.add_resource(ForumPublicationLike, '/publicationLike/<string:id>',)

# Calendar
api.add_resource(Calendar, '/calendar')

if __name__ == "__main__":
    app.run(port=5000, debug=True)
