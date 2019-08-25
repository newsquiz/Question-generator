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
        if words[i] in HOMOPHONES_MEDIUM.keys():
            question = ' '.join(words[:i]) + ' _____ ' + ' '.join(words[i+1:])
            answer   = words[i]
            list_choice = random_choice(HOMOPHONES_MEDIUM[words[i]], 3, [words[i]])
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
                verb_base = verb_dictionary['verb_base_form'][verb_dictionary['verb_3rd_present'].index(verb)]
            if xpos[verb_id] == 'VBD':
                verb_base = verb_dictionary['verb_base_form'][verb_dictionary['verb_past_tense'].index(verb)]
            if xpos[verb_id] == 'VBG':
                verb_base = verb_dictionary['verb_base_form'][verb_dictionary['verb_gerund'].index(verb)]
            if xpos[verb_id] == 'VBN':
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
            # present perfect continuous
            candidates.append('have been ' + verb_dictionary['verb_gerund'][verb_dictionary['verb_base_form'].index(verb_base)])
            candidates.append('has been ' + verb_dictionary['verb_gerund'][verb_dictionary['verb_base_form'].index(verb_base)])
            # future simple
            candidates.append('will ' + verb_base)
            candidates.append('shall ' + verb_base)
            # future continuous
            candidates.append('will be ' + verb_dictionary['verb_gerund'][verb_dictionary['verb_base_form'].index(verb_base)])
            # future perfect
            candidates.append('will have ' + verb_dictionary['verb_past_participle'][verb_dictionary['verb_base_form'].index(verb_base)])
            # future perfect continuous
            candidates.append('will have been ' + verb_dictionary['verb_gerund'][verb_dictionary['verb_base_form'].index(verb_base)])
            # past continuous
            candidates.append('was ' + verb_dictionary['verb_gerund'][verb_dictionary['verb_base_form'].index(verb_base)])
            candidates.append('were ' + verb_dictionary['verb_gerund'][verb_dictionary['verb_base_form'].index(verb_base)])
            # past perfect
            candidates.append('had ' + verb_dictionary['verb_past_participle'][verb_dictionary['verb_base_form'].index(verb_base)])
            # past perfect continuous
            candidates.append('had been ' + verb_dictionary['verb_past_participle'][verb_dictionary['verb_base_form'].index(verb_base)])
            # add question
            question = ' '.join(words[:min_id]) + ' _____ ' + ' '.join(words[max_id:])
            random.shuffle(answers)
            questions.append(question)
            answers.append(verb)
            list_tags.append(['tense', 'grammar'])
            list_choices.append(random_choice(candidates, 3, [verb]) + [verb])
            explains.append("")
    return questions, answers, list_tags, list_choices, explains


def ff_phrasal_verb(words, xpos, heads, labels):
    """
        detect compound:prt relation
        -> change particle base on phrase verb dictionary
        -> if no others particle -> use preposition instead
    """
    questions = []
    answers = []
    list_tags = []
    list_choices = []
    explains = []
    for i in range(1, len(heads)):
        if (labels[i] == 'compound:prt') and (xpos[heads[i]] in verb_labels):
            particle = words[i]
            # get verb base
            verb_base = words[heads[i]]
            if xpos[i] == 'VBG':
                verb_base = verb_dictionary['verb_base_form'][verb_dictionary['verb_gerund'].index(verb_base)]
            if xpos[i] == 'VBN':
                verb_base = verb_dictionary['verb_base_form'][verb_dictionary['verb_past_participle'].index(verb_base)]
            if xpos[i] == 'VBD':
                verb_base = verb_dictionary['verb_base_form'][verb_dictionary['verb_past_tense'].index(verb_base)]
            if xpos[i] == 'VBZ':
                verb_base = verb_dictionary['verb_base_form'][verb_dictionary['verb_3rd_present'].index(verb_base)]
            # get list choices
            list_choice = []
            explain = ""
            if verb_base in PV_DICT.keys():
                for key in PV_DICT[verb_base].keys():
                    list_choice.append(key)
                    explain += verb_base.upper() + " " + key.upper() + "\n" + "    Meaning: " + PV_DICT[verb_base][key]['meaning'] + "\n" + "    Example: " + PV_DICT[verb_base][key]['example'] + "\n\n"
            else:
                continue
            if len(list_choice) < 4:
                list_choice = list_choice + random_choice(list_prep, 4 - len(list_choice), list_choice)
            question = ' '.join(words[:i]) + ' _____ ' + ' '.join(words[i+1:])
            answer = particle
            questions.append(question)
            answers.append(answer)
            list_tags.append(['phrasal_verb', 'grammar', 'vocab'])
            list_choices.append(list_choice)
            explains.append(explain)
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


class MediumFullfillGenerator(object):
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
            # generate phrasal verb
            _questions, _answers, _list_tags, _list_choices, _explains = ff_phrasal_verb(words, xpos, heads, labels)
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
                    res_question['level'] = 'Hard'
                    res_question['tags'] = tags
                    res_question['question'] = question
                    res_question['answer'] = answer
                    res_question['list_choices'] = list_choice
                    res_question['explain'] = explain
                    res_questions.append(res_question)
        return res_questions