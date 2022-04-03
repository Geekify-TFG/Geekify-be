import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
from random import randint

import requests

from api.app import AccountModel


class AccountsRESTTest(unittest.TestCase):


    def test_request_get_accounts(self):
        account_doc = {
            AccountModel.email_col_name: u'example1@gmail.com',
            AccountModel.pass_col_name: u'test',
            AccountModel.name_col_name: u'test',
            AccountModel.photo_col_name: u'https://source.unsplash.com/random',
        }
        account = AccountModel.find_account(email=account_doc[AccountModel.email_col_name])
        if account and account.exists:
            account.delete_from_db()
        account = AccountModel(**account_doc.copy())
        account.hash_password()
        account.save_to_db()
        try:
            url = f'https://geekify-be.herokuapp.com/login?email=example1@gmail.com&password=test'
            response = requests.post(url)
            token = response.json()['token']
            url = "https://geekify-be.herokuapp.com/accounts"
            response = requests.get(url, auth=(token, ''))
            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(response.json())  # add assertion here
        except Exception as e:
            print(type(e), e, e.__traceback__)
        finally:
            account.delete_from_db()

    