from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import json
import redis

# App
application = Flask(__name__)

# connect to MongoDB
mongoClient = MongoClient('mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] +
                          '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_AUTHDB'])
db = mongoClient[os.environ['MONGODB_DATABASE']]

# connect to Redis
redisClient = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get(
    "REDIS_PORT", 6379), db=os.environ.get("REDIS_DB", 0))

# connect to game collection in mongo db
collection_game = db.game

@application.route('/')
def index():
    body = '<h1>MongoDB Exercise - Array</h1>'
    body += '<h2>Alphabet Guessing Game v1.0</h2>'
    body += '<button> <a href="/Play/">play a game</a></button>'
    return body

@application.route('/Play/')
def start():
    body = '<h2>Alphabet Guessing Game v1.0</h2>'
    game = collection_game.find_one()
    if game == None:
        mydict = {
            "question": ["_","_","_","_"],
            "char_remain": ["*","*","*","*"],
            "answer": [],
            "wrong_number": 0,
            "index": 0,
            "Mode": False
            }
        collection_game.insert_one(mydict)
        body += "reload the question again."

    if game != None:
        body = '<h1>Select 4 characters to make a question!</h1>'
        body += '<br></br>'
        question_text = ' '.join(game['question'])
        body += 'Question :' + question_text
        body += '<br></br>'
        body += '<a href="/A/"><button>A</button></a>'
        body += '<a href="/B/"><button>B</button></a>'
        body += '<a href="/C/"><button>C</button></a>'
        body += '<a href="/D/"><button>D</button></a>'
        if game['index'] == 4:
            collection_game.update_one({}, {"$set": {"Mode"  : True}})
            collection_game.update_one({}, {"$set": {"index" : 0}})
            body = '<h1>Select 4 characters to make a question!</h1>'
            body += 'Question created! Prepare for playing'
            body += '<br></br>'
            body += '<a href="/playtime/"><button> Press to go</button></a>'
            return body
    return body


@application.route('/A/')
def routeA():
    game = collection_game.find_one()
    if game["Mode"] == False :
        ans_or_quest(game["Mode"],game,'A')
        return start()
    if game["Mode"] == True :
        ans_or_quest(game["Mode"],game,'A')
        return play()

@application.route('/B/')
def routeB():
    game = collection_game.find_one()
    ans_or_quest(game["Mode"], game, 'B')
    return 0
@application.route('/C/')
def routeC():
    game = collection_game.find_one()
    ans_or_quest(game["Mode"], game, 'C')
    return 0

@application.route('/D/')
def routeD():
    game = collection_game.find_one()
    ans_or_quest(game["Mode"], game, 'D')
    return 0

def ans_or_quest(type, game, alphabet):
    if type == False:
        index_now = game["index"]
        collection_game.update_one({}, {"$set": {"question." + str(index_now) : alphabet}})
        index_now += 1
        collection_game.update_one({}, {"$set": {"index" : index_now}})
    if type == True:
        index_now = game["index"]
        current_fail = game["wrong_number"]
        if game['question'][index_now] == alphabet:
            collection_game.update_one({}, {"$set": {"answer." + str(index_now) : alphabet}})
            index_now += 1
            collection_game.update_one({}, {"$set": {"index" : index_now}})
            collection_game.update_one({}, { "$set": { 'char_remain.' + str(index_now): "" }})
        else:
            current_fail += 1
            collection_game.update_one({}, {"$set": {"wrong_number": current_fail}})



@application.route('/playtime/')
def play():
    collection_game = db.game
    game = collection_game.find_one()
    if game['question'] == game['answer']:
        return gameover()
    ans_text = ' '.join(game['answer'])
    char_remain_text = ' '.join(game['char_remain'])
    body = '<h2>Alphabet Guessing Game V.1.0</h2>'
    body += "Please Choose A or B or C or D to guess."
    body += '<br> <br> '
    body += 'Answer: ' + ans_text
    body += '<br>'
    body += 'Character(s) remaining: ' + char_remain_text
    body += '<br> <br>'
    body += 'Choose:  <a href="/A"><button> A </button></a>'
    body += '<a href="/B"><button> B </button></a>'
    body += '<a href="/C"><button> C </button></a>'
    body += '<a href="/D"><button> D </button></a>'
    body += '<br> <br>'
    body += 'Your miss answer: ' + str(game["wrong_number"])
    return body




@application.route('/gameover')
def gameover():
    collection_game = db.game
    game = collection_game.find_one()
    body = '<h2>Congratulations!!! </h2>'
    body += '<b>You win!</b>'
    body += '<br> <br> '
    body += '<b>Number of wrong answer: </b>' + str(game['wrong_number'])
    body += '<br> <br>'
    body += '<a href="/again"><button> Play again! </button></a>'
    return body

@application.route('/again')
def again():
    collection_game = db.game
    mydict = {
        "question": ["_","_","_","_"],
        "char_remain": ["*","*","*","*"],
        "answer": [],
        "wrong_number": 0,
        "index": 0,
        "Mode": False
    }
    collection_game.update_one({}, {"$set": mydict})
    return index()

@application.route('/sample')
def sample():
    doc = db.test.find_one()
    # return jsonify(doc)
    body = '<div style="text-align:center;">'
    body += '<h1>Python</h1>'
    body += '<p>'
    body += '<a target="_blank" href="https://flask.palletsprojects.com/en/1.1.x/quickstart/">Flask v1.1.x Quickstart</a>'
    body += ' | '
    body += '<a target="_blank" href="https://pymongo.readthedocs.io/en/stable/tutorial.html">PyMongo v3.11.2 Tutorial</a>'
    body += ' | '
    body += '<a target="_blank" href="https://github.com/andymccurdy/redis-py">redis-py v3.5.3 Git</a>'
    body += '</p>'
    body += '</div>'
    body += '<h1>MongoDB</h1>'
    body += '<pre>'
    body += json.dumps(doc, indent=4)
    body += '</pre>'
    res = redisClient.set('Hello', 'World')
    if res == True:
      # Display MongoDB & Redis message.
      body += '<h1>Redis</h1>'
      body += 'Get Hello => '+redisClient.get('Hello').decode("utf-8")
    return body

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("FLASK_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("FLASK_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)