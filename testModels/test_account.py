import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

from bson import ObjectId

from api.app import AccountModel


class AccountModelTest(unittest.TestCase):

    def test_create_user(self):
        """
        when a user is created is never exists until save_to_db is called
        :return: None
        """
        account_doc = {
            AccountModel.email_col_name: u'example1@gmail.com',
            AccountModel.pass_col_name: u'test',
            AccountModel.name_col_name: u'test',
            AccountModel.photo_col_name: u'https://source.unsplash.com/random',
        }
        account = AccountModel(**account_doc)
        self.assertEqual(account.exists, False)

    def test_save_to_db(self):
        """
        :return: None
        """
        account_doc = {
            AccountModel.email_col_name: u'example1@gmail.com',
            AccountModel.pass_col_name: u'test',
            AccountModel.name_col_name: u'test',
            AccountModel.photo_col_name: u'https://source.unsplash.com/random',
        }
        account = AccountModel(**account_doc)
        account.hash_password()
        my_json = account.save_to_db()
        self.assertEqual(account.exists, True)
        self.assertIsNotNone(account.id)
        self.assertEqual(type(account.id), ObjectId)
        self.assertEqual(type(my_json['value']), dict)
        account.delete_from_db()

    def test_delete_from_db(self):
        # save to db it it saved then ignore
        account_doc = {
            AccountModel.email_col_name: u'example1@gmail.com',
            AccountModel.pass_col_name: u'test',
            AccountModel.name_col_name: u'test',
            AccountModel.photo_col_name: u'https://source.unsplash.com/random',
        }
        account = AccountModel(**account_doc)
        account.hash_password()
        account.save_to_db()
        account.delete_from_db()
        self.assertEqual(account.exists, False)
        self.assertEqual(account.doc_ref, None)

    def test_find_all_user(self):
        result = AccountModel.get_all()
        self.assertEqual(type(result), dict)

    def test_find_one_by_column(self):
        result = AccountModel.find_one_by_column(value='test', col_name='email')
        self.assertEqual(type(result), AccountModel)

    def test_find_user_find_by_column(self):
        result = AccountModel.find_by_column(value='test', col_name='email')
        self.assertEqual(type(result), dict)


if __name__ == '__main__':
    unittest.main()
