import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

import requests

from api.app import AccountModel
from api.app import CollectionModel


class CollectionsREST(unittest.TestCase):
    def test_request_get_collections(self):
        url = "http://127.0.0.1:5000/collections"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json())  # add assertion here

    def test_request_create_collection(self):
        collection = CollectionModel(title="test")
        collection.save_to_db()
        collection_id = collection.id
        url = "http://127.0.0.1:5000/collection/{0}".format(collection_id)
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json())  # add assertion here
        collection.delete_from_db()

    def test_request_add_game_collection(self):
        collection = CollectionModel(title="test")
        collection.save_to_db()
        collection_id = collection.id
        url = "http://127.0.0.1:5000/collectionGame/{0}".format(collection_id)
        response = requests.put(url, {"game_id": 3498})
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.json())  # add assertion here
        collection.delete_from_db()


if __name__ == '__main__':
    # run flask before running testing code
    # we don't have server mock yet!
    unittest.main()
