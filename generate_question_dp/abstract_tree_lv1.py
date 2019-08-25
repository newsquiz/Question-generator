from utils import *

# root is verb trees
"""
index: 1
Eg: In 1947-48, Torino scored 125 goals in their 40 matches, finishing with a record goal difference of +92 on their way their fourth title in as many seasons

          root verb
         /        \      
      (subj)    (dobj)        
       /            \
     noun             noun
                   /       \
                (nummod) (nmod:in)
                 /            \
          CD-tag NUMBER         noun           
"""
def verb_tree_1(words, xpos, heads, labels, ners):
    # check if satify condition
    root_id = get_root_id(heads)
    if xpos[root_id] in verb_labels:
        verb_id = root_id
    else:
        return None

    subj_id = -1
    for i in range(1, verb_id):
        if (heads[i] == verb_id) and (xpos[i] in noun_labels) and (xpos[i] != 'PRP'):
            if subj_id == -1:
                subj_id = i
            else:
                subj_id = -1
    if subj_id == -1:
        return

    obj_id = -1
    for i in range(verb_id, len(heads)):
        if (heads[i] == verb_id) and (labels[i] == 'dobj') and (xpos[i] in noun_labels):
            has_nummod = False
            for j in range(verb_id, i):
                if (heads[j] == i) and (labels[j] == 'nummod') and (xpos[j] == 'CD') and (ners[j] == 'NUMBER'):
                    has_nummod = True
                    nummod_id = j
            has_nmodin = False
            for j in range(i, len(heads)):
                if (heads[j] == i) and (labels[j] == 'nmod:in') and (xpos[j] in noun_labels):
                    has_nmodin = True
                    nmodin_id = j
            if has_nmodin and has_nummod and (obj_id == -1):
                obj_id = i
            else:
                obj_id = -1
    if obj_id == -1:
        return None
    # generate question   
    ###=== get subject =================================================================
    subj = ''
    for j in range(1, len(heads)):
        if (check_belong_to(subj_id, j, heads)):
            subj += ' ' + words[j]
    subj = subj[1:]
    ###=== get object and its compound =================================================
    ###=== if compound + nummod + object => noun phrase not number modifier ============
    is_phrase = False
    noun = ''
    for j in range(1, len(heads)):
        if (j == obj_id):
            noun += ' ' + words[j]
        if ((heads[j] == obj_id) and (labels[j] in ['compound', 'amod', 'det',])) or (j == nmodin_id):
            if (labels[j] in ['compound', 'det']) and (j < i) and (i < obj_id):
                is_phrase = True
            for k in range(1, len(heads)):
                if check_belong_to(j, k, heads):
                    noun += ' ' + words[k]
    noun = noun[1:]
    if is_phrase:
        return None
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
    ###=== generate question ============================================================
    if (len(aux) != 0):
        question = 'How many ' + noun + ' ' + f_aux + ' ' + subj + ' ' + e_aux + ' ' + verb 
    else:
        question = 'How many ' + noun + ' ' + subj + ' ' + verb 
    if (xpos[verb_id] == 'VBZ'):
        question = 'How many ' + noun + ' does ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) 
    if (xpos[verb_id] == 'VBP'):
        question = 'How many ' + noun + ' do ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) 
    if (xpos[verb_id] == 'VBD') and (len(aux) == 0):
        question = 'How many ' + noun + ' did ' + subj + ' ' + get_morphy(words[verb_id], xpos[verb_id]) 
    answer = nummod
    ###=== append =======================================================================
    question = question + '?'
    tags = ['nummod']
    return question, answer, tags


def get_question_abstract_tree_lv1(words, xpos, heads, labels, ners):
    questions = []
    answers = []
    list_tags = []
    # root is verb tag
    verb_tree_1_res = verb_tree_1(words, xpos, heads, labels, ners)
    if verb_tree_1_res != None:
        question, answer, tags = verb_tree_1_res
        questions.append(question)
        answers.append(answer)
        list_tags.append(tags)
    return questions, answers, list_tags