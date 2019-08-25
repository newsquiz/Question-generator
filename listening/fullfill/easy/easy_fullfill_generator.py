"""
    TODO: topic newwords
    TODO: tense: verb must have nsubject relation
"""

import re
import random
from utils import *

verb_labels = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
adj_labels = ['JJ', 'JJR', 'JJS']
noun_labels = ['NN', 'NNP', 'NNS', 'NNPS']
nsubj_labels = ['nsubj', 'nsubjpass']
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
days   = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
list_prep = ['in', 'on', 'at', 'into', 'up', 'with', 'upon', 'off', 'onto', 'out', 'away', 'around', 'from', 'by', 'for']

def ff_homophones(words, xpos, heads, labels):
    questions = []
    answers = []
    list_tags = []
    list_choices = []
    explains = []
    for i in range(1, len(heads)):
        if words[i] in HOMOPHONES_EASY.keys():
            question = ' '.join(words[:i]) + ' _____ ' + ' '.join(words[i+1:])
            answer   = words[i]
            list_choice = random_choice(HOMOPHONES_EASY[words[i]], 3, [words[i]])
            questions.append(question)
            answers.append(answer)
            list_tags.append(['homophone', 'phonetic'])
            list_choices.append(list_choice)
            explains.append("")
    return questions, answers, list_tags, list_choices, explains


def ff_tense(words, xpos, heads, labels):
    """
        change verb and aux to get question about tense
        detect tense 
        type 1: ff  -> return question and verb answer
        type 2: ff4 -> generate all posible answer -> choose 4 -> return
    """
    questions = []
    answers = []
    list_tags = []
    list_choices = []
    explains = []
    for i in range(1, len(heads)):
        if (xpos[i] in verb_labels):
            verb_id = i
            # check has nsubject relation
            has_nsubj = False
            for j in range(1, len(heads)):
                if (heads[j] == verb_id) and (labels[j] in nsubj_labels):
                    has_nsubj = True
            if not has_nsubj:
                continue
            # detect verb and its aux
            is_neg = False
            min_id = verb_id
            max_id = verb_id + 1
            verb = words[verb_id]
            aux = ''
            for j in range(1, len(heads)):
                if (heads[j] == verb_id):
                    if (labels[j] in ['aux', 'auxpass']):
                        aux += ' ' + words[j]
                        min_id = min(min_id, j)
                        max_id = max(max_id, j)
                    if (labels[j] == 'neg'):
                        is_neg = True
            aux = aux[1:]
            # check if has negative relation point to verb
            if is_neg:
                continue
            # generate ff4
            candidates = []
            verb_base = verb
            if xpos[verb_id] == 'VBZ':
                if verb not in verb_dictionary['verb_3rd_present']:
                    continue
                verb_base = verb_dictionary['verb_base_form'][verb_dictionary['verb_3rd_present'].index(verb)]
            if xpos[verb_id] == 'VBD':
                if verb not in verb_dictionary['verb_past_tense']:
                    continue
                verb_base = verb_dictionary['verb_base_form'][verb_dictionary['verb_past_tense'].index(verb)]
            if xpos[verb_id] == 'VBG':
                if verb not in verb_dictionary['verb_gerund']:
                    continue
                verb_base = verb_dictionary['verb_base_form'][verb_dictionary['verb_gerund'].index(verb)]
            if xpos[verb_id] == 'VBN':
                if verb not in verb_dictionary['verb_past_participle']:
                    continue
                verb_base = verb_dictionary['verb_base_form'][verb_dictionary['verb_past_participle'].index(verb)]
            # generate candidate in all tense
            # present simple
            candidates.append(verb_base)
            candidates.append(verb_dictionary['verb_3rd_present'][verb_dictionary['verb_base_form'].index(verb_base)])
            # past simple
            candidates.append(verb_dictionary['verb_past_tense'][verb_dictionary['verb_base_form'].index(verb_base)])
            # present continuous
            candidates.append('is ' + verb_dictionary['verb_gerund'][verb_dictionary['verb_base_form'].index(verb_base)])
            candidates.append('are ' + verb_dictionary['verb_gerund'][verb_dictionary['verb_base_form'].index(verb_base)])
            # present perfect
            candidates.append('have ' + verb_dictionary['verb_past_participle'][verb_dictionary['verb_base_form'].index(verb_base)])
            candidates.append('has ' + verb_dictionary['verb_past_participle'][verb_dictionary['verb_base_form'].index(verb_base)])
            # future simple
            candidates.append('will ' + verb_base)
            candidates.append('shall ' + verb_base)
            # add question
            question = ' '.join(words[:min_id]) + ' _____ ' + ' '.join(words[max_id:])
            random.shuffle(answers)
            questions.append(question)
            answers.append(verb)
            list_tags.append(['tense', 'grammar'])
            list_choices.append(random_choice(candidates, 3, [verb]) + [verb])
            explains.append("")
    return questions, answers, list_tags, list_choices, explains


def ff_entity(words, xpos, heads, labels, ners):
    """
        remove DATE, TIME, NUMBER
    """
    questions = []
    answers = []
    list_tags = []
    list_choices = []
    explains = []
    # replace month options
    for month in months:
        if month in words:
            list_choice = random_choice(months, 3, [month]) + [month]
            question = ' '.join(words).replace(month, '_____')
            # add ff4
            questions.append(question)
            answers.append(month)
            list_tags.append(['DATE', 'listening-comprehension'])
            list_choices.append(list_choice)
            explains.append("")
    # replace day in week options
    for day in days:
        if day in words:
            list_choice = random_choice(days, 3, [day]) + [day]
            question = ' '.join(words).replace(day, '_____')
            # add ff4
            questions.append(question)
            answers.append(day)
            list_tags.append(['DATE', 'listening-comprehension'])
            list_choices.append(list_choice)
            explains.append("")
    # replace number
    for i, word in enumerate(words):
        if word.isdigit():
            list_choice = [str(int(words[i]) - 1), words[i], str(int(words[i]) + 1), str(int(words[i]) + 2)]
            raw = ' '.join(words[i-1:i+2])
            target = ' '.join(words[i-1:i] + ['_____'] + words[i+1:i+2])
            question = ' '.join(words).replace(raw, target)
            # add ff4
            questions.append(question)
            answers.append(word)
            list_tags.append(['NUMBER', 'listening-comprehension'])
            list_choices.append(list_choice)
            explains.append("")
        if re.match('(\d{1,3})(\,\d{3})+', word) != None:
            number = re.match('(\d{1,3})(\,\d{3})+', word).group(1)
            list_choice = [word, str(int(number) + 1) + word[len(number):], str(int(number) + 2) + word[len(number):], str(int(number) + 3) + word[len(number):]]
            raw = ' '.join(words[i-1:i+2])
            target = ' '.join(words[i-1:i] + [str(replace_number)] + words[i+1:i+2])
            question = ' '.join(words).replace(raw, target)
            # add ff4
            questions.append(question)
            answers.append(word)
            list_tags.append(['NUMBER', 'listening-comprehension'])
            list_choices.append(list_choice)
            explains.append("")
        if re.match('(\d{1,3})\.(\d{1,2})', word):
            p = re.match('(\d{1,3})\.(\d{1,2})', word).group(1)
            e = re.match('(\d{1,3})\.(\d{1,2})', word).group(2)
            # add ff4 for p
            list_choice = [word, str(int(p) + 1) + '.' + e, str(int(p) + 2) + '.' + e, str(int(p) + 3) + '.' + e]
            raw = ' '.join(words[i-1:i+2])
            target = ' '.join(words[i-1:i] + [str(replace_number)] + words[i+1:i+2])
            question = ' '.join(words).replace(raw, target)
            questions.append(question)
            answers.append(word)
            list_tags.append(['NUMBER', 'listening-comprehension'])
            list_choices.append(list_choice)
            explains.append("")
            # add ff4 for e
            list_choice = [word, p + '.' + str(int(e) + 1), p + '.' + str(int(e) + 2), p + '.' + str(int(e) + 3)]
            raw = ' '.join(words[i-1:i+2])
            target = ' '.join(words[i-1:i] + [str(replace_number)] + words[i+1:i+2])
            replace_options.append((raw, target))
            question = ' '.join(words).replace(raw, target)
            questions.append(question)
            answers.append(word)
            list_tags.append(['NUMBER', 'listening-comprehension'])
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
        if words[i] in OXFORD_EASY.keys():
            if ((xpos[i] in noun_labels) and (OXFORD_EASY[words[i]]['pos'] == 'noun')) or ((xpos[i] in adj_labels) and (OXFORD_EASY[words[i]]['pos'] == 'adj')):
                question = ' '.join(words[:i]) + ' _____ ' + ' '.join(words[i+1:])
                answer = words[i]
                tags = ['vocab']
                list_choice = []
                explain = OXFORD_EASY[words[i]]['meaning']
                questions.append(question)
                answers.append(answer)
                list_tags.append(tags)
                list_choices.append(list_choice)
                explains.append(explain)
    return questions, answers, list_tags, list_choices, explains 


class EasyFullfillGenerator(object):
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
            # generate tense
            _questions, _answers, _list_tags, _list_choices, _explains = ff_tense(words, xpos, heads, labels)
            questions += _questions
            answers += _answers
            list_tags += _list_tags
            list_choices += _list_choices
            explains += _explains
            # generate entity
            _questions, _answers, _list_tags, _list_choices, _explains = ff_entity(words, xpos, heads, labels, ners)
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
                res_question['level'] = 'Easy'
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