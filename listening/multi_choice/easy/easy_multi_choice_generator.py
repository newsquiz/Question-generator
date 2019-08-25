"""
	câu hỏi lựa chọn dễ sinh dựa trên câu hỏi sinh ra từ câu gốc
	lựa chọn các câu có các tags PERSON, LOCATION, ORGNIZATION làm câu hỏi:
	- 4 đáp án bao gồm các Entity khác xuất hiện trong đoạn
	- Nếu Entity cùng loại không đủ 4 -> lấy thêm từ Entity tương đồng
	- Nếu < 4 đáp án -> loại
	câu có tags TIME, DATE, NUMBER:
	- thay đổi gía trị gần với đáp án
	lựa chọn câu có đáp án là 1 phrase

	TODO:
	- sinh câu có đáp án là 1 phrase hoặc 1 câu hoàn chỉnh
"""
import re
import pdb
import random
from generate_question_dp import *

class EasyMultiChoiceGenerator(object):
	def __init__(self):
		self.months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
		self.days   = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

	def get_candidates(self, sentences):
		candidates = []
		for i, sentence in sentences:
			words = sentence['words']
			xpos = sentence['xpos']
			heads = sentence['heads']
			labels = sentence['labels']
			ners = sentence['ners']
			questions = []
			answers = []
			list_tags = []
			# subject
			_questions, _answers, _list_tags = generate_subj_question(words, xpos, heads, labels, ners)
			questions += _questions
			answers += _answers
			list_tags += _list_tags
			# ccomp/xcomp
			_questions, _answers, _list_tags = generate_ccomp_xcomp_question(words, xpos, heads, labels, ners)
			questions += _questions
			answers += _answers
			list_tags += _list_tags
			# nmod
			_questions, _answers, _list_tags = generate_nmod_question(words, xpos, heads, labels, ners)
			questions += _questions
			answers += _answers
			list_tags += _list_tags
			# nummod
			_questions, _answers, _list_tags = generate_nummod_question(words, xpos, heads, labels, ners)
			questions += _questions
			answers += _answers
			list_tags += _list_tags
			# object
			_questions, _answers, _list_tags = generate_obj_question(words, xpos, heads, labels, ners)
			questions += _questions
			answers += _answers
			list_tags += _list_tags

			for question, answer, tags in zip(questions, answers, list_tags):
				candidate = {}
				candidate['sentence_index'] = i
				candidate['question_type'] = 'Multi-Choice-Question'
				candidate['level'] = 'Easy'
				candidate['tags'] = tags + ['listening-comprehension']
				candidate['question'] = question
				candidate['answer'] = answer
				candidate['explain'] = ''
				candidates.append(candidate)
		return candidates

	def process_candidate(self, candidate, ners):
		# process ENTITY tags questions
		if ('PERSON' in candidate['tags']) and (candidate['answer'] in ners['PERSON']):
			if len(ners['PERSON']) >= 4:
				top_answers = ners['PERSON']
			elif len(ners['PERSON'] + ners['ORGANIZATION']) >= 4:
				top_answers = ners['PERSON'] + ners['ORGANIZATION']
			else:
				return None
			random.shuffle(top_answers)
			list_choices = [candidate['answer']] + [answer for answer in top_answers if answer != candidate['answer']]
			list_choices = list_choices[:4]
			random.shuffle(list_choices)
			candidate['list_choices'] = list_choices
			return candidate

		if ('ORGANIZATION' in candidate['tags']) and (candidate['answer'] in ners['ORGANIZATION']):
			if len(ners['ORGANIZATION']) >= 4:
				top_answers = ners['ORGANIZATION']
			elif len(ners['ORGANIZATION'] + ners['PERSON']) >= 4:
				top_answers = ners['ORGANIZATION'] + ners['PERSON']
			else:
				return None
			random.shuffle(top_answers)
			list_choices = [candidate['answer']] + [answer for answer in top_answers if answer != candidate['answer']]
			list_choices = list_choices[:4]
			random.shuffle(list_choices)
			candidate['list_choices'] = list_choices
			return candidate

		if ('LOCATION' in candidate['tags']) and (candidate['answer'] in ners['LOCATION']):
			if len(ners['LOCATION']) >= 4:
				top_answers = ners['LOCATION']
			elif len(ners['LOCATION'] + ners['COUNTRY']) >= 4:
				top_answers = ners['LOCATION'] + ners['COUNTRY']
			else:
				return None
			random.shuffle(top_answers)
			list_choices = [candidate['answer']] + [answer for answer in top_answers if answer != candidate['answer']]
			list_choices = list_choices[:4]
			random.shuffle(list_choices)
			candidate['list_choices'] = list_choices
			return candidate

		if ('COUNTRY' in candidate['tags']) and (candidate['answer'] in ners['COUNTRY']):
			if len(ners['COUNTRY']) >= 4:
				top_answers = ners['COUNTRY']
			elif len(ners['COUNTRY'] + ners['LOCATION']) >= 4:
				top_answers = ners['COUNTRY'] + ners['LOCATION']
			else:
				return None
			random.shuffle(top_answers)
			list_choices = [candidate['answer']] + [answer for answer in top_answers if answer != candidate['answer']]
			list_choices = list_choices[:4]
			random.shuffle(list_choices)
			candidate['list_choices'] = list_choices
			return candidate

		if ('TIME' in candidate['tags']):
			split_time = candidate['answer'].split(' ')
			top_answers = []
			for i in range(len(split_time)):
				if split_time[i].isdigit():
					for nummod in [-1, 1, 2]:
						can_choice = ' '.join(split_time[:i] + [str(int(split_time[i]) + nummod)] + split_time[i+1:])
						top_answers.append(can_choice)
			if len(top_answers) < 3:
				return None
			random.shuffle(top_answers)
			list_choices = [candidate['answer']] + [answer for answer in top_answers if answer != candidate['answer']]
			list_choices = list_choices[:4]
			random.shuffle(list_choices)
			candidate['list_choices'] = list_choices
			return candidate

		if ('DATE' in candidate['tags']):
			split_date = candidate['answer'].split(' ')
			top_answers = []
			for i in range(len(split_date)):
				if split_date[i].isdigit():
					for nummod in [-1, 1, 2]:
						can_choice = ' '.join(split_date[:i] + [str(int(split_date[i]) + nummod)] + split_date[i+1:])
						top_answers.append(can_choice)
				if split_date[i] in self.months:
					for nummod in [-1, 1, 2]:
						can_choice = ' '.join(split_date[:i] + [self.months[(self.months.index(split_date[i]) + nummod)%len(self.months)]] + split_date[i+1:])
						top_answers.append(can_choice)
				if split_date[i] in self.days:
					for nummod in [-1, 1, 2]:
						can_choice = ' '.join(split_date[:i] + [self.days[(self.days.index(split_date[i]) + nummod)%len(self.days)]] + split_date[i+1:])
						top_answers.append(can_choice)
				if re.match('(\d{4})s', split_date[i]) != None:
					year = re.match('(\d{4})s', split_date[i]).group(1)
					for nummod in [-1, 1, 2]:
						can_choice = ' '.join(split_date[:i] + [str(int(year[:3]) + nummod) + year[3:]] + split_date[i+1:])
						top_answers.append(can_choice)
			if len(top_answers) < 3:
				return None
			random.shuffle(top_answers)
			list_choices = [candidate['answer']] + [answer for answer in top_answers if answer != candidate['answer']]
			list_choices = list_choices[:4]
			random.shuffle(list_choices)
			candidate['list_choices'] = list_choices
			return candidate

		if ('nummod' in candidate['tags']):
			split_nummod = candidate['answer'].split(' ')
			top_answers = []
			for i in range(len(split_nummod)):
				if split_nummod[i].isdigit():
					for nummod in [-1, 1, 2]:
						can_choice = ' '.join(split_nummod[:i] + [str(int(split_nummod[i]) + nummod)] + split_nummod[i+1:])
						top_answers.append(can_choice)
			if len(top_answers) < 3:
				return None
			random.shuffle(top_answers)
			list_choices = [candidate['answer']] + [answer for answer in top_answers if answer != candidate['answer']]
			list_choices = list_choices[:4]
			random.shuffle(list_choices)
			candidate['list_choices'] = list_choices
			return candidate

		# process phrase or full sentence answer
		# TODO
		
			

	def get_questions(self, sentences, ners):
		"""
		TODO: dont generate question for question sentence
		"""
		res_questions = []
		# get all candidates
		candidates = self.get_candidates(sentences)
		# choose suitable candidates and generate list answers
		for candidate in candidates:
			res_question = self.process_candidate(candidate, ners)
			if res_question != None:
				res_questions.append(res_question)
		return res_questions
		