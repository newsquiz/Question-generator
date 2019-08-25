import json
import random
import numpy as np 
from nltk.corpus import wordnet as wn

QWORDS = ['what', 'when', 'where', 'who', 'why', 'which', 'whom', 'how']

verb_labels = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
adj_labels = ['JJ', 'JJR', 'JJS']
noun_labels = ['NN', 'NNP', 'NNS', 'NNPS']
nsubj_labels = ['nsubj', 'nsubjpass']

verb_dictionary = {}
verb_dictionary['verb_base_form'] = []
verb_dictionary['verb_3rd_present'] = []
verb_dictionary['verb_gerund'] = []
verb_dictionary['verb_past_tense'] = []
verb_dictionary['verb_past_participle'] = []

with open('data/verb.tsv', 'r') as f:
    for row in f:
        row_split = row[:-1].split('\t')
        verb_dictionary['verb_base_form'].append(row_split[0])
        verb_dictionary['verb_3rd_present'].append(row_split[1])
        verb_dictionary['verb_gerund'].append(row_split[2])
        verb_dictionary['verb_past_tense'].append(row_split[3])
        verb_dictionary['verb_past_participle'].append(row_split[4])

with open('data/phrasal_verb.json', 'r') as f:
    PV_DICT = json.load(f)

with open('data/homophones/easy.json', 'r') as f:
    HOMOPHONES_EASY = json.load(f)

with open('data/homophones/medium.json', 'r') as f:
    HOMOPHONES_MEDIUM = json.load(f)

with open('data/homophones/hard.json', 'r') as f:
    HOMOPHONES_HARD = json.load(f)

with open("data/oxford_dictionary/easy.json", "r") as f:
    OXFORD_EASY = json.load(f)

with open("data/oxford_dictionary/medium.json", "r") as f:
    OXFORD_MEDIUM = json.load(f)

with open("data/oxford_dictionary/hard.json", "r") as f:
    OXFORD_HARD = json.load(f)


def dfs(i, result, status, relations):
    if (i >= len(relations)):
        status_ = [i for i in status]
        result.append(status_)
        return result

    for x in relations[i]:
        status.append(x)
        result = dfs(i + 1, result, status, relations)
        status.remove(x)

    return result

def get_dp_conll(raw_dp, words, xpos, ners):
    # declare list of dependency trees
    dependency_trees = []

    # make a tuple of relations
    relations = []

    for dependency in raw_dp['dependparser'][0]:
        head = dependency.root_index + 1
        tail = dependency.target_index + 1
        label = dependency.label
        if (label == 'nsubj:xsubj'):
            continue
        is_exist = False
        for i in range(len(relations)):
            for j in range(len(relations[i])):
                if ((relations[i][j][0] == head) and (relations[i][j][1] == tail)) or ((relations[i][j][0] == tail) and (relations[i][j][1] == head)):
                    is_exist = True
                    relations[i].append([head, tail, label])
                    break
            if is_exist:
                break
        if not is_exist:
            relations.append([[head, tail, label]])
    # devide all relation in to corespnding no-loop trees
    dependency_relations = dfs(0, [], [], relations)

    # generate dependency trees
    for dependency_relation in dependency_relations:
        # declare lists
        labels = ['']
        heads = [-1]
        for i in range(1, len(words)):
            labels.append('root')
            heads.append(0)
        # generate tree
        for relation in dependency_relation:
            if (heads[relation[1]] != 0) and (labels[relation[1]] == 'conj:and') and (relation[2] in ['nsubj', 'ccomp', 'xcomp']):
                continue
            heads[relation[1]] = relation[0]
            labels[relation[1]] = relation[2]
        count_root = 0
        for head in heads:
            if head == 0:
                count_root += 1
        if count_root > 1:
            continue
        dependency_trees.append({'words' : words, 'xpos' : xpos, 'heads' : heads, 'labels': labels, 'ners' : ners})

    return dependency_trees


def get_pos_conll(raw_pos):
    words = ['']
    xpos = ['']

    for pos in raw_pos[0]:
        words.append(pos.word)
        xpos.append(pos.pos_tag)

    return words, xpos


def get_ner_conll(raw_ner):
    ners = ['']
    for ner in raw_ner[0]:
        ners.append(ner.ner_tag)
    return ners

def get_morphy(verb, tag):
    morphy = verb
    if (tag in ['VB', 'VBP']):
        morphy = verb
    if (tag == 'VBZ'):
        if (verb.lower() in verb_dictionary['verb_3rd_present']):
            morphy = verb_dictionary['verb_base_form'][verb_dictionary['verb_3rd_present'].index(verb.lower())]
    if (tag == 'VBD'):
        if (verb.lower() in verb_dictionary['verb_past_tense']):
            morphy = verb_dictionary['verb_base_form'][verb_dictionary['verb_past_tense'].index(verb.lower())]      
    if (tag == 'VBN'):
        if (verb.lower() in verb_dictionary['verb_past_participle']):
            morphy = verb_dictionary['verb_base_form'][verb_dictionary['verb_past_participle'].index(verb.lower())]
    if (tag == 'VBG'):
        if (verb.lower() in verb_dictionary['verb_gerund']):
            morphy = verb_dictionary['verb_base_form'][verb_dictionary['verb_gerund'].index(verb.lower())]
    return morphy

def check_belong_to(i, j, heads):
    cnt = 0
    while (j != 0) and (j != i):
        j = heads[j]
        cnt += 1
        if (cnt == 100):
            return False
    if (j == i):
        return True
    else:
        return False

def get_all_word_belong_to(i, words, heads):
    answer = ''
    last_answer_id = -1
    for j in range(1, len(heads)):
        if check_belong_to(i, j, heads):
            answer += ' ' + words[j]
            last_answer_id = j
    return answer, last_answer_id

def get_noun_info(noun, tag):
    noun_labels = ['NN', 'NNP', 'NNS', 'NNPS']
    personal_pronoun_labels = ['PRP']
    singular_personal_pronoun = ['i', 'she', 'he', 'it']
    plural_personal_pronoun = ['we', 'you', 'they']
    ### noun type is singular (0) or prural (1)
    noun_type = 0
    is_human = False
    if (tag in noun_labels):
        if (tag in ['NNS', 'NNPS']):
            noun_type = 1

        ### noun points to Human or not
        synsets = wn.synsets(str(wn.morphy(noun.lower())), 'n')
        if (len(synsets) != 0):
            cnt = 0
            noun = synsets[0]
            while (len(noun.hypernyms()) != 0) and (cnt < 100):
                cnt += 1
                if (noun.name()[:6] == 'person'):
                    is_human = True
                    break
                noun = noun.hypernyms()[0]
    if (tag in personal_pronoun_labels + plural_personal_pronoun):
        if (noun.lower() in plural_personal_pronoun):
            noun_type = 1
        if (noun.lower() in ['i', 'we', 'she', 'he', 'you', 'they']):
            is_human = True

    ### return
    return is_human, noun_type

def random_choice(arr, k, e):
    choices = [item for item in arr if item not in e]
    random.shuffle(choices)
    if len(choices) < k:
        return None
    if k == 1:
        return choices[0]
    return choices[:k]

def get_root_id(heads):
    for i in range(1, len(heads)):
        if heads[i] == 0:
            return i