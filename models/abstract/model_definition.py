from bson import ObjectId


class DocumentModel(object):
    collection = None
    __doc = None
    __id = None
    __created__ = False

    def __init__(self, doc=None):
        self.__doc = doc
        if doc is None:
            self.__doc = dict()

    @property
    def id(self):
        return self.__id

    @property
    def exists(self):
        return self.__id is not None and self.doc_ref is not None

    @property
    def created(self):
        return self.__created__

    def set_created(self, cond: bool = True):
        self.__created__ = cond

    @property
    def doc_ref(self):
        return self.__doc

    def set_doc_ref(self, doc):
        self.__doc = doc

    def set_id(self, id):
        self.__id = id
        self.doc_ref['id'] = self.__id.__str__()
        self.set_doc_ref(self.doc_ref.copy())

    def get_id(self):
        return self.__id.__str__()

    def get_column(self, col_name: str = None, col_type: type = None):
        if col_name:  # safe get column
            if col_name not in self.__doc.keys():
                # if user does not have a column with this name then lets creat one
                self.__doc[col_name] = col_type() if col_type else ''
                self.update_document()
            return self.__doc[col_name]

    # Create new document -- private method
    def __create(self):

        """
        if it's not created yet then create it otherwise ignore and return json just to have fun
        :return: void
        """
        if not self.exists:
            my_json = self.json()
            result = self.collection.insert_one(my_json['None'].copy())
            self.set_doc_ref(my_json['None'].copy())
            self.set_id(result.inserted_id)
            my_json['None']['id'] = self.get_id()
            my_json[u'{}'.format(self.get_id())] = my_json.pop('None')
            return my_json
        return self.json()

    def json(self):
        return {u'{}'.format(self.__id): self.__doc}

    def save_to_db(self):
        self.__created__ = True
        return self.__create()

    def delete_from_db(self):
        if self.exists:
            self.collection.find_one_and_delete({'_id': self.id})
            self.__doc = None
            self.__id = None
            self.__created__ = False

    def update_document(self, **kwargs):
        if self.exists:
            if kwargs:
                for key, value in kwargs.items():
                    self.__update_column__(key, value)
            self.collection.find_one_and_update(
                {'_id': self.id},
                {
                    '$set': self.__doc
                }
            )

    def __update_column__(self, column_name, value):
        self.__doc[column_name] = value

    @classmethod
    def get_all(cls):
        try:
            docs_generator = cls.collection.find()
            return cls.__create_from_docs_generator(docs_generator)
        except Exception:
            return dict()

    @classmethod
    def find_one_by_column(cls, value, col_name):
        try:
            doc = cls.collection.find_one({u'{0}'.format(col_name): u'{0}'.format(value)})
            if doc:
                model = cls.__create_from_doc_generator(doc, doc['_id'])
                return model
            return cls()
        except Exception:
            return cls()

    @classmethod
    def find_by_column(cls, value, col_name) -> dict:
        try:
            docs = cls.collection.find({u'{0}'.format(col_name): u'{0}'.format(value)})
            return cls.__create_from_docs_generator(docs)
        except Exception:
            return dict()

    @classmethod
    def __create_from_docs_generator(cls, docs_generator):
        models = dict()
        # usually it's one doc in the doc generator but just in case we receive a list of docs
        for doc in docs_generator:
            doc_id = doc['_id']
            models[doc_id.__str__()] = cls.__create_from_doc_generator(doc=doc, id=doc_id)
        return models

    @classmethod
    def __create_from_doc_generator(cls, doc, id: ObjectId):
        new_model = cls(doc=doc)
        new_model.set_id(id)
        new_model.set_created()
        return new_model

    @classmethod
    def find_by_id(cls, id):
        try:
            doc = cls.collection.find_one({'_id': ObjectId(id)})
            return cls.__create_from_doc_generator(doc, doc['_id'])
        except Exception:
            return cls(None)

    @classmethod
    def delete_by_id(cls, id):
        model = cls.find_by_id(id)
        if model.exists:
            model.delete_from_db()

    @classmethod
    def update_by_id(cls, id, **kwargs):
        model = cls.find_by_id(id)
        if model.exists:
            model.update_document(**kwargs)
