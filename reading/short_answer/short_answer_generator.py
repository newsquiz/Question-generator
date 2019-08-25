"""
    Easy questions are generated base on relation tags
    Medium and hard questions are generated base on specific dependency tree shape
"""

from reading.short_answer.easy.easy_short_answer_generator import EasyShortAnswerGenerator

class ShortAnswerGenerator(object):
    def __init__(self):
        self.easy = EasyShortAnswerGenerator()

    def get_questions(self, data):
        questions = []
        # generate easy questions
        questions += self.easy.get_questions(data["raw_sentences"])
        ### temp: medium question use easy question generator but on paraphrase sentences
        for question in self.easy.get_questions(data["paraphrase_sentences"]):
            question["level"] = "Medium"
            question["tags"].append("paraphrase")
            questions.append(question)
        ###
        # return
        return questions