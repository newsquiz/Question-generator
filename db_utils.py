from pymongo import MongoClient
import datetime
import random 
import os
import uuid

MONGO_HOST = '172.104.185.102'
MONGO_PORT = 8600
MONGO_DB = 'newsquiz'
# client = MongoClient(MONGO_HOST, MONGO_PORT)
client = MongoClient("mongodb://newsquiz:grdVGACnq%242019@172.104.185.102:8600/admin?connectTimeoutMS=10000&authSource=admin&authMechanism=SCRAM-SHA-1")
db = client[MONGO_DB]
question_collection = db.questions
article_collection  = db.articles

def generate_id():
    fname = uuid.uuid5(uuid.NAMESPACE_OID, str(datetime.datetime.now()))
    return str(fname).replace('-', '')

def get_all_article_by_date(date):
	articles = article_collection.find({'created_time': {'$gt': date}}, no_cursor_timeout = True)
	return articles


def get_all_articles():
	articles = article_collection.find()
	return articles


def get_all_questions():
	questions = question_collection.find()
	return questions

def check_processed_article(article_id):
	questions = question_collection.find({'id': article_id}, no_cursor_timeout = True)
	if len(questions) == 0:
		return False
	return True

def save_question(question):
	question_collection.insert_one(question)


if __name__ == '__main__':
	sample_question = {
		'id'     : '123456789',
		'content': 'what is?',
		'type'   : 'fullfill',
		'level'  : 'easy',
		'value'  : 'reading comprehension',
		'tags'   : [
			'vocabulary',
			'DATE',
		],
		'answer' : 'D',
		'options': [
			'A',
			'B',
			'C',
			'D'
		],
		'explaination': ''
	}