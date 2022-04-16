from models.abstract.model_definition import DocumentModel


class PublicationModel(DocumentModel):
    # definition of the document columns
    __column_names__ = ['date', 'content', 'user', 'forum_id', 'image_user', 'likes']

    def __init__(self, date=None, content=None, user=None, forum_id=None, image_user=None,likes=None, doc=None):
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
            except Exception as e:
                raise Exception('document does not exists! \n Error  {}:{}'.format(type(e), e))
        else:
            self.date = date
            self.content = content
            self.user = user
            self.forum_id = forum_id
            self.image_user = image_user
            self.likes = []
            self.set_doc_ref(self.json()['None'])

    def json(self):
        return {
            u'{}'.format(self.get_id()): {
                u'date': u'{}'.format(self.date),
                u'user': u'{}'.format(self.user),
                u'content': u'{}'.format(self.content),
                u'forum_id': u'{}'.format(self.forum_id),
                u'image_user': u'{}'.format(self.image_user),
                u'likes': self.likes
            }
        }

    @classmethod
    def find_by_forum(cls, forum_id):
        return cls.find_by_column(forum_id, 'forum_id')

    @classmethod
    def find_by_user(cls, user):
        return cls.find_one_by_column(user, 'user')

    @classmethod
    def delete_by_forum_id(cls, forum_id):
        # pero una cosa debe borrar todos los comments
        publication = cls.find_by_column(forum_id, 'forum_id')
        for comment_id, comment in publication.items():
            comment.delete_from_db()
        return publication
