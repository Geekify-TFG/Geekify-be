import datetime
import random

import requests

from app import AccountModel
from app import CommentModel

Users = [
    "johnblake@geekify.com",
    "marthastuart@geekify.com",
    "marthastuart@geekify.com",
    "davidmann@geekify.com",
    "davidmann@geekify.com",
    "emmadavis@geekify.com",
    "juliastone@geekify.com",
    "demianmars@geekify.com",
    "karlmarx@geekify.com",
    "lakelynhogan@geekify.com",
    "trotsky@geekify.com",
    "justinewatson@geekify.com",
    "justinewatson@geekify.com",
    "markuslinn@geekify.com",
    "michaelleon@geekify.com",
    "lilyaugust@geekify.com",
    "leahgreen@geekify.com",
    "dansamuel@geekify.com",
    "lauramartens@geekify.com",
]

Comments = [
    "Commentary number 1",
    "Commentary number 2",
    "Commentary number 3",
    "Commentary number 4",
    "Commentary number 5",
    "Commentary number 6",
    "Commentary number 7",
    "Commentary number 8",
    "Commentary number 9",
    "Commentary number 10",
    "Commentary number 11",
    "Commentary number 12",
    "Commentary number 12",
    "Commentary number 13",
    "Commentary number 14",
    "Commentary number 15",
]

Dates = [
    "1/04/2022",
    "2/04/2022",
    "3/04/2022",
    "4/04/2022",
    "5/04/2022",
    "6/04/2022",
    "7/04/2022",
    "8/04/2022",
    "9/04/2022",
    "10/04/2022",
    "11/04/2022",
    "12/04/2022",
]

Photo = [
    "https://i.picsum.photos/id/473/200/200.jpg?hmac=lXsJQxtsh73ygSCMmcWA-YqIpQ4FjdxUYkkuLTAPBfM",
    "https://i.picsum.photos/id/305/200/200.jpg?hmac=GAm9fW477iVRZTOeQCdEqLVug4lTf8wnHHzLof8RbFQ",
    "https://i.picsum.photos/id/400/200/200.jpg?hmac=YLB07yPNCdu_zyt5Mr1eLqUtqY7nPOmnJBvJea4s7Uc",
    "https://i.picsum.photos/id/955/200/200.jpg?hmac=_m3ln1pswsR9s9hWuWrwY_O6N4wizKmukfhvyaTrkjE",
    "https://i.picsum.photos/id/1066/200/200.jpg?hmac=BHYYzH0KERL1WifyefL6hVVg0wURJUgTaByr75WmJug",
    "https://i.picsum.photos/id/504/200/200.jpg?hmac=uNktbiKQMUD0MuwgQUxt7R2zjHBGFxyUSG3prhX0FWM",
]

account_doc = {
    'email': u'example1@gmail.com',
    'password': u'test',
    'is_admin': u'0',
    'name': u'test',
    'photo': u'https://source.unsplash.com/random',
}


def create_user(email, name, photo):
    test = AccountModel.find_account(email=email)
    if test and test.exists:
        return None
    else:
        account_doc['email'] = email
        account_doc['name'] = name
        account_doc['photo'] = photo
        account = AccountModel(**account_doc)
        account.hash_password()
        account.save_to_db()
        return account


def create_users():
    for user in Users:
        photo = (random.choice(Photo))
        name = user.split('@')[0]
        create_user(user, name, photo)


def users_comment_games():
    accounts = AccountModel.get_all()
    API_KEY = '40f3cb2ff2c94a5889d3d6c865415ec5'
    games_id = []
    for i in range(1, 6):
        api_rawg = "https://api.rawg.io/api/games?page={0}&key=".format(i) + API_KEY
        games = requests.get(api_rawg)
        my_json = games.json().get("results")
        for index in range(len(my_json)):
            games_id.append(my_json[index]['id'])

    for game in games_id:
        num_comments = random.randrange(1, 4)
        for numComments in range(0, num_comments):
            user = (random.choice(Users))
            username = user.split('@')[0]
            date = (random.choice(Dates))
            image_user = (random.choice(Photo))
            content = (random.choice(Comments))
            new_comment = CommentModel(date, content, username, game, image_user)
            new_comment.save_to_db()


add_comments = users_comment_games()

if __name__ == "__main__":
    add_comments
    # create_users()
