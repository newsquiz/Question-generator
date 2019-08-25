"""
    ccomp: clausal complement
    Verb -- ccomp -- Verb : 68%
    Verb -- ccomp -- Adj  : 10%
    Verb -- ccomp -- Noun : 9%
    Eg: He says that you like to swim
    => question: what he say? = what + nsubj (subject of verb) + verb
    => answer  : you like swim = clausal complement
"""
from utils import *
import pdb
def generate_ccomp_xcomp_question(words, xpos, heads, labels, ners):
    ###
    questions = []
    answers = []
    list_tags = []
    verb_labels = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    adj_labels = ['JJ', 'JJR', 'JJS']
    noun_labels = ['NN', 'NNP', 'NNS', 'NNPS']
    nsubj_labels = ['nsubj', 'nsubjpass']

    ### find all ccomp relations
    for i in range(1, len(labels)):
        is_q = False
        for j in range(1, len(heads)):
            if ((heads[j] == i) or (heads[j] == heads[i])) and (words[j] in QWORDS):
                is_q = True
        if is_q:
            continue
        if (labels[i] in ['ccomp', 'xcomp']):
            head_id = heads[i]
            tail_id = i
            tags = []
            ### VERB ----ccomp----> VERB/ADJ/NOUN
            if ((xpos[head_id] in verb_labels) and (xpos[tail_id] in (verb_labels + adj_labels + noun_labels))):
                ### --Nsubject--> VERB --ccomp--> VERB
                # get nsubj of sentence
                nsubj = ''
                for j in range(1, len(labels)):
                    if ((heads[j] == head_id) and (labels[j] in nsubj_labels)):
                        nsubj = ''
                        illegal_id = []
                        if xpos[j] in ['NNP', 'NNPS']:
                            for k1 in range(1, len(heads)):
                                if (heads[k1] == j) and ((labels[k1] in ['appos', 'punct']) or ((len(labels[k1]) > 4) and (labels[k1][:4] == 'nmod'))):
                                    for k2 in range(1, len(heads)):
                                        if check_belong_to(k1, k2, heads):
                                            illegal_id.append(k2)
                        for k in range(1, len(labels)):
                            if (k not in illegal_id) and (check_belong_to(j, k, heads)):
                                nsubj += ' ' + words[k]
                        nsubj = nsubj[1:]
                # can not generate question without subject
                if (nsubj == ''):
                    continue
                # get object of sentence
                dobj = ''
                for j in range(1, len(heads)):
                    if (heads[j] == head_id) and (labels[j] in ['dobj', 'iobj']):
                        dobj = ''
                        for k in range(1, len(labels)):
                            if (check_belong_to(j, k, heads)):
                                dobj += ' ' + words[k]
                dobj = dobj[1:]
                # get auxiliary of verb
                aux = ''
                for j in range(1, len(heads)):
                    if (heads[j] == head_id) and (labels[j] in ['aux', 'auxpass']):
                        aux = ''
                        for k in range(1, len(labels)):
                            if (check_belong_to(j, k, heads)):
                                aux += ' ' + words[k]
                aux = aux[1:]
                f_aux = aux.split(' ')[0]
                e_aux = ' '.join(aux.split(' ')[1:])
                # get compound of verb
                compound = ''
                for j in range(1, len(heads)):
                    if (heads[j] == head_id) and (labels[j] in ['compound:prt']):
                        compound += ' ' + words[j]
                compound = compound[1:] 
                # get nmod of verb
                nmod = ''
                for j in range(1, len(heads)):
                    if (heads[j] == head_id) and (len(labels[j]) >= 4) and (labels[j][:4] == 'nmod'):
                        for k in range(1, len(labels)):
                            if (check_belong_to(j, k, heads)):
                                nmod += ' ' + words[k]
                nmod = nmod[1:]
                # get all clausal complement except first 'mark' relation
                verb_clausal = ''
                illegal_id = []
                has_todo = False
                for j in range(1, len(labels)):
                    if ((heads[j] == i) and (labels[j] in ['mark'])):
                        if words[j] == 'to':
                            has_todo = True
                        for k in range(1, len(labels)):
                            if (check_belong_to(j, k, heads)):
                                illegal_id.append(k)
                        break

                for j in range(1, len(labels)):
                    if ((j not in illegal_id) and (check_belong_to(i, j, heads))):
                        verb_clausal += ' ' + words[j]
                verb_clausal = verb_clausal[1:]
                # generate question + process verb form
                question = ''
                if aux == '':
                    if xpos[head_id] == 'VBD':
                        question = 'what did ' + nsubj + ' ' + get_morphy(words[head_id], 'VBD')
                    elif (xpos[head_id] == 'VBZ') and (wn.morphy(words[head_id], 'v') != 'be'):
                        question = 'what does ' + nsubj + ' ' + get_morphy(words[head_id], 'VBZ')
                    elif (xpos[head_id] == 'VBP') and (wn.morphy(words[head_id], 'v') == 'be'):
                        question = 'what do ' + nsubj + ' ' + words[head_id]
                    else:
                        question = 'what ' + nsubj + ' ' + words[head_id]
                else:
                    question = 'what ' + f_aux + ' ' + nsubj + ' ' + e_aux + ' ' + words[head_id] + ' ' + compound
                if dobj != '':
                    question += ' ' + dobj
                if has_todo:
                    question += ' to do'
                if (nmod != '') and (compound == ''):
                    question += ' ' + nmod
                answer = verb_clausal
                if question == '':
                    continue
                # append
                questions.append(question + '?')
                answers.append(answer)
                tags.append('ccomp/xcomp')
                list_tags.append(tags)
            break
    ### return
    return questions, answers, list_tags