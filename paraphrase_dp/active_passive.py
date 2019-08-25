'''
	this paraphrase can only be done by existing these following conditions:
	-	sentence has root verb
	-	sentence has subject
	-	sentence has object
'''
from utils import *


def active_to_passive(words, xpos, heads, labels, verb_id, nsubj_id, obj_id):
	v_list = [words[verb_id]]
	paraphrased = []
	### get all auxiliaries
	aux_id = []
	for i in range(1, len(heads)):
		if (heads[i] == verb_id) and (labels[i] == 'aux'):
			aux_id.append(i)

	### check simple tense
	if (xpos[verb_id] in ['VBP', 'VBZ']) and (len(aux_id) == 0):
		if (xpos[verb_id] == 'VBP'):
			verb = get_morphy(words[verb_id], 'VBP')
		if (xpos[verb_id] == 'VBZ'):
			verb = get_morphy(words[verb_id], 'VBZ')
		aux = 'are'
		if (verb in verb_dictionary['verb_base_form']):
			verb = verb_dictionary['verb_past_participle'][verb_dictionary['verb_base_form'].index(verb)]
		if (xpos[obj_id] in ['NN', 'NNP']):
			aux = 'is'
		v_list = [aux, verb]
	### check past simple
	if (xpos[verb_id] in ['VBD']) and (len(aux_id) == 0):
		verb = get_morphy(words[verb_id], 'VBD')
		aux = 'were'
		if (verb in verb_dictionary['verb_base_form']):
			verb = verb_dictionary['verb_past_participle'][verb_dictionary['verb_base_form'].index(verb)]
		if (xpos[obj_id] in ['NN', 'NNP']):
			aux = 'was'
		v_list = [aux, verb]

	### check present continues
	if (xpos[verb_id] in ['VBG']) and (len(aux_id) == 1) and (xpos[aux_id[0]] in ['VBP', 'VBZ']):
		verb = get_morphy(words[verb_id], 'VBG')
		aux = 'are'
		if (verb in verb_dictionary['verb_base_form']):
			verb = verb_dictionary['verb_past_participle'][verb_dictionary['verb_base_form'].index(verb)]
		if (xpos[obj_id] in ['NN', 'NNP']):
			aux = 'is'
		v_list = [aux, 'being', verb]

	### check present perfect
	if (xpos[verb_id] in ['VBN']) and (len(aux_id) == 1) and (xpos[aux_id[0]] in ['VBP', 'VBZ']):
		verb = get_morphy(words[verb_id], 'VBN')
		aux = 'have'
		if (verb in verb_dictionary['verb_base_form']):
			verb = verb_dictionary['verb_past_participle'][verb_dictionary['verb_base_form'].index(verb)]
		if (xpos[obj_id] in ['NN', 'NNP']):
			aux = 'has'
		v_list = [aux, 'been', verb]

	### check simple future
	if (xpos[verb_id] in ['VB']) and (len(aux_id) == 1):
		verb = get_morphy(words[verb_id], 'VB')
		if (verb in verb_dictionary['verb_base_form']):
			verb = verb_dictionary['verb_past_participle'][verb_dictionary['verb_base_form'].index(verb)]
		v_list = ['will', 'be', verb]

	### check past continues
	if (xpos[verb_id] in ['VBG']) and (len(aux_id) == 1) and (xpos[aux_id[0]] in ['VBD']):
		verb = get_morphy(words[verb_id], 'VBG')
		aux = 'were'
		if (verb in verb_dictionary['verb_base_form']):
			verb = verb_dictionary['verb_past_participle'][verb_dictionary['verb_base_form'].index(verb)]
		if (xpos[obj_id] in ['NN', 'NNP']):
			aux = 'was'
		v_list = [aux, 'being', verb]

	### check past perfect
	if (xpos[verb_id] in ['VBN']) and (len(aux_id) == 1) and (xpos[aux_id[0]] in ['VBD']):
		verb = get_morphy(words[verb_id], 'VBN')
		if (verb in verb_dictionary['verb_base_form']):
			verb = verb_dictionary['verb_past_participle'][verb_dictionary['verb_base_form'].index(verb)]
		v_list = ['had', 'been', verb]

	### check future perfect
	if (xpos[verb_id] in ['VBN']) and (len(aux_id) == 2):
		verb = get_morphy(words[verb_id], 'VBN')
		if (verb in verb_dictionary['verb_base_form']):
			verb = verb_dictionary['verb_past_participle'][verb_dictionary['verb_base_form'].index(verb)]
		v_list = ['will', 'have', 'been', verb]

	### merge all parts
	for i in range(1, len(heads)):
		if (heads[i] == verb_id):
			if (labels[i] in ['aux', 'auxpass']):
				continue
			if (i == nsubj_id):
				for j in range(1, len(heads)):
					if check_belong_to(obj_id, j, heads):
						paraphrased.append(words[j])
				continue
			if (i == obj_id):
				paraphrased.append('by')
				for j in range(1, len(heads)):
					if check_belong_to(nsubj_id, j, heads):
						paraphrased.append(words[j])
				continue
			for j in range(1, len(heads)):
				if check_belong_to(i, j, heads):
					paraphrased.append(words[j])
		if (i == verb_id):
			paraphrased += v_list

	### return
	return paraphrased

def passive_to_active(words, xpos, heads, labels, verb_id, nsubj_id, obj_id):
	pass

def active_passive_paraphrase(words, xpos, heads, labels, ners):
	### declare
	paraphrased = [word for word in words]
	### check 3 conditions
	verb_labels = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
	noun_labels = ['NN', 'NNP', 'NNS', 'NNPS', 'PRP']
	nsubj_labels = ['nsubj', 'nsubjpass']

	### check whether sentence has root verb
	verb_id = -1
	for i in range(1, len(heads)):
		if (heads[i] == 0) and (xpos[i] in verb_labels):
			verb_id = i
			break
	if (verb_id == -1):
		return None

	### check whether sentence has subject
	nsubj_id = -1
	for i in range(1, len(heads)):
		if (heads[i] == verb_id) and (labels[i] in nsubj_labels) and (xpos[i] in noun_labels) and (xpos[i] != 'PRP'):
			nsubj_id = i
			break
	if (nsubj_id == -1):
		return None

	### check whether sentence has object (direct object)
	obj_id = -1
	for i in range(1, len(heads)):
		if (heads[i] == verb_id) and (labels[i] == 'dobj') and (xpos[i] in noun_labels) and (xpos[i] != 'PRP'):
			obj_id = i 
			break
	if (obj_id == -1):
		return None

	### get auxiliary:pass if exist
	auxpass_id = -1
	for i in range(1, len(heads)):
		if (heads[i] == verb_id) and (labels[i] == 'auxpass'):
			auxpass_id = i
	### check current sentence is active or passive
	if (xpos[verb_id] == 'VBN') and (auxpass_id != -1):
		return None
	else:
		paraphrased = active_to_passive(words, xpos, heads, labels, verb_id, nsubj_id, obj_id)

	return ' '.join(paraphrased)
