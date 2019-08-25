"""
    dobj: direct object
    70%: VERB -- dobj -- NOUN
    Eg: She gave me a raise
    question: what she gave me? = what + clausal (all words belong to Verb except dobj part which will be answer)
    answer  : a raise = all words belong to NOUN

    error: 1 câu hoặc 1 mệnh đề có thể có nhiều dobj
"""
from utils import *

def generate_obj_question(words, xpos, heads, labels, ners):
    ###
    questions = []
    answers = []
    list_tags = []
    verb_labels = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    adj_labels = ['JJ', 'JJR', 'JJS']
    noun_labels = ['NN', 'NNP', 'NNS', 'NNPS', 'PRP']
    nsubj_labels = ['nsubj', 'nsubjpass']
    ### find all dobj relations
    for i in range(1, len(labels)):
        is_q = False
        for j in range(1, len(heads)):
            if ((heads[j] == i) or (heads[j] == heads[i])) and (words[j] in QWORDS):
                is_q = True
        if is_q:
            continue
            
        if (labels[i] == 'dobj'):
            head_id = heads[i]
            tail_id = i
            tags = []
            ### VERB ----dobj----> NOUN
            if ((xpos[head_id] in verb_labels) and (xpos[tail_id] in noun_labels)) and (xpos[tail_id] not in ['PRP']):
                # get nsubj of sentence
                nsubj = ''
                is_prp = False
                for j in range(1, len(labels)):
                    if ((heads[j] == head_id) and (labels[j] in nsubj_labels)):
                        nsubj = ''
                        illegal_id = []
                        if (xpos[j] == 'PRP'):
                            is_prp = True
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
                if (nsubj == '') or (is_prp):
                    continue

                # get dobj
                dobj = ''
                illegal_id = []
                for j in range(1, len(labels)):
                    if (check_belong_to(i, j, heads)):
                        dobj += ' ' + words[j]
                        illegal_id.append(j)
                dobj = dobj[1:]

                # get dobj info
                is_human, type_noun = get_noun_info(words[tail_id], xpos[tail_id])
                if (ners[tail_id] == 'PERSON'):
                    is_human = True
                for j in range(1, len(heads)):
                    if (heads[j] == tail_id) and (labels[j] in ['conj']):
                        noun_type = 1
                # get compound
                compound = ''
                for j in range(1, len(heads)):
                    if (heads[j] == head_id) and (labels[j] in ['compound:prt']):
                        compound += ' ' + words[j]
                compound = compound[1:] 
                # get body of question: the whole part belong to head except dobj will be the 
                # get aux
                aux = ''
                for j in range(1, len(heads)):
                    if (check_belong_to(head_id, j, heads) and (labels[j] in ['aux', 'auxpass'])):
                        aux += ' ' + words[j]
                f_aux = aux.split(' ')[0]
                e_aux = ' '.join(aux.split(' ')[1:])
                # get extension
                extension = ''
                for j in range(head_id, len(heads)):
                    if (heads[j] == head_id) and ((labels[j] in ['advmod']) or ((len(labels[j]) >= 4) and (labels[j][:4] == 'nmod'))):
                        for k in range(head_id, len(heads)):
                            if (check_belong_to(j, k, heads)):
                                extension += ' ' + words[k]
                extension = extension[1:]

                # generate question
                if (is_human):
                    if (len(aux) != 0):
                        question = 'who ' + f_aux + ' ' + nsubj + ' ' + e_aux + ' ' + words[head_id] + ' ' + compound + ' ' + extension
                    else:
                        question = 'who ' + nsubj + ' ' + words[head_id] + ' ' + compound + ' ' + extension
                    if (xpos[head_id] == 'VBZ'):
                        question = 'who does ' + nsubj + ' ' + get_morphy(words[head_id], 'VBZ') + ' ' + compound + ' ' + extension
                    if (xpos[head_id] == 'VBP'):
                        question = 'who do ' + nsubj + ' ' + get_morphy(words[head_id], 'VBP') + ' ' + compound + ' ' + extension
                    if (xpos[head_id] == 'VBD') and (len(aux) == 0):
                        question = 'who did ' + nsubj + ' ' + get_morphy(words[head_id], 'VBD') + ' ' + compound + ' ' + extension
                else:
                    if (ners[tail_id] == 'MONEY'):
                        if (len(aux) != 0):
                            question = 'How much ' + f_aux + ' ' + nsubj + ' ' + e_aux + ' ' + words[head_id] + ' ' + compound + ' ' + extension
                        else:
                            question = 'How much ' + nsubj + ' ' + words[head_id] + ' ' + compound + ' ' + extension
                        if (xpos[head_id] == 'VBZ'):
                            question = 'How much does ' + nsubj + ' ' + get_morphy(words[head_id], 'VBZ') + ' ' + compound + ' ' + compound + ' ' + extension
                        if (xpos[head_id] == 'VBP'):
                            question = 'How much do ' + nsubj + ' ' + get_morphy(words[head_id], 'VBP') + ' ' + compound + ' ' + extension
                        if (xpos[head_id] == 'VBD') and (len(aux) == 0):
                            question = 'How much did ' + nsubj + ' ' + get_morphy(words[head_id], 'VBD') + ' ' + compound + ' ' + extension
                    else:
                        if (len(aux) != 0):
                            question = 'what ' + f_aux + ' ' + nsubj + ' ' + e_aux + ' ' + words[head_id] + ' ' + compound + ' ' + extension
                        else:
                            question = 'what ' + nsubj + ' ' + words[head_id] + ' ' + compound + ' ' + extension
                        if (xpos[head_id] == 'VBZ'):
                            question = 'what does ' + nsubj + ' ' + get_morphy(words[head_id], 'VBZ') + ' ' + compound + ' ' + extension
                        if (xpos[head_id] == 'VBP'):
                            question = 'what do ' + nsubj + ' ' + get_morphy(words[head_id], 'VBP') + ' ' + compound + ' ' + extension
                        if (xpos[head_id] == 'VBD') and (len(aux) == 0):
                            question = 'what did ' + nsubj + ' ' + get_morphy(words[head_id], 'VBD') + ' ' + compound + ' ' + extension
                answer = dobj
                # append
                questions.append(question + '?')
                answers.append(answer)
                tags.append('dobj')
                list_tags.append(tags)
    ### return
    return questions, answers, list_tags