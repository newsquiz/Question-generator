from paraphrase_dp.active_passive import active_passive_paraphrase
from paraphrase_dp.reported_speech import reported_speech_paraphrase

def generate_paraphrase(words, xpos, heads, labels, ners):
	paraphrase_sentence = []
	ap_paraphrase = active_passive_paraphrase(words, xpos, heads, labels, ners)
	if ap_paraphrase != None:
		paraphrase_sentence.append(ap_paraphrase)
	rs_paraphrase = reported_speech_paraphrase(words, xpos, heads, labels, ners)
	if rs_paraphrase != None:
		paraphrase_sentence.append(rs_paraphrase)
	return paraphrase_sentence