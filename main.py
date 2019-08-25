from reading.reading_generator import ReadingGenerator
from listening.listening_generator import ListeningGenerator
from db_utils import *
from tqdm import tqdm
import pdb

def main():
	reading_generator = ReadingGenerator()
	listening_generator = ListeningGenerator()
	# process all articles
	articles = get_all_articles()
	for article in tqdm(articles):
		questions = []
		print(article['title'])
		if article['type'] == 'audio':
			content = article['content'].replace('\n', ' ')
			questions = listening_generator.get_questions(content)
		elif article['type'] == 'text':
			questions = reading_generator.get_questions(article['content'])

		for question in questions:
			save_dict = {}
			save_dict['id'] = generate_id()
			save_dict['article_id'] = article['id']
			save_dict['sent_id'] = question['sentence_index']
			save_dict['type'] = question['question_type']
			save_dict['level'] = question['level']
			save_dict['tags'] = question['tags']
			save_dict['content'] = question['question']
			save_dict['answer'] = question['answer']
			if 'list_choices' in question.keys():
				save_dict['options'] = question['list_choices']
			if 'explain' in question.keys():
				save_dict['explain'] = question['explain']
			save_question(save_dict)


if __name__ == '__main__':
	main()