import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

import requests

from api.app import AccountModel


class GamesREST(unittest.TestCase):

    def test_request_get_games(self):
        url = "https://geekify-be.herokuapp.com/games"
        response = requests.get(url)
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json())  # add assertion here

    def test_request_get_games_by_title(self):
        url = "https://geekify-be.herokuapp.com/games/title/destiny"
        response = requests.get(url)
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json())  # add assertion here

    def test_request_get_games_detail(self):
        url = "https://geekify-be.herokuapp.com/game/32"
        response = requests.get(url)
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json())  # add assertion here

    def test_request_get_games_by_order(self):
        url = "https://geekify-be.herokuapp.com/games/filter/rating"
        response = requests.get(url)
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json())  # add assertion here

    def test_request_get_games_by_order(self):
        url = "https://geekify-be.herokuapp.com/games/filters?dates=1999&dates=2000&metacritic=80&metacritic=100" \
              "&parent_platforms=2&parent_platforms=7 "
        response = requests.get(url)
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json())  # add assertion here


if __name__ == '__main__':
    # run flask before running testing code
    # we don't have server mock yet!
    unittest.main()
