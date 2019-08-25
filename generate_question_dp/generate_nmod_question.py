from utils import *

def generate_nmod_question(words, xpos, heads, labels, ners):
    ###
    questions = []
    answers = []
    list_tags = []
    verb_labels = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    adj_labels = ['JJ', 'JJR', 'JJS']
    noun_labels = ['NN', 'NNP', 'NNS', 'NNPS']
    nsubj_labels = ['nsubj', 'nsubjpass']
    nmod_labels = ['nmod:in', 'nmod:on', 'nmod:at', 'nmod:before', 'nmod:after', 'nmod:near']
    """
        nmod:in -> location
    """
    for i in range(1, len(labels)):
        is_q = False
        for j in range(1, len(heads)):
            if ((heads[j] == i) or (heads[j] == heads[i])) and (words[j] in QWORDS):
                is_q = True
        if is_q:
            continue
        """
            process sentences have form: subject + verb + dobj + in/on + TIME/LOCATION
        """
        tags = []
        if (labels[i] in nmod_labels) and (xpos[heads[i]] in verb_labels) and (ners[i] in ['TIME', 'DATE', 'LOCATION', 'ORGANIZATION', 'COUNTRY']):
            verb_id = heads[i]
            entity_id = i
            ###=== get subject_id ===============================================================
            subj_id = -1
            for j in range(1, len(heads)):
                if (heads[j] == verb_id) and (labels[j] in nsubj_labels):
                    subj_id = j
            if (subj_id != -1):
                ###=== exist auxulary or not ========================================================
                aux = ''
                illegal_id = []
                for j in range(1, len(heads)):
                    if (heads[j] == verb_id) and (labels[j] in ['aux', 'auxpass']):
                        aux += ' ' + words[j]
                        illegal_id.append(j)
                aux = aux[1:]
                f_aux = aux.split(' ')[0]
                e_aux = ' '.join(aux.split(' ')[1:])
                ###=== get subject ==================================================================
                subj = ''
                for j in range(1, len(heads)):
                    if (check_belong_to(subj_id, j, heads)):
                        subj += ' ' + words[j]
                subj = subj[1:]
                ###=== get verb =====================================================================
                verb = ''
                for j in range(1, len(heads)):
                    if (heads[j] == verb_id) and (labels[j] not in ['compound', 'compound:prt', 'compound:svc']):
                        for k in range(1, len(heads)):
                            if (check_belong_to(j, k, heads)):
                                illegal_id.append(k)
                for j in range(1, len(heads)):
                    if (j not in illegal_id) and (check_belong_to(verb_id, j, heads)):
                        verb += ' ' + words[j]
                verb = verb[1:]
                ###=== get verb compound=====================================================================
                compound = ''
                for j in range(1, len(heads)):
                    if (heads[j] == verb_id) and (labels[j] in ['compound:prt', 'advmod']):
                        compound += ' ' + words[j]
                compound = compound[1:]
                ###=== get entity ===================================================================
                entity = ''
                for j in range(1, len(heads)):
                    if (j == entity_id):
                        entity += ' ' + words[j]
                    if (heads[j] == entity_id) and (labels[j] in ['compound', 'nummod']):
                        for k in range(1, len(heads)):
                            if (check_belong_to(j, k ,heads)):
                                entity += ' ' + words[k]
                entity = entity[1:]
                ###=== get direct object ===========================================================
                dobject = ''
                for j in range(1, len(heads)):
                    if (labels[j] == 'dobj') and (heads[j] == verb_id):
                        for k in range(1, len(heads)):
                            if (not check_belong_to(entity_id, k, heads)) and (check_belong_to(j, k, heads)):
                                dobject += ' ' + words[k]
                dobject = dobject[1:]
                ###=== generate question ===========================================================
                question = ''
                answer = ''
                if (ners[i] in ['LOCATION', 'ORGANIZATION', 'COUNTRY']):
                    if (len(aux) == 0):
                        if (xpos[verb_id] == 'VBZ'):
                            question = 'where does' + ' ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + compound + ' ' + dobject
                        if (xpos[verb_id] == 'VBP'):
                            question = 'where do' + ' ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + compound + ' ' + dobject
                        if (xpos[verb_id] == 'VBD'):
                            question = 'where did' + ' ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + compound + ' ' + dobject
                    else:
                        question = 'where ' + f_aux + ' ' + subj + ' ' + e_aux + ' ' + verb + ' ' + dobject
                    tags.append(ners[i])

                if (ners[i] in ['DATE', 'TIME']):
                    if (len(aux) == 0):
                        if (xpos[verb_id] == 'VBZ'):
                            question = 'when does' + ' ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + compound + ' ' + dobject
                        if (xpos[verb_id] == 'VBP'):
                            question = 'when do' + ' ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + compound + ' ' + dobject
                        if (xpos[verb_id] == 'VBD'):
                            question = 'when did' + ' ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + compound + ' ' + dobject
                    else:
                        question = 'when ' + f_aux + ' ' + subj + ' ' + e_aux + ' ' + verb + ' ' + dobject
                    tags.append(ners[i])
                answer = entity
                questions.append(question + '?')
                answers.append(answer)
                tags.append('nmod')
                list_tags.append(tags)
        """
            process sentences have form: subject + verb + xcomp/ccomp + in/on + TIME/LOCATION
        """  
        if (labels[i] in nmod_labels) and (labels[heads[i]] in ['xcomp', 'ccomp']) and (xpos[heads[heads[i]]] in verb_labels) and (ners[i] in ['TIME', 'DATE', 'LOCATION', 'ORGANIZATION', 'COUNTRY']):
            verb_id = heads[heads[i]]
            entity_id = i
            ###=== get subject_id ===============================================================
            subj_id = -1
            for j in range(1, len(heads)):
                if (heads[j] == verb_id) and (labels[j] in nsubj_labels):
                    subj_id = j
            if (subj_id != -1):
                ###=== exist auxulary or not ========================================================
                aux = ''
                illegal_id = []
                for j in range(1, len(heads)):
                    if (heads[j] == verb_id) and (labels[j] in ['aux', 'auxpass']):
                        aux += ' ' + words[j]
                        illegal_id.append(j)
                aux = aux[1:]
                f_aux = aux.split(' ')[0]
                e_aux = ' '.join(aux.split(' ')[1:])
                ###=== get subject ==================================================================
                subj = ''
                for j in range(1, len(heads)):
                    if (check_belong_to(subj_id, j, heads)):
                        subj += ' ' + words[j]
                subj = subj[1:]
                ###=== get verb =====================================================================
                verb = ''
                for j in range(1, len(heads)):
                    if (heads[j] == verb_id) and (labels[j] not in ['compound', 'compound:prt', 'compound:svc', 'aux', 'auxpass']):
                        for k in range(1, len(heads)):
                            if (check_belong_to(j, k, heads)):
                                illegal_id.append(k)
                for j in range(1, len(heads)):
                    if (j not in illegal_id) and (check_belong_to(verb_id, j, heads)):
                        verb += ' ' + words[j]
                verb = verb[1:]
                ###=== get verb compound=====================================================================
                compound = ''
                for j in range(1, len(heads)):
                    if (heads[j] == verb_id) and (labels[j] in ['compound:prt', 'advmod']):
                        compound += ' ' + words[j]
                compound = compound[1:]
                ###=== get entity ===================================================================
                illegal_id = []
                entity = ''
                for j in range(1, len(heads)):
                    if (j == entity_id):
                        entity += ' ' + words[j]
                        illegal_id.append(j)
                    if (heads[j] == entity_id) and (labels[j] in ['compound', 'nummod', 'det']):
                        for k in range(1, len(heads)):
                            if (check_belong_to(j, k ,heads)):
                                entity += ' ' + words[k]
                                illegal_id.append(k)
                entity = entity[1:]
                ###=== get direct object ===========================================================
                dobject = ''
                for j in range(1, len(heads)):
                    if (labels[j] == 'dobj') and (heads[j] == verb_id):
                        for k in range(1, len(heads)):
                            if (not check_belong_to(entity_id, k, heads)) and (check_belong_to(j, k, heads)):
                                dobject += ' ' + words[j]
                dobject = dobject[1:]
                ###=== get ccomp/xcomp part ========================================================
                extention = ''
                for j in range(1, len(heads)):
                    if (j not in illegal_id) and (not check_belong_to(entity_id, j, heads)) and (check_belong_to(heads[i], j, heads)):
                        extention += ' ' + words[j]
                ###=== generate question ===========================================================
                question = ''
                answer = ''
                if (ners[i] in ['LOCATION', 'ORGANIZATION', 'COUNTRY']):
                    if (len(aux) == 0):
                        if (xpos[verb_id] == 'VBZ'):
                            question = 'where does' + ' ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + compound + ' ' + dobject + ' ' + extention
                        if (xpos[verb_id] == 'VBP'):
                            question = 'where do' + ' ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + compound + ' ' + dobject + ' ' + extention
                        if (xpos[verb_id] == 'VBD'):
                            question = 'where did' + ' ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + compound + ' ' + dobject + ' ' + extention
                    else:
                        question = 'where ' + f_aux + ' ' + subj + ' ' + e_aux + ' ' + verb + ' ' + dobject + ' ' + extention
                    tags.append(ners[i])

                if (ners[i] in ['DATE', 'TIME']):
                    if (len(aux) == 0):
                        if (xpos[verb_id] == 'VBZ'):
                            question = 'when does' + ' ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + compound + ' ' + dobject + ' ' + extention
                        if (xpos[verb_id] == 'VBP'):
                            question = 'when do' + ' ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + compound + ' ' + dobject + ' ' + extention
                        if (xpos[verb_id] == 'VBD'):
                            question = 'when did' + ' ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) + ' ' + compound + ' ' + dobject + ' ' + extention
                    else:
                        question = 'when ' + f_aux + ' ' + subj + ' ' + e_aux + ' ' + verb + ' ' + dobject + ' ' + extention
                    tags.append(ners[i])
                answer = entity
                questions.append(question + '?')
                answers.append(answer)
                tags.append('nmod')
                list_tags.append(tags)
    return questions, answers, list_tags