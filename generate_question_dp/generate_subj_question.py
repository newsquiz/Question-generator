"""
    if sentence in basic form: subject + verb + object -> form = 1 -> short question
    if sentence in ccomp form: subject + verb + clouse -> form = 2 -> long question
    if sentence in cop form  : subject + cop + noun/adj-> form = 3 
    ignore questions which answer's tag in 'PRP'
"""
from utils import *
import pdb

def generate_subj_question(words, xpos, heads, labels, ners):
    questions = []
    answers = []
    list_tags = []
    min_qb_length = 5
    verb_labels = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    adj_labels = ['JJ', 'JJR', 'JJS']
    noun_labels = ['NN', 'NNP', 'NNS', 'NNPS', 'PRP']
    # find all word with nsubj label
    nsubj_labels = ['nsubj', 'nsubjpass']
    for i in range(1, len(labels)):
        is_q = False
        for j in range(1, len(heads)):
            if ((heads[j] == i) or (heads[j] == heads[i])) and (words[j] in QWORDS):
                is_q = True
        if is_q:
            continue
            
        if (labels[i] in nsubj_labels) and (xpos[i] not in ['PRP']) and (xpos[heads[i]] in verb_labels):
            tags = []
            is_human = False
            is_organization = False
            ### get all words belong to subject
            illegal_id = []
            for j in range(1, len(heads)):
                if ((labels[j] in ['ref', 'case', 'punct', 'appos', 'acl:relcl']) and (heads[j] == i)):
                    for k in range(1, len(heads)):
                        if (check_belong_to(j, k, heads)):
                            illegal_id.append(k)
            answer = ''
            for j in range(1, len(heads)):
                if (check_belong_to(i, j, heads)):
                    if (j not in illegal_id):
                        answer += ' ' + words[j]
                    last_answer_id = j
            answer = answer[1:]
            # check noun info
            is_human, _ = get_noun_info(words[i], xpos[i])
            if (ners[i] == 'PERSON'):
                is_human = True
            if (ners[i] == 'ORGANIZATION'):
                is_organization = True
        
            ### get all words belong to predicate
            # get form of sentence
            form = 0
            for j in range(1, len(heads)):
                if (heads[j] == heads[i]):
                    if (labels[j] == 'dobj'):
                        form = 1
                    if (labels[j] in ['ccomp', 'xcomp']) or ((len(labels[j]) >= 5) and (labels[j][:5] == 'advcl')):
                        form = 2
            # get question in form 1
            question_body = ''
            if form == 1:
                illegal_id = []
                for j in range(last_answer_id + 1, len(heads)):
                    if (heads[j] == heads[i]) and not (labels[j] in ['dobj', 'aux', 'auxpass', 'cop', 'advmod', 'ref', 'compound', 'compound:prt', 'neg']):
                        for k in range(1, len(heads)):
                            if check_belong_to(j, k, heads):
                                illegal_id.append(k)
                for j in range(last_answer_id + 1, len(heads)):
                    if (j not in illegal_id) and (check_belong_to(heads[i], j, heads)):
                        if (words[j] == 'am'):
                            question_body += ' is'
                        else:
                            question_body += ' ' + words[j]
            # change to form 2 if length question too short
            if (form == 1) and (len(question_body.split(" ")) < min_qb_length):
                question_body = ""
                form = 2
            # get question in form 2
            if form == 2:
                illegal_id = []
                for j in range(last_answer_id + 1, len(heads)):
                    if words[j] == ".":
                        illegal_id.append(j)
                for j in range(last_answer_id + 1, len(heads)):
                    if (j not in illegal_id) and (check_belong_to(heads[i], j, heads)):
                        if (words[j] == 'am'):
                            question_body += ' is'
                        else:
                            question_body += ' ' + words[j]
            if (question_body == ''):
                continue
            if is_human:
                question = 'who' + question_body
                tags.append('PERSON')
            elif is_organization:
                question = 'which organization' + question_body
                tags.append('ORGANIZATION')
            else:
                question = 'what' + question_body

            # append
            questions.append(question + '?')
            answers.append(answer)
            tags.append('subj')
            list_tags.append(tags)
            
        if (labels[i] in nsubj_labels) and (xpos[i] not in ['PRP']) and (xpos[heads[i]] in adj_labels + noun_labels):
            tags = []
            is_human = False
            is_organization = False
            # check if in cop form
            has_cop = False
            for j in range(1, len(heads)):
                if (heads[j] == heads[i]) and (labels[j] == 'cop'):
                    has_cop = True
            if not has_cop:
                continue
            ### get all words belong to subject
            illegal_id = []
            for j in range(1, len(heads)):
                if ((labels[j] in ['ref', 'case', 'punct', 'appos', 'acl:relcl']) and (heads[j] == i)):
                    for k in range(1, len(heads)):
                        if (check_belong_to(j, k, heads)):
                            illegal_id.append(k)
            answer = ''
            for j in range(1, len(heads)):
                if (check_belong_to(i, j, heads)):
                    if (j not in illegal_id):
                        answer += ' ' + words[j]
                    last_answer_id = j
            answer = answer[1:]
            # check noun info
            is_human, _ = get_noun_info(words[i], xpos[i])
            if (ners[i] == 'PERSON'):
                is_human = True
            if (ners[i] == 'ORGANIZATION'):
                is_organization = True
            # get question body
            question_body = ""
            for j in range(1, len(heads)):
                if (j == heads[i]):
                    question_body += ' ' + words[j]
                if (heads[j] == heads[i]) and ((labels[j] in ['cop', 'det', 'advmod', 'aux', 'auxpass', 'neg', 'case', 'amod', 'xcomp', 'ccomp']) or ((len(labels[j]) >= 4) and (labels[j][:4] == 'nmod'))):
                    for k in range(1, len(heads)):
                        if (check_belong_to(j, k, heads)):
                            if (words[k] == 'am'):
                                question_body += ' is'
                            else:
                                question_body += ' ' + words[k]
            if (question_body == ''):
                continue
            if is_human:
                question = 'who' + question_body
                tags.append('PERSON')
            elif is_organization:
                question = 'which organization' + question_body
                tags.append('ORGANIZATION')
            else:
                question = 'what' + question_body
            # append
            questions.append(question + '?')
            answers.append(answer)
            tags.append('subj')
            list_tags.append(tags)
    return questions, answers, list_tags