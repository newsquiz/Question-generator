from reading.yes_no.easy.easy_yes_no_generator import EasyYesNoGenerator

class YesNoGenerator(object):
    def __init__(self):
        self.easy = EasyYesNoGenerator()

    def get_questions(self, data):
        questions = []
        # generate easy questions
        questions += self.easy.get_questions(data["raw_sentences"], data["ners"])
        ### temp: medium question use easy question generator but on paraphrase sentences
        for question in self.easy.get_questions(data["paraphrase_sentences"], data["ners"]):
            question["level"] = "Medium"
            question["tags"].append("paraphrase")
            questions.append(question)
        ###
        # return
        return questions