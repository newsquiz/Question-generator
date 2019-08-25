"""
    câu hỏi được đặt dựa trên 1 câu có sẵn trong bài
    câu đúng -> gĩư nguyên
    câu sai  -> thay đổi subject, object, adjective, adverb,...
                thay đổi entity, number theo easy multi choice quétions

    #TODO function check_digit()
"""
import re
import pdb
from utils import *

class EasyYesNoGenerator(object):
    def __init__(self):
        self.months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        self.days   = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    def get_question_yes(self, words, xpos, heads, labels, ners):
        """
            sinh câu hỏi yes-no cho các câu có dạng:
            - form 1: subject + verb (+ object) + ccomp/xcomp/nmod 
            - form 2: cop
        """
        questions = []
        answers = []
        verb_labels = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        adj_labels = ['JJ', 'JJR', 'JJS']
        noun_labels = ['NN', 'NNP', 'NNS', 'NNPS']
        nsubj_labels = ['nsubj', 'nsubjpass']
        for i in range(1, len(heads)):
            # check form
            is_q = False
            for j in range(1, len(heads)):
                if ((heads[j] == i) or (heads[j] == heads[i])) and (words[j] in QWORDS):
                    is_q = True
            if is_q:
                continue

            if (labels[i] in nsubj_labels) and (xpos[heads[i]] in verb_labels):
                subj_id = i
                verb_id = heads[i]
                has_obj = False
                has_comp = False
                for j in range(1, len(heads)):
                    if (heads[j] == verb_id):
                        if labels[j] == 'dobj':
                            has_obj = True
                        if labels[j] in ['ccomp', 'xcomp']:
                            has_comp = True
                if has_obj or has_comp:
                    # get auxiliary of verb
                    aux = ''
                    illegal_id = []
                    for j in range(1, len(heads)):
                        if (heads[j] == verb_id) and (labels[j] == 'aux'):
                            aux = ''
                            for k in range(1, len(labels)):
                                if (check_belong_to(j, k, heads)):
                                    aux += ' ' + words[k]
                                    illegal_id.append(k)
                    aux = aux[1:]
                    # remove punct both side
                    for j in range(1, len(heads)):
                        if words[j] in ['.', ',']:
                            illegal_id.append(j)
                        else:                
                            break
                    for j in range(len(heads)-1, -1, -1):
                        if words[j] in ['.', ',']:
                            illegal_id.append(j)
                        else:
                            break
                    # remove appos point to subject and words have index < subj_id
                    for j in range(1, len(heads)):
                        if ((heads[j] == subj_id) and (labels[j] in ['appos', 'punct'])) or ((j < subj_id) and (not check_belong_to(subj_id, j, heads)) and check_belong_to(verb_id, j, heads)):
                            for k in range(1, len(heads)):
                                if check_belong_to(j, k, heads):
                                    illegal_id.append(k)
                    # generate yes question
                    question = ''
                    for j in range(1, len(heads)):
                        if (j == verb_id):
                            if xpos[j] == 'VBZ':
                                question = 'does ' + question + ' ' + get_morphy(words[verb_id], xpos[verb_id])
                            elif xpos[j] == 'VBP':
                                question = 'do ' + question + ' ' + get_morphy(words[verb_id], xpos[verb_id])
                            elif xpos[j] == 'VBD':
                                question = 'did ' + question + ' ' + get_morphy(words[verb_id], xpos[verb_id])
                            else:
                                question = aux + ' ' + question + ' ' + words[verb_id]
                        if (heads[j] == verb_id) and (j not in illegal_id):
                            for k in range(1, len(heads)):
                                if (check_belong_to(j, k, heads)) and (k not in illegal_id):
                                    question += ' ' + words[k]
                    question += '?'
                    questions.append(question)
                    answers.append('yes')
        return questions, answers


    def get_question_no(self, questions_yes, ners):
        questions = []
        answers = []
        for question in questions_yes:
            replace_options = []
            # replace entity options
            for key in ners.keys():
                for val in ners[key]:
                    if val in question:
                        target = random_choice(ners[key], 1, [val])
                        if target != None:
                            replace_options.append((val, target))
            # replace month options
            for month in self.months:
                if month in question:
                    target = random_choice(self.months, 1, [month])
                    if target != None:
                        replace_options.append((month, target))
            # replace day in week options
            for day in self.days:
                if day in question:
                    target = random_choice(self.days, 1, [day])
                    if target != None:
                        replace_options.append((day, target))
            # replace number
            words = question.split(' ')
            for i, word in enumerate(words):
                if word.isdigit():
                    replace_number = int(words[i]) + random_choice([-1, 1, 2], 1, [])
                    raw = ' '.join(words[i-1:i+2])
                    target = ' '.join(words[i-1:i] + [str(replace_number)] + words[i+1:i+2])
                    replace_options.append((raw, target))
                if re.match('(\d{1,3})(\,\d{3})+', word) != None:
                    number = re.match('(\d{1,3})(\,\d{3})+', word).group(1)
                    replace_number = str(int(number) + random_choice([1, 2, 3], 1, [])) + word[len(number):]
                    raw = ' '.join(words[i-1:i+2])
                    target = ' '.join(words[i-1:i] + [str(replace_number)] + words[i+1:i+2])
                    replace_options.append((raw, target))
                if re.match('(\d{1,3})\.(\d{1,2})', word):
                    p = re.match('(\d{1,3})\.(\d{1,2})', word).group(1)
                    e = re.match('(\d{1,3})\.(\d{1,2})', word).group(2)
                    replace_number = str(int(p) + random_choice([1, 2, 3], 1, [])) + '.' + e
                    raw = ' '.join(words[i-1:i+2])
                    target = ' '.join(words[i-1:i] + [str(replace_number)] + words[i+1:i+2])
                    replace_options.append((raw, target))
                    replace_number = p + '.' + str(int(e) + random_choice([1, 2, 3], 1, []))
                    raw = ' '.join(words[i-1:i+2])
                    target = ' '.join(words[i-1:i] + [str(replace_number)] + words[i+1:i+2])
                    replace_options.append((raw, target))
            # choose one in list options
            if len(replace_options) > 0:
                random.shuffle(replace_options)
                question = question.replace(replace_options[0][0], replace_options[0][1])
                questions.append(question)
                answers.append('no')
        return questions, answers

    def get_questions(self, sentences, doc_ners):
        res_questions = []
        for i, sentence in sentences:
            words = sentence['words']
            xpos = sentence['xpos']
            heads = sentence['heads']
            labels = sentence['labels']
            ners = sentence['ners']
            questions_yes, answers_yes = self.get_question_yes(words, xpos, heads, labels, ners)
            questions_no, answers_no  = self.get_question_no(questions_yes, doc_ners)
            for question, answer in zip(questions_yes + questions_no, answers_yes + answers_no):
                res_question = {}
                res_question['sentence_index'] = i
                res_question['question_type'] = 'Yes-No-Question'
                res_question['level'] = 'Easy'
                res_question['tags'] = [answer, 'listening-comprehension']
                res_question['question'] = question
                res_question['answer'] = answer
                res_question['explain'] = ''
                res_questions.append(res_question)
        return res_questions