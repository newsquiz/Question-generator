"""
    nmod:tmod : A temporal modifier is a subtype of the nmod relation: if the modifier is specifying
     a time, it is labeled as tmod.
    Eg: last night, I swam in the pool
    question: when I swam in the pool?
    answer  : last night
"""
from utils import *

def generate_tmod_question(words, xpos, heads, labels, ners):
    questions = []
    answers = []
    list_tags = []

    ### find tmod relation
    for i in range(1, len(labels)):
        is_q = False
        for j in range(1, len(heads)):
            if ((heads[j] == i) or (heads[j] == heads[i])) and (words[j] in QWORDS):
                is_q = True
        if is_q:
            continue
            
        tags = []
        if (labels[i] in ['tmod', 'nmod:tmod', 'nmod:since']):
            head_id = heads[i]
            tail_id = i

            ### find tmod phrase (all words belong to tail-word)
            illegal_id = [] 
            tmod_phrase = ''
            for j in range(1, len(heads)):
                if (check_belong_to(tail_id, j, heads)):
                    tmod_phrase += ' ' + words[j]
                    illegal_id.append(j)
            tmod_phrase = tmod_phrase[1:]

            ### find body of question
            body_question = ''
            for j in range(1, len(heads)):
                if ((j not in illegal_id) and check_belong_to(head_id, j, heads)):
                    body_question += ' ' + words[j]
            body_question = body_question[1:]

            ### generate question
            question = 'when ' + body_question
            answer = tmod_phrase

            ### append
            questions.append(question)
            answers.append(answer)
            tags.append('tmod')
            list_tags.append(tags)

    return questions, answers, list_tags