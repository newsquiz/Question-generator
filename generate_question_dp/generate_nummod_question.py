"""
    nummod : numeric modifier of a noun
    64% Noun  -- nummod -- Num
    17% PropN -- nummod -- Num
    10% Sym   -- nummod -- Num
"""
from utils import *

def generate_nummod_question(words, xpos, heads, labels, ners):
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
        """
        =========================================================================================
        ==== process sentences have form: subject(CD --nummod-- noun) + verb + ...===============
        =========================================================================================
        """
        tags = []
        if (labels[i] == 'nummod') and (labels[heads[i]] in nsubj_labels) and (xpos[heads[heads[i]]] in verb_labels) and (ners[i] == 'NUMBER'):
            nummod_id = i
            subj_id = heads[i]
            verb_id = heads[heads[i]]
            ###=== get nummod ===================================================================
            nummod = ''
            for j in range(len(labels)):
                if check_belong_to(nummod_id, j, heads):
                    nummod += ' ' + words[j]
            nummod = nummod[1:]
            ###=== get subject and its compound =================================================
            ###=== if compound + nummod + nsubject => noun phrase not number modifier ===========
            is_phrase = False
            noun = ''
            for j in range(1, len(heads)):
                if (j == subj_id):
                    noun += ' ' + words[j]
                if (heads[j] == subj_id) and (labels[j] in ['compound', 'amod', 'det', 'nmod:of', 'nmod:per']):
                    if (labels[j] in ['compound', 'det']) and (j < i) and (i < subj_id):
                        is_phrase = True
                    for k in range(1, len(heads)):
                        if check_belong_to(j, k, heads):
                            noun += ' ' + words[k]
            noun = noun[1:]
            if is_phrase:
                continue
            ###=== generate question ============================================================
            question_body = ''
            for j in range(1, len(heads)):
                if (j == heads[subj_id]):
                    question_body += ' ' + words[j]
                if (not check_belong_to(subj_id, j, heads)) and (heads[j] == heads[subj_id]) and (labels[j] not in ['mark']):
                    for k in range(1, len(heads)):
                        if check_belong_to(j, k, heads):
                            if (words[j] == 'am'):
                                question_body += ' is'
                            else:
                                question_body += ' ' + words[k]
            if (question_body == ''):
                continue
            question = 'How many ' + noun + ' ' + question_body
            ###=== append =======================================================================
            questions.append(question + '?')
            answers.append(nummod)
            tags.append('nummod')
            list_tags.append(tags)

        """
        =========================================================================================
        === process sentences have form: subject + verb + direct_object(CD -- nummod -- noun) ===
        =========================================================================================
        """
        if (labels[i] == 'nummod') and (labels[heads[i]] == 'dobj') and (xpos[heads[heads[i]]] in verb_labels) and (ners[i] == 'NUMBER'):
            obj_id = heads[i]
            nummod_id = i
            verb_id = heads[obj_id]
            ###=== check if exist nsubj point to head ==========================================
            nsubj_id = -1
            for j in range(1, len(labels)):
                if (check_belong_to(verb_id, j, heads) and (labels[j] in nsubj_labels)):
                    nsubj_id = j
                    break
            if (nsubj_id == -1):
                continue
            ###=== get dobj info ================================================================
            is_human, type_noun = get_noun_info(words[obj_id], xpos[obj_id])
            if (ners[obj_id] == 'PERSON'):
                is_human = True
            for j in range(1, len(heads)):
                if (heads[j] == obj_id) and (labels[j] in ['conj']):
                    noun_type = 1       
            ###=== get body of question: the whole part belong to head except dobj ==============
            ###=== get nsubject =================================================================
            nsubj = ''
            for j in range(1, len(heads)):
                if (check_belong_to(nsubj_id, j, heads)):
                    nsubj += ' ' + words[j]
            nsubj = nsubj[1:]
            ###=== get object and its compound =================================================
            ###=== if compound + nummod + object => noun phrase not number modifier ============
            is_phrase = False
            noun = ''
            for j in range(1, len(heads)):
                if (j == obj_id):
                    noun += ' ' + words[j]
                if (heads[j] == obj_id) and (labels[j] in ['compound', 'amod', 'det', 'nmod:of', 'nmod:per']):
                    if (labels[j] in ['compound', 'det']) and (j < i) and (i < obj_id):
                        is_phrase = True
                    for k in range(1, len(heads)):
                        if check_belong_to(j, k, heads):
                            noun += ' ' + words[k]
            noun = noun[1:]
            if is_phrase:
                continue
            ###=== get nummod ===================================================================
            nummod = ''
            for j in range(len(heads)):
                if (check_belong_to(nummod_id, j, heads)):
                    nummod += ' ' + words[j]
            nummod = nummod[1:]
            ###=== get aux ======================================================================
            aux = ''
            for j in range(1, len(heads)):
                if (check_belong_to(verb_id, j, heads) and (labels[j] in ['aux', 'auxpass'])):
                    aux += ' ' + words[j]
            aux = aux[1:]
            f_aux = aux.split(' ')[0]
            e_aux = ' '.join(aux.split(' ')[1:])
            ###=== get verb =====================================================================
            verb = ''
            for j in range(1, len(heads)):
                if (j == verb_id) or ((heads[j] == verb_id) and (labels[j] not in ['aux', 'auxpass'])):
                    verb += ' ' + words[j]
            verb = verb[1:]
            ###=== get extension ================================================================
            extension = ''
            for j in range(verb_id, len(heads)):
                if (heads[j] == verb_id) and (((len(labels[j]) >= 5) and (labels[j][:5] == 'advcl')) or ((len(labels[j]) >= 4) and (labels[j][:4] == 'nmod')) or (labels[j] in ['acl'])):
                    for k in range(verb_id, len(heads)):
                        if (check_belong_to(j, k, heads)):
                            extension += ' ' + words[k]
            extension = extension[1:]
            ###=== generate question ============================================================
            if (len(aux) != 0):
                question = 'How many ' + noun + ' ' + f_aux + ' ' + nsubj + ' ' + e_aux + ' ' + verb + ' ' + extension
            else:
                question = 'How many ' + noun + ' ' + nsubj + ' ' + verb + ' ' + extension
            if (xpos[verb_id] == 'VBZ'):
                question = 'How many ' + noun + ' does ' + nsubj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + extension
            if (xpos[verb_id] == 'VBP'):
                question = 'How many ' + noun + ' do ' + nsubj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + extension
            if (xpos[verb_id] == 'VBD') and (len(aux) == 0):
                question = 'How many ' + noun + ' did ' + nsubj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + extension
            answer = nummod
            ###=== append =======================================================================
            questions.append(question + '?')
            answers.append(answer)
            tags.append('nummod')
            list_tags.append(tags)

        """
        =========================================================================================
        === process sentences have form: (CD --nummod-- noun) + (be --cop-- noun) ===============
        =========================================================================================
        """
        if (labels[i] == 'nummod') and (labels[heads[i]] in nsubj_labels) and (xpos[heads[heads[i]]] in noun_labels) and (ners[i] == 'NUMBER'):
            nummod_id = i
            subj_id = heads[i]
            obj_id = heads[subj_id]
            ###=== check whether exist cop relation =============================================
            cop_id = -1
            for j in range(1, len(heads)):
                if (heads[j] == obj_id) and (labels[j] == 'cop'):
                    cop_id = j
            if (cop_id == -1):
                continue
            ###=== get nummod ===================================================================
            nummod = ''
            for j in range(1, len(heads)):
                if (check_belong_to(nummod_id, j, heads)):
                    nummod += ' ' + words[j]
            nummod = nummod[1:]
            ###=== get subject ==================================================================
            ###=== if compound + nummod + nsubject => noun phrase not number modifier ===========
            is_phrase = False
            subject = ''
            for j in range(1, len(heads)):
                if (heads[j] == subj_id) and (labels[j] in ['compound', 'amod', 'det']):
                    if (labels[j] in ['compound', 'det']) and (j < i) and (i < subj_id):
                        is_phrase = True
                    subject += ' ' + words[j]
            subject = subject[1:]
            if is_phrase:
                continue
            ###=== get tobe =====================================================================
            tobe = ''
            for j in range(1, len(heads)):
                if (heads[j] == obj_id) and (labels[j] in ['cop', 'aux', 'auxpass']):
                    tobe += ' ' + words[j]
            tobe = tobe[1:]
            ###=== get dobject ==================================================================
            dobject = ''
            for j in range(1, len(heads)):
                if (j == obj_id):
                    dobject += ' ' + words[j]
                if ((heads[j] == obj_id) and (labels[j] in ['compound', 'amod', 'nummod'])):
                    for k in range(1, len(heads)):
                        if (check_belong_to(j, k, heads)):
                            dobject += ' ' + words[k]
            dobject = dobject[1:]
            ###=== generate question ============================================================
            question = 'how many ' + subject + ' ' + tobe + ' ' + dobject
            answer = nummod
            ###=== append =======================================================================
            questions.append(question + '?')
            answers.append(answer)
            tags.append('nummod')
            list_tags.append(tags)
        """
        =========================================================================================
        === process sentences have form: subject + (be --cop-- (CD --nummod-- noun)) ============
        =========================================================================================
        """
        if (labels[i] == 'nummod') and (labels[heads[i]] == 'root') and (ners[i] == 'NUMBER'):
            nummod_id = i
            obj_id = heads[i]
            ###=== get subject id ===============================================================
            subj_id = -1
            for j in range(1, len(heads)):
                if (heads[j] == obj_id) and (labels[j] in nsubj_labels):
                    subj_id = j
            if (subj_id == -1):
                continue
            ###=== get subject ==================================================================
            subject = ''
            for j in range(1, len(heads)):
                if (check_belong_to(subj_id, j, heads)):
                    subject += ' ' + words[j]
            subject = subject[1:]
            ###=== get tobe =====================================================================
            tobe = ''
            for j in range(1, len(heads)):
                if (heads[j] == obj_id) and (labels[j] in ['cop', 'aux', 'auxpass']):
                    tobe += ' ' + words[j]
            tobe = tobe[1:]
            ###=== get dobject ==================================================================
            ###=== if compound + nummod + object => noun phrase not number modifier =============
            is_phrase = False
            dobject = ''
            for j in range(1, len(heads)):
                if (j == obj_id):
                    dobject += ' ' + words[j]
                if ((heads[j] == obj_id) and (labels[j] in ['compound', 'det'])):
                    if (labels[j] in ['compound', 'det']) and (j < i) and (j < obj_id):
                        is_phrase = True
                    for k in range(1, len(heads)):
                        if (check_belong_to(j, k, heads)):
                            dobject += ' ' + words[k]
            dobject = dobject[1:]
            if is_phrase:
                continue
            ###=== get nummod ===================================================================
            nummod = ''
            for j in range(1, len(heads)):
                if (check_belong_to(nummod_id, j, heads)):
                    nummod += ' ' + words[j]
            nummod = nummod[1:]
            ###=== generate question ============================================================
            question = 'how many ' + dobject + ' ' + tobe + ' ' + subject
            answer = nummod
            ###=== append =======================================================================
            questions.append(question + '?')
            answers.append(answer)
            tags.append('nummod')
            list_tags.append(tags)
        """
        =========================================================================================
        === process sentences have form: ... + (verb --nmod:tmod-- (CD --nummod-- noun))=========
        =========================================================================================
        """
        if (labels[i] == 'nummod') and (labels[heads[i]] in ['nmod:tmod']) and (xpos[heads[heads[i]]] in verb_labels) and (ners[i] == 'NUMBER'):
            nummod_id = i
            verb_id = heads[heads[i]]
            illegal_id = []
            ###=== get nsubj of sentence ========================================================
            nsubj = ''
            for j in range(1, len(labels)):
                if ((heads[j] == verb_id) and (labels[j] in nsubj_labels)):
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
            ###=== get nummod ===================================================================
            nummod = ''
            for j in range(1, len(heads)):
                if (check_belong_to(nummod_id, j, heads)):
                    nummod += ' ' + words[j]
                    illegal_id.append(j)
            nummod = nummod[1:]
            ###=== get noun and its compound ====================================================
            is_phrase = False
            noun = ''
            for j in range(1, len(heads)):
                if (j == heads[i]) or ((heads[j] == heads[i]) and (labels[j] == 'compound', 'det')):
                    if (labels[j] in ['compound', 'det']) and (j < i) and (i < subj_id):
                        is_phrase = True
                    noun += ' ' + words[j]
                    illegal_id.append(j)
            noun = noun[1:]
            if is_phrase:
                continue
            ###=== get auxiliary of verb ========================================================
            aux = ''
            for j in range(1, len(heads)):
                if (heads[j] == verb_id) and (labels[j] == 'aux'):
                    aux = ''
                    for k in range(1, len(labels)):
                        if (check_belong_to(j, k, heads)):
                            aux += ' ' + words[k]
            aux = aux[1:]
            ###=== get predicate ================================================================
            predicate = ''
            for j in range(1, len(heads)):
                if (heads[j] == verb_id) and (labels[j] not in ['punct', 'aux', 'nsubj', 'nsubjpass']) and not ((len(labels[j]) >= 4) and (labels[j][:4] == 'nmod')):
                    for k in range(1, len(heads)):
                        if check_belong_to(j, k, heads):
                            predicate += ' ' + words[k]
            predicate = predicate[1:]
            ###=== generate question ============================================================
            question = ''
            if aux == '':
                if (xpos[verb_id] == 'VBZ'):
                    question = 'how many ' + noun + ' does '
                if (xpos[verb_id] == 'VBP'):
                    question = 'how many ' + noun + ' do '
                if (xpos[verb_id] == 'VBD'):
                    question = 'how many ' + noun + ' did '
                if (xpos[verb_id] == 'VBN'):
                    question = 'how many ' + noun + ' have '
            elif len(aux.split(' ')) == 1:
                question = 'how many ' + noun + ' ' + aux + ' '
            if (question != '') and (nsubj != ''):
                question += nsubj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + predicate
            else:
                question += get_morphy(words[verb_id], xpos[verb_id]) + ' ' + predicate
            answer = nummod
            ###=== append =======================================================================
            if question == '':
                continue
            questions.append(question + '?')
            answers.append(answer)
            tags.append('nummod')
            list_tags.append(tags)

    ### return
    return questions, answers, list_tags