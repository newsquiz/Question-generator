#TODO: Thanh: add question classes representing for different question type
#These definition is subect to change :D

class Question(object):

    def __init__(self):
        pass

    def get_answers(self):
        '''Return a list of answer.'''
        pass

    def is_answer_correct(self):
        pass

    @staticmethod
    def build_from_dict(task, djson):
        'Deserilization appropriate question object form json'
        if task == 'write':
            if str(djson['task'])=='1':
                return WritingTask1.from_dict(djson)
            else:
                return WritingTask2.from_dict(djson)

    def from_dict(self, djson):
        'Catch json data in request body to object which will be used in eval.'
        pass

    def to_dict(self, djson):
        'Generate json data from objects might be used in quention generator. E.g. submit new question to data/backend'
        pass

class MultiChoice(list):
    pass

class FillBlankQuestion(Question):
   
    def __init__(self, text, choices, correct_answers, user_answer=None):
        self.text = text
        self.choices = choices
        self.correct_answer = correct_answer
        self.user_answer = user_answer

class ShortAnswerQuestion(Question):
   
    def __init__(self, text, choices, correct_answers, user_answer=None):
        self.text = text
        self.choices = choices
        self.correct_answer = correct_answer
        self.user_answer = user_answer

class MatchingQuestion(Question):
   
    def __init__(self, first_list, second_list, correct_answers, user_answer=None):
        self.first_list = first_list
        self.second_list = second_list
        self.correct_answer = correct_answer
        self.user_answer = user_answer

class WritingTask1(Question):

    def __init__(self, question_text, data, figure_url, answer_text=None):
        self.quest_text = text
        self.data = data
        self.figure_url = figure_url
        self.answer_text = answer_text

    @staticmethod
    def from_dict(djson):
        qtext = djson['qtext']
        data = djson['data']
        figure_url = djson['figure_url']
        atext = djson['atext']
        return WritingTask1(qtext, data, figure_url, atext)

class WritingTask2(Question):

    def __init__(self, question_text, answer_text=None):
        self.quest_text = question_text
        self.answer_text = answer_text

    @staticmethod
    def from_dict(djson):
        qtext = djson['qtext']
        atext = djson['atext']
        return WritingTask2(qtext, atext)



