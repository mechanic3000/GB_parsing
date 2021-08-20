from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['vacancies']
vacancies_db = db.items


#  ( задание № 2 )
def find_work(salary):
    return_list = []
    for item in vacancies_db.find({'$or': [
                                            {'salary_min': {'$gte': salary}},
                                            {'salary_max': {'$gte': salary}}
                                            ]}):
        return_list.append([item['title'], item['link']])

    return return_list


pprint(find_work(250_000))
