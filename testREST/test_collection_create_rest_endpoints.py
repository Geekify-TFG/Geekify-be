import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

import requests

from app import CollectionModel


class CollectionsREST(unittest.TestCase):
    def test_request_get_collections(self):
        url = f'https://geekify-be.herokuapp.com/login?email=test@a.com&password=test'
        response = requests.post(url)
        token = response.json()['account']['token']
        url = "https://geekify-be.herokuapp.com/collections/user_email/test@a.com"
        response = requests.get(url, auth=(token, ''))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json())  # add assertion here

    def test_request_create_collection(self):
        url = f'https://geekify-be.herokuapp.com/login?email=test@a.com&password=test'
        response = requests.post(url)
        token = response.json()['account']['token']

        collection = CollectionModel(title="testing")
        collection.save_to_db()
        collection_id = collection.id
        url = "https://geekify-be.herokuapp.com/collection/{0}".format(collection_id)
        response = requests.get(url, auth=(token, ''))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json())  # add assertion here
        collection.delete_from_db()

    """  def test_request_add_game_collection(self):
            url = f'https://geekify-be.herokuapp.com/login?email=test@a.com&password=test'
            response = requests.post(url)
            token = response.json()['account']['token']
            collection = CollectionModel(title="testing")
            collection.save_to_db()
            collection_id = collection.id
            url = "https://geekify-be.herokuapp.com/collectionGame/{0}".format(collection_id)
            response = requests.put(url, {"game_id": 3498})
            self.assertEqual(response.status_code, 201)
            self.assertIsNotNone(response.json())  # add assertion here
            collection.delete_from_db()
    """

if __name__ == '__main__':
    # run flask before running testing code
    # we don't have server mock yet!
    unittest.main()
