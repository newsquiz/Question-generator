"""
    câu hỏi lựa chọn dễ sinh dựa trên câu gốc
    câu hỏi lựa chọn khó và vừa sinh dựa trên câu đã paraphase
    đáp áp:
    - nếu đáp án ngắn dạng người, địa điểm, tổ chức -> xác định NP tương tự trong đoạn làm đáp án
    - nếu đáp án dài -> khẳng định, phủ định, pa-ra-pha-se,...
"""
from reading.multi_choice.easy.easy_multi_choice_generator import EasyMultiChoiceGenerator

class MultiChoiceGenerator(object):
    def __init__(self):
        self.easy = EasyMultiChoiceGenerator()

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