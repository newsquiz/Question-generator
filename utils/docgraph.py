from collections import defaultdict
from enlp import NER, POS, DependencyParser, Coreference, SentenceTokenizer, WordTokenizer
from .kgraph import KnowledgeGraph
from common import Entity

import pdb


class DocumentGraph(object):
    '''Reading questin generator.'''
    
    def __init__(self, text):
        self.sentoken = SentenceTokenizer()
        self.wordtoken = WordTokenizer()
        self.ner = NER()
        self.pos = POS()
        self.depend = DependencyParser()
        self.corefer = Coreference()

        #initilizing...
        # print('Initilizing...')
        self.text = text
        self.sent_tokens, self.sents, self.sent_token_toid, self.tokenid_to_sentid = self._build_token_id_mapping(text)
        self.kg, self.entities = self._build_knowledge_graph()

    def _build_token_id_mapping(self, text):
        # print('Building index mapping...')
        sents = self.sentoken.transform(text)
        sent_tokens = []
        sent_token_toid = defaultdict(dict)
        tokenid_to_sentid = {}
        id_count = -1
        for send_id, s in enumerate(sents):
            tokens = self.wordtoken.transform(s)
            sent_tokens.append(tokens)
            for token_id, token in enumerate(tokens):
                id_count +=1
                sent_token_toid[send_id][token_id] = id_count
                tokenid_to_sentid[id_count] = (send_id, token_id)

        return sent_tokens, sents, sent_token_toid, tokenid_to_sentid

    def _get_token_id(self, sent_id, token_id):
        if token_id in self.sent_token_toid[sent_id]:
            return self.sent_token_toid[sent_id][token_id]
        else:
            raise ValueError('Sentence {} doesnt has tokenid {}'.format(sent_id, token_id))

    def _build_knowledge_graph(self):
        kg = KnowledgeGraph(['text', 'sent_id', 'token_id', 'pos', 'ner', 'begin_text', 'end_text'], ['string', 'short', 'short', 'string', 'string', 'string', 'string'], ['dependency', 'connect_text', 'relation'], ['string', 'string', 'string'])
        #begin_text, end_text is the text at begining or starting of sentence which is not belonging to any entity or their relations.
        #connec_text is the text connecting two entity

        
        # print('======building coreference knowledge graph...')
        coref_kg = self._build_coreference_knowledge_graph()

        # print('======Add sentences to knowledge graph...')
        sent_entities = {}
        for i, s in enumerate(self.sent_tokens):
            s_entities = self._add_sentence_to_knowledge_graph(i, s, kg)
            sent_entities[i] = s_entities

        # print('======Combine DocumentKG and CoreferenceKG...')
        self._combine_dockg_and_corefkg(kg, coref_kg)
        return kg, sent_entities


    def _combine_dockg_and_corefkg(self, kg, coref_kg):
        for e in coref_kg.get_edges_by_property('relation', 'coreference'):
            mention = e[0]
            mention_sent_id = coref_kg.get_vertex_property_value(mention, 'psent')
            mention_token_id = coref_kg.get_vertex_property_value(mention, 'pstart')
            #mention_token_end_id = coref_kg.get_vertex_property_value(mention, 'pend')

            refer = e[1]
            refer_sent_id = coref_kg.get_vertex_property_value(refer, 'psent')
            refer_token_id = coref_kg.get_vertex_property_value(refer, 'pstart')
            #refer_token_end_id = coref_kg.get_vertex_property_value(mention, 'pend')

            v_start_id = self._get_token_id(mention_sent_id, mention_token_id)
            v_end_id = self._get_token_id(refer_sent_id, refer_token_id)
            kg.add_new_edge_with_properties(v_start_id, v_end_id, [('relation', 'coreference')])

    def _build_coreference_knowledge_graph(self):
        kg = KnowledgeGraph(['text', 'psent', 'pstart', 'pend', 'position'], ['string', 'short', 'short', 'short', 'vector<short>'], ['relation'], ['string'])

        # print('======Build coreference knowledge graph...')
        _, corefers = self.corefer.transform(self.text)

        for refer in corefers:
            refer_text = self._get_text_from_coref(refer.refer)
            mention_text = self._get_text_from_coref(refer.mention)
            # print(mention_text + '->' + refer_text + '-> add a vertex: text: ' + refer_text + ', position: {}'.format(refer.refer.to_list()))
            v_refer = self._get_refer_by_position(*refer.refer.to_list(), kg)
            if len(v_refer)>0:
                # print ('Same refer to', refer.refer.to_list())
                v_refer = v_refer[0]
            else:
                prefer = refer.refer
                v_refer = kg.add_new_vertex_with_properties([('text', refer_text), ('psent', prefer.sent_id), ('pstart', prefer.start), ('pend', prefer.end), ('position', prefer.to_list())])
            mention = refer.mention
            v_mention = kg.add_new_vertex_with_properties([('text', mention_text), ('psent', mention.sent_id), ('pstart', mention.start), ('pend', mention.end), ('position', mention.to_list())])
            kg.add_new_edge_with_properties(v_mention, v_refer, [('relation', 'coreference')])
        return kg

    def _is_added_to_knowledge_graph(self, sent_id, start, end, kg):
        return len(kg.get_vertices_by_property('position', [[sent_id, start, end]]))>0

    def _get_refer_by_position(self, sent_id, start, end, kg):
        return kg.get_vertices_by_property('position', [[sent_id, start, end]])
    
    def _get_text_from_coref(self, coref):
        return self._get_sub_text(coref.sent_id, coref.start, coref.end)

    def _get_sub_text(self, sent_id, start, end):
        #TODO recheck correct and speed up by save some data
        return ' '.join(self.sent_tokens[sent_id][start:end])

    def _add_sentence_to_knowledge_graph(self, sent_id, tokens, kg):
        #TODO continue here, levarage NLP analyses to extend knowledge graph
        #dcoref = corefers.to_dict_sent_coref()
        sent = ' '.join(tokens)
        # print('=======Process: ', sent)
        skg = self._present_sentence_as_knowledge_graph(sent)
        skg, entities = self._build_entities_relations_graph_from_sentence_graph(skg, tokens)
        self._join_sentence_graph_to_doc_graph(sent_id, tokens, skg, kg)

        #map entities to new vertices
        sent_entities = []
        for entity in entities:
            v0 = self._get_token_id(sent_id, int(entity[0]))
            new_e = Entity([kg.get_vertex(v0)])
            for v in entity[1:]:
                new_id = self._get_token_id(sent_id, int(v))
                new_e.append(kg.get_vertex(new_id))
            sent_entities.append(new_e)
        # print('#entites in sentence: ', len(sent_entities))
        return sent_entities

    def _join_sentence_graph_to_doc_graph(self, sent_id, tokens, skg, kg):

        #Copy vertices
        v_pnames = list(skg.vertex_pnames)
        v_pnames.append('sent_id')
        for token_id, token in enumerate(tokens):
            pvalues = skg.get_vetex_properties_values(skg.get_vertex(token_id), skg.vertex_pnames)
            #v_pnames = skg.vertex_pnames
            #v_pnames.append('sent_id')
            pvalues.append(sent_id)
            new_v = kg.add_new_vertex_with_properties(zip(v_pnames, pvalues))
            v_id = self._get_token_id(sent_id, token_id)
            assert v_id == int(new_v), 'Index is not fit between document and graph??'

        #copy edge
        e_pnames = list(skg.edge_pnames)
        for e in skg.get_edges():
            pvalues = skg.get_edge_properties_values(e, skg.edge_pnames)
            new_e = kg.add_new_edge_with_properties(int(e[0]), int(e[1]), zip(e_pnames, pvalues))

        # print('Doc graph infos: ', kg.get_description())

    def _present_sentence_as_knowledge_graph(self, sent):
        pos = self.pos.transform(sent)
        dp = self.depend.transform(sent)
        ner = self.ner.transform(sent)

        skg = KnowledgeGraph(['text', 'token_id', 'pos', 'ner', 'begin_text', 'end_text'], ['string', 'short', 'string', 'string', 'string', 'string'], ['dependency', 'connect_text'], ['string', 'string'])
        for token_id, ptag in enumerate(pos[0]):
            assert len(ner[0])==len(pos[0]), 'POS and NER using different tokens??'
            skg.add_new_vertex_with_properties([('text', ptag.word), ('token_id', token_id), ('pos', ptag.pos_tag), ('ner', ner[0][token_id].ner_tag)])

        for d in dp[0]:
            skg.add_new_edge_with_properties(d.root_index, d.target_index, [('dependency', d.label)])
        
        return skg
    
    def _build_entities_relations_graph_from_sentence_graph(self, skg, tokens):
        entities = self._get_entities_from_sentence_graph(skg)

        entities = sorted(entities, key=lambda e: int(e[0]))
        # print('Entities text: ', self._get_entities_text(skg, entities))

        #add relation_text ege is the text between entities found
        for pi, e in enumerate(entities[1:]):
            pe = entities[pi]
            start_id = int(pe[-1])+1
            end_id = int(e[0])
            ctext = ' '.join(tokens[start_id:end_id])
            if ctext!='':
                skg.add_new_edge_with_properties(int(pe[0]), int(e[0]), [('connect_text', ctext)])
                # print(pi, pi+1, ctext)
    
        #add redundant text into graph
        first_entity_vertex = entities[0][0]
        if int(first_entity_vertex)>0:
            begin_text = ' '.join(tokens[0:int(first_entity_vertex)])
            skg.add_vertex_property(first_entity_vertex, 'begin_text', begin_text) 
            # print('begin_text:', begin_text)
        last_entity_vertex = entities[-1][-1]
        if int(last_entity_vertex)<len(tokens)-1:
            end_text = ' '.join(tokens[int(last_entity_vertex)+1:])
            if end_text.strip()!= '.':
                skg.add_vertex_property(last_entity_vertex, 'end_text', end_text) 
                # print('end_text:', end_text)

        return skg, entities

    def _get_entities_from_sentence_graph(self, skg):
        entities = []
        used_vertices = []
        #Add entity type (from NER) DATE, TIME, MONEY, LOCATION as entity
        ners = skg.get_vertices_by_property('ner', ['DATE', 'TIME', 'MONEY', 'LOCATION'])
        
        entities.extend(self._group_adjacent_vertices_same_property_to_entity(ners, skg, 'ner'))
        used_vertices.extend(ners)

        #compound as entities
        compound_edges = skg.get_edges_by_property('dependency' , 'compound')
        for start_v, end_v in compound_edges:
            if start_v in used_vertices:
                continue
            #expanding to get full compound including the determiner
            entity_vertices = skg.expand_by_relation_types(start_v, ['compound', 'det'])
            entity_vertices = sorted(entity_vertices, key=lambda v:int(v))
            entities.append(Entity(entity_vertices))
            used_vertices.extend(entity_vertices)

        #NN, NNP, NNS, PRP as entities
        nouns = skg.get_vertices_by_property('pos', ['NN', 'NNP', 'NNS', 'PRP'])
        for v in nouns:
            if v in used_vertices:
                continue
            entity_vertices = skg.expand_by_relation_types(v, ['det', 'amod', 'nummod', 'nmod:of', 'nmod:poss'], infinite_deep=True)
            entity_vertices = sorted(entity_vertices, key=lambda v:int(v))
            entities.append(Entity(entity_vertices))
            used_vertices.extend(entity_vertices)

        return self._filter_sub_entities(entities)

    def _filter_sub_entities(self, entities):
        entities = sorted(entities, key=lambda e: int(e[-1]))
        ret_entities = []
        for i, e in enumerate(entities):
            is_sub_entity = False
            for check in entities[i+1:]:
                if e!=check and set(e) < set(check):
                    is_sub_entity = True
                    break
            if not is_sub_entity:
                ret_entities.append(e)
        return ret_entities

    def _get_entities_text(self, kg, entities):
        entities_text = []
        for e in entities:
            entities_text.append(' '.join(kg.get_vertices_property_value(e, 'text')))
        return entities_text
            

    def _group_adjacent_vertices_same_property_to_entity(self, vertices, kg, pname):
        if len(vertices)==0:
            return []

        vertices = sorted(vertices, key= lambda v: int(v))
        entities = []
    
        last_entity = Entity([vertices[0]])
        entities.append(last_entity)

        last_pvalue = kg.get_vertex_property_value(vertices[0], pname)
        for v in vertices[1:]:
            v_pvalue = kg.get_vertex_property_value(v, pname)
            if v_pvalue == last_pvalue:
                last_entity.append(v)
            else:
                last_pvalue = v_pvalue
                last_entity = Entity([v])
                entities.append(last_entity)
        return entities

    def get_sentence_entities(self, sent_id):
        entities = self.entities[sent_id]
        for e in entities:
            e.text = self.get_entity_text(e)
            e.refer = self.get_entity_refer(e)
        return entities

    def get_entity_text(self, entity):
        return ' '.join(self.kg.get_vertices_property_value(entity, 'text'))

    def get_entity_refer(self, entity):
        for v in entity:
            for e in v.out_edges():
                relation = self.kg.get_edge_property_value(e, 'relation')
                if relation == 'coreference':
                    refer_entity =  self.get_entity_at_token_id(int(e.target()))
                    if refer_entity is not None:
                        refer_entity.refer = self.get_entity_refer(refer_entity)
                        refer_entity.text = self.get_entity_text(refer_entity)
                    return refer_entity
        return None

    def get_entity_at_token_id(self, token_id):
        sent_id, sent_token_id = self.tokenid_to_sentid[token_id]
        for e in self.entities[sent_id]:
            if int(e[-1])>=token_id:
                return e
        return None
