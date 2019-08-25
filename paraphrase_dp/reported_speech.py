"""
    can't find gender of subject
    #TODO: use coreference to detect gender of subject, object...
    wrong tree: note ccomp but xcomp and advcl tags

"""

import numpy as np 
from utils import *
import pdb

MODAL_VERB = ['can', 'may', 'must', 'could', 'might', 'should']
CHANGE_MODAL_VERB = ['could', 'might', 'had to', 'could', 'might', 'should']
PERSONAL_PRONOUN = ['I', 'we', 'you', 'me', 'us', 'myself', 'ourselves', 'yourself', 'yourselves']
CHANGE_PERSONAL_PRONOUN = ['she', 'they', 'they', 'her', 'them', 'herself', 'themselves', 'herself', 'themselves']
POSSESSIVE_PRONOUN = ['my', 'our', 'your', 'mine', 'ours', 'yours']
CHANGE_POSSESSIVE_PRONOUN = ['her', 'their', 'their', 'hers', 'theirs', 'theirs']

verb_labels = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
adj_labels = ['JJ', 'JJR', 'JJS']
noun_labels = ['NN', 'NNP', 'NNS', 'NNPS']
nsubj_labels = ['nsubj', 'nsubjpass']

def check_rsp_condition(words, xpos, heads, labels, ners):
    # check root is verb and its morphy in ['say', 'tell']
    verb_id = -1
    for i in range(1, len(heads)):
        if (heads[i] == 0) and get_morphy(words[i], xpos[i]) in ['say', 'tell']:
            verb_id = i
    if verb_id == -1:
        return None
    # check has subject and subject tag is not PRP
    nsubj_id = -1
    for i in range(1, len(heads)):
        if (heads[i] == verb_id) and (labels[i] in nsubj_labels) and (xpos[i] != 'PRP'):
            nsubj_id = i 
    if nsubj_id == -1:
        return None
    # check has direct speech with quotation marks
    # signal: " --comp-- "
    clause_id = -1
    # check if clause is on the left of verb
    qm_ids = []
    ccomp_id = -1
    for i in range(1, verb_id):
        if (heads[i] == verb_id):
            if (labels[i] in ['ccomp', 'dep', 'xcomp']):
                ccomp_id = i
    for i in range(1, verb_id):
        if (heads[i] == verb_id) or (heads[i] == ccomp_id):
            if (words[i] in ['"', '``', "''"]):
                qm_ids.append(i)
    if (len(qm_ids) > 0) and (qm_ids[0] < ccomp_id) and (ccomp_id < qm_ids[-1]):
        clause_id = ccomp_id
    # check if clause is on the right of verb
    qm_ids = []
    ccomp_id = -1
    for i in range(verb_id, len(heads)):
        if (heads[i] == verb_id):
            if (labels[i] in ['ccomp', 'dep', 'xcomp']):
                ccomp_id = i
    for i in range(verb_id, len(heads)):
        if (heads[i] == verb_id) or (heads[i] == ccomp_id):
            if (words[i] in ['"', '``', "''"]):
                qm_ids.append(i)
    if (len(qm_ids) > 0) and (qm_ids[0] < ccomp_id) and (ccomp_id < qm_ids[-1]):
        clause_id = ccomp_id
    if clause_id == -1:
        return None
    return verb_id, nsubj_id, clause_id

def change_verb_tense(aux, verb, pos):
    res = aux + ' ' + verb
    if aux == '':
        # present simple
        if pos in ['VB', 'VBP']:
            if verb in verb_dictionary['verb_base_form']:
                res = verb_dictionary['verb_past_tense'][verb_dictionary['verb_base_form'].index(verb)]
            else:
                res = verb
        # past simple
        if pos == 'VBZ':
            if verb in verb_dictionary['verb_3rd_present']:
                res = verb_dictionary['verb_past_tense'][verb_dictionary['verb_3rd_present'].index(verb)]
            else:
                res = verb
    else:
        # present continuous
        if (aux == 'is') and (pos == 'VBG'):
            res = 'was ' + verb
        if (aux == 'are') and (pos == 'VBG'):
            res = 'were ' + verb
        # present perfect
        if (aux in ['have', 'has']) and (pos == 'VBN'):
            res = 'had ' + verb
        # present perfect continuous
        if (aux in ['have been', 'has been']) and (pos == 'VBG'):
            res = 'had been ' + verb
        # future simple
        if (aux == 'will') and (pos in ['VB', 'VBP']):
            res = 'would ' + verb
        # future continuous
        if (aux == 'will be') and (pos in ['VBG']):
            res = 'would be ' + verb
        # future perfect
        if (aux == 'will have') and (pos == 'VBN'):
            res = 'would have ' + verb
        # future perfect continuous
        if (aux == 'will have been') and (pos == 'VBG'):
            res = 'would have been ' + verb
        # past continuous
        if (aux in ['was', 'were']) and (pos == 'VBG'):
            res = 'had been ' + verb
        # past perfect
        if (aux == 'had') and (pos == 'VBN'):
            res = aux + ' ' + verb
        # past perfect continuous
        if (aux == 'had been') and (pos == 'VBG'):
            res = aux + ' ' + verb
    return res


def reported_speech_paraphrase(words, xpos, heads, labels, ners):
    # check whether input sentence is direct speech sentence
    check_condition = check_rsp_condition(words, xpos, heads, labels, ners)
    if check_condition == None:
        return None
    verb_id, nsubj_id, clause_id = check_condition
    # get nsubject
    nsubj = ""
    for i in range(1, len(heads)):
        if check_belong_to(nsubj_id, i, heads):
            nsubj += ' ' + words[i]
    nsubj = nsubj[1:]
    # get verb
    if get_morphy(words[verb_id], xpos[verb_id]) not in verb_dictionary['verb_base_form']:
        return None
    if clause_id < verb_id:
        verb = verb_dictionary['verb_past_tense'][verb_dictionary['verb_base_form'].index(get_morphy(words[verb_id], xpos[verb_id]))]
        for i in range(verb_id + 1, len(heads)):
            if check_belong_to(verb_id, i, heads) and not check_belong_to(clause_id, i, heads):
                verb += ' ' + words[i]
    elif clause_id > verb_id:
        verb = verb_dictionary['verb_past_tense'][verb_dictionary['verb_base_form'].index(get_morphy(words[verb_id], xpos[verb_id]))]
        for i in range(verb_id + 1, clause_id):
            if check_belong_to(verb_id, i, heads) and not check_belong_to(clause_id, i, heads):
                verb += ' ' + words[i]
    # get reported clause
    reported_clause = ""
    # pdb.set_trace()
    for i in range(1, len(heads)):
        if check_belong_to(clause_id, i, heads) and ((labels[i] not in ['aux', 'auxpass', 'punct']) or ((xpos[i] == 'MD') and (words[i] != 'will'))):
            word = words[i]
            if xpos[i] in verb_labels:
                aux = ""
                for j in range(1, len(heads)):
                    if (heads[j] == i) and (labels[j] in ['aux', 'auxpass']) and ((xpos[j] != 'MD') or (words[j] == 'will')):
                        aux += ' ' + words[j]
                aux = aux[1:]
                word = change_verb_tense(aux, words[i], xpos[i])
            if (xpos[i] == 'MD') and (word in MODAL_VERB):
                word = CHANGE_MODAL_VERB[MODAL_VERB.index(word)]
            if words[i] in PERSONAL_PRONOUN:
                if (words[i] == 'I') and check_belong_to(clause_id, i, heads) and (words[nsubj_id] == 'he'):
                    word = 'he'
                elif (words[i] == 'me') and check_belong_to(clause_id, i, heads) and (words[nsubj_id] == 'he'):
                    word = 'him'
                elif (words[i] == 'myself') and check_belong_to(clause_id, i, heads) and (words[nsubj_id] == 'he'):
                    word = 'himself'
                elif (words[i] == 'you') and (labels[i] in ['dobj', 'iobj']):
                    word = 'them'
                else:
                    word = CHANGE_PERSONAL_PRONOUN[PERSONAL_PRONOUN.index(words[i])]
            if (words[i] in POSSESSIVE_PRONOUN) and (xpos[i] in ['PRP', 'PRP$']):
                if (words[i] == 'my') and (check_belong_to(clause_id, i, heads)) and (words[nsubj_id] == 'he'):
                    word = 'his'
                else:
                    word = CHANGE_POSSESSIVE_PRONOUN[POSSESSIVE_PRONOUN.index(words[i])]
            reported_clause += ' ' + word
    # concate to full reported speech sentence
    sentence = nsubj + ' ' + verb + ' that ' + reported_clause
    print(sentence)
    return sentence


