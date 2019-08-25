"""
	easy short-answer questions are generated base on extract informations inside specific sentences
	- subject: not personal pronoun
	- datetime
	- location
"""
from generate_question_dp import *

class EasyShortAnswerGenerator(object):
	def __init__(self):
		pass

	def get_questions(self, sentences):
		"""
		TODO: dont generate question for question sentence
		"""
		res_questions = []
		for i, sentence in sentences:
			words = sentence['words']
			xpos = sentence['xpos']
			heads = sentence['heads']
			labels = sentence['labels']
			ners = sentence['ners']
			processed_relation = []
			# abstract lv1
			questions, answers, list_tags = get_question_abstract_tree_lv1(words, xpos, heads, labels, ners)
			for tags in list_tags:
				processed_relation += tags
			# subject
			if 'subj' not in processed_relation:
				_questions, _answers, _list_tags = generate_subj_question(words, xpos, heads, labels, ners)
				questions += _questions
				answers += _answers
				list_tags += _list_tags
			# ccomp/xcomp
			if 'ccomp/xcomp' not in processed_relation:
				_questions, _answers, _list_tags = generate_ccomp_xcomp_question(words, xpos, heads, labels, ners)
				questions += _questions
				answers += _answers
				list_tags += _list_tags
			# nmod
			if 'nmod' not in processed_relation:
				_questions, _answers, _list_tags = generate_nmod_question(words, xpos, heads, labels, ners)
				questions += _questions
				answers += _answers
				list_tags += _list_tags
			# nummod
			if 'nummod' not in processed_relation:
				_questions, _answers, _list_tags = generate_nummod_question(words, xpos, heads, labels, ners)
				questions += _questions
				answers += _answers
				list_tags += _list_tags
			# object
			if 'dobj' not in processed_relation:
				_questions, _answers, _list_tags = generate_obj_question(words, xpos, heads, labels, ners)
				questions += _questions
				answers += _answers
				list_tags += _list_tags

			for question, answer, tags in zip(questions, answers, list_tags):
				res_question = {}
				res_question['sentence_index'] = i
				res_question['question_type'] = 'Short-Answer-Question'
				res_question['level'] = 'Easy'
				res_question['tags'] = tags + ["reading-comprehension"]
				res_question['question'] = question
				res_question['answer'] = answer
				res_question['explain'] = ''
				res_questions.append(res_question)
		return res_questions
		