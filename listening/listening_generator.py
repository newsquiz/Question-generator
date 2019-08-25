"""
    Get text document and generate all posible question-answer with corresponding tags
    Question types:
        - fullfill
    Level:
        - Easy
        - Medium
        - Hard
        - Freestyle
    Tags:
        - Question type and sub question type:
            + Fullfill:
                - purpose: tense, topic new words, prasal verb, entities, homophones,...

"""
import re

from utils import *
from listening.short_answer.short_answer_generator import ShortAnswerGenerator
from listening.multi_choice.multi_choice_generator import MultiChoiceGenerator
from listening.yes_no.yes_no_generator import YesNoGenerator
from listening.fullfill.fullfill_generator import FullfillGenerator
from paraphrase_dp.generate_paraphrase import generate_paraphrase

from enlp import NER, POS, DependencyParser, Coreference, SentenceTokenizer, WordTokenizer
import pdb


class ListeningGenerator(object):
    def __init__(self):
        self.short_answer = ShortAnswerGenerator()
        self.multi_choice = MultiChoiceGenerator()
        self.yes_no = YesNoGenerator()
        self.fullfill = FullfillGenerator()
        self.pos = POS()
        self.ner = NER()
        self.dependparser = DependencyParser()
        self.sentence_tokenizer = SentenceTokenizer()
        self.word_tokenizer = WordTokenizer()
        self.coreference = Coreference()

    def preprocess_sentence(self, raw_sentences):
        """
            $2  -> 2 dollars
            2%  -> 2 percents
            £10 -> 10 euro
            n't -> not
        """
        res = []
        for sentence in raw_sentences:
            words = sentence.split(' ')
            for i in range(len(words)):
                if re.match('\$(\d)*', words[i]) != None:
                    words[i] = re.match('\$(\d)*', words[i]).group(1) + ' dollar'
                if re.match('£(\d)*', words[i]) != None:
                    words[i] = re.match('£(\d)*', words[i]).group(1) + ' euro'
                if re.match('(\d*)%', words[i]) != None:
                    words[i] = re.match('(\d*)%', words[i]).group(1) + ' percent'
            res.append(' '.join(words))
        return res


    def prepare_ners(self, sentences):
        doc_ners = {
            'LOCATION': [],
            'PERSON': [],
            'ORGANIZATION': [],
            'COUNTRY': [],
            'TIME': [],
            'DATE': [],
            'NATIONALITY': [],
        }
        for sentence in sentences:
            raw_pos = self.pos.transform(sentence)
            if (len(raw_pos) == 0):
                continue
            raw_ner = self.ner.transform(sentence)
            words, xpos = get_pos_conll(raw_pos)
            ners = get_ner_conll(raw_ner)
            i = 0
            while i < len(words):
                if ners[i] in doc_ners.keys():
                    ner = ners[i]
                    word = ''
                    while (i < len(words)) and (ners[i] == ner):
                        word += ' ' + words[i]
                        i += 1
                    doc_ners[ner].append(word[1:])
                else:
                    i += 1
        return doc_ners


    def prepare_raw_sentences(self, raw_sentences):
        raw_sentences_data = []
        for i, sentence in enumerate(raw_sentences):
            # process nlp tasks
            # print("sentence: ", sentence)
            raw_pos = self.pos.transform(sentence)
            if (len(raw_pos) == 0):
                continue
            raw_dp = self.dependparser.predict({'text' : sentence})
            raw_ner = self.ner.transform(sentence)
            words, xpos = get_pos_conll(raw_pos)
            ners = get_ner_conll(raw_ner)
            dependency_trees = get_dp_conll(raw_dp, words, xpos, ners)
            # add to sentences data
            if len(dependency_trees) == 0:
                continue
            sentence_data = dependency_trees[0]
            raw_sentences_data.append((i, sentence_data))
        return raw_sentences_data


    def prepare_paraphrase_sentences(self, raw_sentences):
        paraphrase_sentences = []
        for i, sentence in raw_sentences:
            words = sentence['words']
            xpos = sentence['xpos']
            heads = sentence['heads']
            labels = sentence['labels']
            ners = sentence['ners']
            for paraphrase_sentence in generate_paraphrase(words, xpos, heads, labels, ners):
                # paraphrase_sentences.append((paraphrase_sentence, i))
                # process nlp tasks
                raw_pos = self.pos.transform(paraphrase_sentence)
                if (len(raw_pos) == 0):
                    continue
                raw_dp = self.dependparser.predict({'text' : paraphrase_sentence})
                raw_ner = self.ner.transform(paraphrase_sentence)
                words, xpos = get_pos_conll(raw_pos)
                ners = get_ner_conll(raw_ner)
                dependency_trees = get_dp_conll(raw_dp, words, xpos, ners)
                # add to sentences data
                sentence_data = dependency_trees[0]
                paraphrase_sentences.append((i, sentence_data))

        return paraphrase_sentences   


    def replace_coreference(self, document):
        """
            replace coref for PRP only
        """
        coref_sentences = []
        # get tokens
        sent_tokens = []
        sentences = self.sentence_tokenizer.transform(document)
        sentences = self.preprocess_sentence(sentences)
        for sentence in sentences:
            sent_tokens.append(self.word_tokenizer.transform(sentence))
        # get replace list
        rp_list = {}
        for i in range(len(sentences)):
            rp_list[str(i)] = {
                'rp_idxs'  : [],
                'rp_words' : []
            }
        _, corefers = self.coreference.transform(document)
        for coref in corefers:
            sent_id = coref.mention.sent_id
            if (coref.mention.end - coref.mention.start == 1) and (sent_tokens[sent_id][coref.mention.start].lower() in ['he', 'she', 'it', 'they']):
                target = " ".join(sent_tokens[coref.refer.sent_id][coref.refer.start:coref.refer.end])
                rp_list[str(sent_id)]['rp_idxs'].append(coref.mention.start)
                rp_list[str(sent_id)]['rp_words'].append(target)
        # gen coref sentences
        for i in range(len(sentences)):
            j = 0
            sentence = ""
            while j < len(sent_tokens[i]):
                if j in rp_list[str(i)]['rp_idxs']:
                    sentence += ' ' + rp_list[str(i)]['rp_words'][rp_list[str(i)]['rp_idxs'].index(j)]
                else:
                    sentence += ' ' + sent_tokens[i][j]
                j += 1
            sentence = sentence[1:]
            coref_sentences.append(sentence)
            # print(sentence)
        return coref_sentences


    def get_questions(self, document):
        """
            data: {
                raw_sentences = [],
                paraphrase_sentences = [],
                summerized_sentences = [],
            }
        """ 
        # prepare data
        data = {}
        raw_sentences = self.sentence_tokenizer.transform(document)
        coref_sentences = self.replace_coreference(document)
        data["ners"] = self.prepare_ners(coref_sentences)
        data["raw_sentences"] = self.prepare_raw_sentences(coref_sentences)
        data["paraphrase_sentences"] = self.prepare_paraphrase_sentences(data["raw_sentences"])
        # print(data["paraphrase_sentences"])
        # # generate questions
        questions = []
        questions += self.fullfill.get_questions(data)
        questions += self.short_answer.get_questions(data)
        questions += self.multi_choice.get_questions(data)
        questions += self.yes_no.get_questions(data)
        # return 
        return questions
        
        