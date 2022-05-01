from models.abstract.model_definition import DocumentModel


class PublicationModel(DocumentModel):
    # definition of the document columns
    __column_names__ = ['date', 'content', 'user', 'forum_id', 'image_user', 'likes', 'num_likes']

    def __init__(self, date=None, content=None, user=None, forum_id=None, image_user=None, likes=[], num_likes=0,
                 doc=None):
        super(PublicationModel, self).__init__(doc)
        if doc:
            dic = dict.fromkeys(self.__column_names__)
            dic.update(self.doc_ref)
            self.set_doc_ref(dic.copy())  # make sure doc_ref have all columns
            try:
                self.date = self.doc_ref['date']
                self.content = self.doc_ref['content']
                self.user = self.doc_ref['user']
                self.forum_id = self.doc_ref['forum_id']
                self.image_user = self.doc_ref['image_user']
                self.likes = self.doc_ref['likes']
                self.num_likes = self.doc_ref['num_likes']
            except Exception as e:
                raise Exception('document does not exists! \n Error  {}:{}'.format(type(e), e))
        else:
            self.date = date
            self.content = content
            self.user = user
            self.forum_id = forum_id
            self.image_user = image_user
            self.likes = likes
            self.num_likes = num_likes
            self.set_doc_ref(self.json()['None'])

    def json(self):
        return {
            u'{}'.format(self.get_id()): {
                u'date': u'{}'.format(self.date),
                u'user': u'{}'.format(self.user),
                u'content': u'{}'.format(self.content),
                u'forum_id': u'{}'.format(self.forum_id),
                u'image_user': u'{}'.format(self.image_user),
                u'likes': self.likes,
                u'num_likes': self.num_likes
            }
        }

    def update_document(
            self, date=None, user=None, content=None, forum_id=None, image_user=None, likes=None, num_likes=None
    ):
        # if it's already exists then update
        if self.exists:
            if date:
                self.__update_column__('date', str(date))
            if user:
                self.__update_column__('user', str(user))
            if content:
                self.__update_column__('content', content)
            if forum_id:
                self.__update_column__('forum_id', forum_id)
            if image_user:
                self.__update_column__('image_user', image_user)
            if likes:
                self.__update_column__('likes', likes)
                self.__update_column__('num_likes', len(likes))
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

    def add_or_remove_like_publication(self, user):
        if user:
            likes = self.get_likes()
            num_likes = self.get_num_likes()
            if user in likes:
                likes.remove(u'{0}'.format(user))
            else:
                likes.append(u'{}'.format(user))
            #num_likes = len(likes)
            self.update_document(likes=likes,num_likes=num_likes)

    @classmethod
    def find_by_forum(cls, forum_id):
        return cls.find_by_column(forum_id, 'forum_id')

    @classmethod
    def find_by_user(cls, user):
        return cls.find_one_by_column(user, 'user')

    @classmethod
    def delete_by_forum_id(cls, forum_id):
        publication = cls.find_by_column(forum_id, 'forum_id')
        for comment_id, comment in publication.items():
            comment.delete_from_db()
        return publication

    @classmethod
    def find_publication(cls, id=None) -> dict:
        if id:
            publication = cls.find_by_id(id)
        else:
            raise ValueError(
                "You need to give one the following: "
                "an existing title or existing user id"
            )
        return publication
