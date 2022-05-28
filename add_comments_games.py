import datetime
import random

import requests

from app import AccountModel
from app import CommentModel
from models.forumModel import ForumModel
from models.publicationModel import PublicationModel

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
    "One of my favorite games. Good for an adventure visiting grand sights and living out memorable experiences or simply relaxing and exploring the beautiful world.",
    "After several years on both this and original Im still absolutely in love with this amazing game.",
    "Most fun I had in any video game ever. 10/10 would play again.",
    "Such a fun and hilarious game. Played through almost the full game in 1 sitting and laughed almost the entire time.",
    "BEST GAME I HAVE EVER PLAYED!!!!!!This game is so good!!!! I just love turning my PC on and playing it!!! The grapics are awesome gameplay is THE BEST!! And the best part is.. IT REALLY PLAYS WELL!!",
    "This game sucked up hundreds of hours of my life and i dont regret a thing.",
    "Pretty awsome game with many opportunity to try and tottally worth it's price!",
    "Horrible game not worth it.",
    "No other game can give me what i feel about this game absolutely love it.",
    "Why should you buy this game?....oh yeah because its great",
    "The most addicting game ever.. Gets an easy 9/10 from me.To get a ten it would be some bug fixing but thats not too hard.",
    "Oh god. So fun. So fast and you can get into it in short intervals diving in and out of gameplay to fit in your busy schedule.",
    "This is the best game eva made. 10/10 mastapiece.",
    "this game is awesome every single part of it is amazing!!!",
    "This game is amazing!!! The graphics are good concept is amazingly good and it is eazy to play all day. It was a really good game and I liked it a lot.",
    "Very addicting. A must buy.",
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
    "https://i.postimg.cc/dZ2xnvvr/descarga.jpg",
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

Gender=[
    "Male",
    "Female",
    "Other"
]
Birthday = [
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

FavCategories=[
    "action",
    "adventure",
    "shooter",
    "puzzle",
    "RPG",
    "indie",
    "strategy",
    "sports",
    "family",
    "fighting"
]

Location=[
    "Madrid",
    "Barcelona",
    "Sevilla",
    "Málaga",
    "Valencia",
    "Zaragoza",
    "Palma",
    "Murcia",
    "Las Palmas",
    "A Coruña",
    "Bilbao",
    "Alicante",
    "Córdoba",
    "Valladolid",
    "Vigo",
    "Gijón",
    "Vitoria-Gasteiz",
    "Elche",
    "Granada",
]

TopGames=['3498', '3328', '4200', '5286', '5679', '4291', '12020', '13536', '4062', '3439', '802', '28', '13537', '4286', '1030', '2454', '3070', '32', '11859', '3939', '58175', '4459', '278', '3272', '10213', '29028', '3192', '766', '422', '7689', '23027', '3287', '16944', '41494', '19103', '11973', '416', '17822', '10035', '4427', '19710', '4252', '19709', '3612', '1447', '4332', '2551', '3790', '2462', '13668', '10754', '19487', '4386', '9767', '58134', '4161', '41', '11936', '290856', '4828', '3696', '4514', '3144', '18080', '3636', '13633', '17540', '4570', '4806', '29177', '39', '10533', '362', '5583', '9721', '10243', '3841', '12536', '430', '4248', '5563', '3387', '4166', '654', '11935', '3747', '12447', '3543', '613', '3017', '108', '10142', '3254', '50738', '58812', '11934', '864', '9882', '4513', '3191']



def create_user(email, name, photo,gender,birthday,location,fav_categories,top_games,followed_users):
    test = AccountModel.find_account(email=email)
    if test and test.exists:
        return None
    else:
        account_doc['email'] = email
        account_doc['name'] = name
        account_doc['photo'] = photo
        account_doc['gender'] = gender
        account_doc['birthday']=birthday
        account_doc['location']=location
        account_doc['fav_categories']=fav_categories
        account_doc['top_games']=top_games
        account_doc['followed_users']=followed_users
        account = AccountModel(**account_doc)
        account.hash_password()
        account.save_to_db()
        return account


def create_users():
    for user in Users:
        photo = (random.choice(Photo))
        name = user.split('@')[0]
        gender = (random.choice(Gender))
        birthday = (random.choice(Birthday))
        location= (random.choice(Location))
        #Insert 2 values from FavCategories to fav_categories
        fav_categories = random.sample(set(FavCategories),2)
        top_games = random.sample(set(TopGames),3)
        followed_users=random.sample(set(Users),2)
        create_user(user, name, photo,gender,birthday,location,fav_categories,top_games,followed_users)

def users_comment_games():
    accounts = AccountModel.get_all()
    API_KEY = '37ba2daee1ea4636b4b96fb2cf0193b3'
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
            new_comment = CommentModel(date, content, user, game, image_user)
            new_comment.save_to_db()


def users_publications_forums():
    ret = ForumModel.get_all()
    #print(list(ret.keys()))
    for forum in list(ret.keys()):
        num_publications = random.randrange(1, 4)
        for numPublications in range(0, num_publications):
            user = (random.choice(Users))
            date = (random.choice(Dates))
            image_user = (random.choice(Photo))
            content = (random.choice(Comments))
            new_publication = PublicationModel(date, content, user, forum,image_user)
            #print(new_publication.json())
            new_publication.save_to_db()

def users_follow_forum():
    ret = ForumModel.get_all()
    for forum_id in list(ret.keys()):
        #Get random Users
        num_followers = random.randrange(1, 6)
        users = random.sample(set(Users),num_followers)
        forum = ForumModel.find_by_id(forum_id)
        forum.update_by_id(forum_id, users=users)
        #print(forum)

add_comments = users_comment_games()
create_users = create_users()
add_publications_forum = users_publications_forums()
add_follow_forum = users_follow_forum()
if __name__ == "__main__":
    #add_comments
    # create_users
    #add_publications_forum
    add_follow_forum
