"""
	Easy questions are generated base on relation tags
	Medium and hard questions are generated base on specific dependency tree shape
"""

from listening.short_answer.easy.easy_short_answer_generator import EasyShortAnswerGenerator

class ShortAnswerGenerator(object):
	def __init__(self):
		self.easy = EasyShortAnswerGenerator()

	def get_questions(self, data):
		questions = []
		# generate easy questions
		for question in self.easy.get_questions(data["raw_sentences"]):
			if "nummod" not in question["tags"]:
				question["level"] = "Medium"
			questions.append(question)
		### temp: medium question use easy question generator but on paraphrase sentences
		for question in self.easy.get_questions(data["paraphrase_sentences"]):
			if "nummod" not in question["tags"]:
				question["level"] = "Hard"
			else:
				question["level"] = "Medium"
			question["tags"].append("paraphrase")
			questions.append(question)
		###
		# return
		return questions