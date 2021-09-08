# Requires the PyMongo package.
# https://api.mongodb.com/python/current
from pymongo import MongoClient
from pprint import pprint

client = MongoClient('mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection='
                     'true&ssl=false')

# Task 04
filter_1 = {'from_username': 'machine_learning_with_python'}

# Task 05
filter_2 = {'$and': [{'from_username': 'python.learning'},
                        {'user_status': 'following'}]}

result_1 = client['instagram']['instagramfollowers'].find(filter=filter_1)
result_2 = client['instagram']['instagramfollowers'].find(filter=filter_2)

for item in result_1:
    pprint(item)

for item in result_2:
    pprint(item)
