import re
import random
from utils import *


def ff_homophones(words, xpos, heads, labels):
    questions = []
    answers = []
    list_tags = []
    list_choices = []
    explains = []
    for i in range(1, len(heads)):
        if words[i] in HOMOPHONES_HARD.keys():
            question = ' '.join(words[:i]) + ' _____ ' + ' '.join(words[i+1:])
            answer   = words[i]
            list_choice = random_choice(HOMOPHONES_HARD[words[i]], 3, [words[i]])
            questions.append(question)
            answers.append(answer)
            list_tags.append(['homophone', 'phonetic'])
            list_choices.append(list_choice)
            explains.append("")
    return questions, answers, list_tags, list_choices, explains


def ff_topic_newwords(words, xpos, heads, labels):
    questions = []
    answers = []
    list_tags = []
    list_choices = []
    explains = []
    for i in range(1, len(heads)):
        if words[i] in OXFORD_MEDIUM.keys():
            if ((xpos[i] in noun_labels) and (OXFORD_MEDIUM[words[i]]['pos'] == 'noun')) or ((xpos[i] in adj_labels) and (OXFORD_MEDIUM[words[i]]['pos'] == 'adj')):
                question = ' '.join(words[:i]) + ' _____ ' + ' '.join(words[i+1:])
                answer = words[i]
                tags = ['vocab']
                list_choice = []
                explain = OXFORD_MEDIUM[words[i]]['meaning']
                questions.append(question)
                answers.append(answer)
                list_tags.append(tags)
                list_choices.append(list_choice)
                explains.append(explain)
    return questions, answers, list_tags, list_choices, explains


class HardFullfillGenerator(object):
    def __init__(self):
        pass

    def get_questions(self, sentences):
        res_questions = []
        for i, sentence in sentences:
            words = sentence['words']
            xpos = sentence['xpos']
            heads = sentence['heads']
            labels = sentence['labels']
            ners = sentence['ners']
            questions = []
            answers = []
            list_tags = []
            list_choices = []
            explains = []
            # generate homophones
            _questions, _answers, _list_tags, _list_choices, _explains = ff_homophones(words, xpos, heads, labels)
            questions += _questions
            answers += _answers
            list_tags += _list_tags
            list_choices += _list_choices
            explains += _explains
            # generate topic newword
            _questions, _answers, _list_tags, _list_choices, _explains = ff_topic_newwords(words, xpos, heads, labels)
            questions += _questions
            answers += _answers
            list_tags += _list_tags
            list_choices += _list_choices
            explains += _explains

            for question, answer, tags, list_choice, explain in zip(questions, answers, list_tags, list_choices, explains):
                # add fullfill
                res_question = {}
                res_question['sentence_index'] = i
                res_question['question_type'] = 'Fullfill'
                res_question['level'] = 'Medium'
                res_question['tags'] = tags
                res_question['question'] = question
                res_question['answer'] = answer
                res_question['explain'] = explain
                res_questions.append(res_question)
                # add fullfill multichoice
                if len(list_choice) != 0:
                    res_question = {}
                    res_question['sentence_index'] = i
                    res_question['question_type'] = 'Fullfill-MultiChoice'
                    res_question['level'] = 'Medium'
                    res_question['tags'] = tags
                    res_question['question'] = question
                    res_question['answer'] = answer
                    res_question['list_choices'] = list_choice
                    res_question['explain'] = explain
                    res_questions.append(res_question)
        return res_questions