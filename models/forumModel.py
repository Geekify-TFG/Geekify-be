import random
from flask_httpauth import HTTPBasicAuth

from models.abstract.model_definition import DocumentModel

auth = HTTPBasicAuth()

'''
    account model specially is converted and protected as it were a relational model 
    all attribute are defined here and is a must have value
    account (email, password(encrypted), name, ...)
'''

Photo = [
    "https://i.picsum.photos/id/473/200/200.jpg?hmac=lXsJQxtsh73ygSCMmcWA-YqIpQ4FjdxUYkkuLTAPBfM",
    "https://i.picsum.photos/id/305/200/200.jpg?hmac=GAm9fW477iVRZTOeQCdEqLVug4lTf8wnHHzLof8RbFQ",
    "https://i.picsum.photos/id/400/200/200.jpg?hmac=YLB07yPNCdu_zyt5Mr1eLqUtqY7nPOmnJBvJea4s7Uc",
    "https://i.picsum.photos/id/955/200/200.jpg?hmac=_m3ln1pswsR9s9hWuWrwY_O6N4wizKmukfhvyaTrkjE",
    "https://i.picsum.photos/id/1066/200/200.jpg?hmac=BHYYzH0KERL1WifyefL6hVVg0wURJUgTaByr75WmJug",
    "https://i.picsum.photos/id/504/200/200.jpg?hmac=uNktbiKQMUD0MuwgQUxt7R2zjHBGFxyUSG3prhX0FWM",
]

class ForumModel(DocumentModel):
    """
   class representing account model.
   mongodb - collection called accounts
   """

    __column_names__ = ['title', 'description', 'image', 'tag', 'game', 'users', 'num_users', 'posts', 'admin']

    # columns is a dict where the value for each column are referenced
    title_col_name = __column_names__[0]
    description_col_name = __column_names__[1]
    image_col_name = __column_names__[2]
    tag_col_name = __column_names__[3]
    game_col_name = __column_names__[4]
    users_col_name = __column_names__[5]
    num_users_col_name = __column_names__[6]
    posts_col_name = __column_names__[7]
    admin_col_name = __column_names__[8]

    def __init__(
            self,
            title=None,
            description=None,
            image='{0}'.format(random.choice(Photo)),
            tag=None,
            game=None,
            users=None,
            num_users=0,
            posts=None,
            admin=None,
            doc=None
    ):
        super(ForumModel, self).__init__(doc)
        if users is None:
            users = []
        columns = dict.fromkeys(self.__column_names__)
        if doc:
            dic = dict.fromkeys(self.__column_names__)
            dic.update(self.doc_ref)
            self.set_doc_ref(dic.copy())  # make sure doc_ref have all columns
            try:
                # -- check all args are there in case missing args throw exception -- this can omitted --
                for col in self.__column_names__:
                    columns[col] = self.doc_ref[u'{0}'.format(col)]
            except Exception as e:
                raise Exception('missing arguments! \n Error  {0}:{1}'.format(type(e), e))
        else:
            columns['{0}'.format(self.title_col_name)] = str(title)
            columns['{0}'.format(self.description_col_name)] = str(description)
            columns['{0}'.format(self.image_col_name)] = '{0}'.format(random.choice(Photo))
            columns['{0}'.format(self.tag_col_name)] = tag
            columns['{0}'.format(self.game_col_name)] = game
            columns['{0}'.format(self.users_col_name)] = users
            columns['{0}'.format(self.num_users_col_name)] = num_users
            columns['{0}'.format(self.posts_col_name)] = posts
            columns['{0}'.format(self.admin_col_name)] = admin
            self.set_doc_ref(columns.copy())

    # Create new document -- private method
    def __create(self):
        """
        if it's not created yet then create it otherwise ignore and return json just to have fun
        :return: void
        """
        if not self.exists:
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
            self, title=None, description=None, image=None, tag=None, game=None, users=None, num_users=None, admin=None,
            posts=None,
    ):
        # if it's already exists then update
        if self.exists:
            if title:
                self.__update_column__(self.title_col_name, str(title))
            if description:
                self.__update_column__(self.title_col_name, str(title))
            if image:
                self.__update_column__(self.image_col_name, str(image))
            if tag:
                self.__update_column__(self.tag_col_name, tag)
            if game:
                self.__update_column__(self.game_col_name, game)
            if users:
                self.__update_column__(self.users_col_name, users)
            if posts:
                self.__update_column__(self.posts_col_name, posts)
            if num_users:
                self.__update_column__(self.num_users_col_name, num_users)
            if admin:
                self.__update_column__(self.admin_col_name, admin)
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
            title=None, description=None, image=None, tag=None, game=None, users=None, num_users=None, admin=None,posts=None
    ):
        collection = cls.find_by_id(id)
        if collection.exists:
            collection.update_document(
                title=title,
                description=description,
                image=image,
                tag=tag,
                game=game,
                users=users,
                num_users=num_users,
                admin=admin,
                posts=posts
            )

    @classmethod
    def find_by_title(cls, title) -> dict:
        return cls.find_collection(title=title)

    def delete_from_db(self):
        super(ForumModel, self).delete_from_db()

    @classmethod
    def find_forum(cls, title=None, id=None) -> dict:

        if title:
            forum = cls.find_one_by_column(title, cls.title_col_name)
        elif id:
            forum = cls.find_by_id(id)
        else:
            raise ValueError(
                "You need to give one the following: "
                "an existing title or existing user id"
            )
        return forum
