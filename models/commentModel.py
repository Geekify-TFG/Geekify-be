from models.abstract.model_definition import DocumentModel


class CommentModel(DocumentModel):
    # definition of the document columns
    __column_names__ = ['date', 'content', 'user', 'game_id', 'image_user','likes','num_likes']  # likes

    def __init__(self, date=None, content=None, user=None, game_id=None,image_user=None,likes=[],num_likes=0, doc=None):
        super(CommentModel, self).__init__(doc)
        if doc:
            dic = dict.fromkeys(self.__column_names__)
            dic.update(self.doc_ref)
            self.set_doc_ref(dic.copy())  # make sure doc_ref have all columns
            try:
                self.date = self.doc_ref['date']
                self.content = self.doc_ref['content']
                self.user = self.doc_ref['user']
                self.game_id = self.doc_ref['game_id']
                self.image_user = self.doc_ref['image_user']
                self.likes = self.doc_ref['likes']
                self.num_likes = self.doc_ref['num_likes']
            except Exception as e:
                raise Exception('document does not exists! \n Error  {}:{}'.format(type(e), e))
        else:
            self.date = date
            self.content = content
            self.user = user
            self.game_id = game_id
            self.image_user = image_user
            self.likes = []
            self.num_likes=num_likes
            self.set_doc_ref(self.json()['None'])

    def json(self):
        return {
            u'{}'.format(self.get_id()): {
                u'date': u'{}'.format(self.date),
                u'user': u'{}'.format(self.user),
                u'content': u'{}'.format(self.content),
                u'game_id': u'{}'.format(self.game_id),
                u'image_user': u'{}'.format(self.image_user),
                u'likes': self.likes,
                u'num_likes': self.num_likes
            }
        }

    def update_document(
        self,date=None, content=None, user=None, game_id=None,image_user=None,likes=[],num_likes=0 ):
        # if it's already exists then update
        if self.exists:
            if date:
                self.__update_column__('date', str(date))
            if user:
                self.__update_column__('user', str(user))
            if content:
                self.__update_column__('content', content)
            if game_id:
                self.__update_column__('game_id', game_id)
            if image_user:
                self.__update_column__('image_user', image_user)
            if likes:
                self.__update_column__('likes', likes)
            if num_likes:
                (num_likes)
                self.__update_column__('num_likes', num_likes)

            self.collection.find_one_and_update(
                {'_id': self.id},
                {
                    '$set': self.doc_ref
                }
            )

    def get_likes(self):
        return self.get_column(col_name='likes', col_type=list)

    def get_num_likes(self):
        return self.get_column(col_name='num_likes', col_type=list)
    
    def add_or_remove_like_comment(self, user):
        if user:
            likes = self.get_likes()
            num_likes = self.get_num_likes()
            if user in likes:
                likes.remove(u'{0}'.format(user))
                num_likes -= 1
            else:
                likes.append(u'{}'.format(user))
                num_likes += 1
            self.update_document(likes=likes,num_likes=num_likes)
    @classmethod
    def find_by_game(cls, game_id):
        return cls.find_by_column(game_id, 'game_id')

    @classmethod
    def find_by_user(cls, user):
        return cls.find_one_by_column(user, 'user')

    @classmethod
    def delete_by_game_id(cls, game_id):
        comments = cls.find_by_column(game_id, 'game_id')
        for comment_id, comment in comments.items():
            comment.delete_from_db()
        return comments

    @classmethod
    def find_comment(cls, id=None) -> dict:
        if id:
            comment = cls.find_by_id(id)
        else:
            raise ValueError(
                "You need to give one the following: "
                "an existing title or existing user id"
            )
        return comment
