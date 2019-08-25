"""

"""

from listening.fullfill.easy.easy_fullfill_generator import EasyFullfillGenerator
from listening.fullfill.medium.medium_fullfill_generator import MediumFullfillGenerator
from listening.fullfill.hard.hard_fullfill_generator import HardFullfillGenerator

class FullfillGenerator(object):
	def __init__(self):
		self.easy = EasyFullfillGenerator()
		self.medium = MediumFullfillGenerator()
		self.hard = HardFullfillGenerator()

	def get_questions(self, data):
		questions = []
		# generate easy questions
		questions += self.easy.get_questions(data["raw_sentences"])
		# generate medium questions
		questions += self.medium.get_questions(data["raw_sentences"])
		# generate hard questions
		questions += self.hard.get_questions(data["raw_sentences"])
		# return
		return questions