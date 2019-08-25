import graph_tool as gt
import logging
import pdb

class KnowledgeGraph(object):
    
    def __init_old__(self, pos_tags, dependencies):
        """Init knowledge graph representing dependency tree (A graph with labels on vertices as PoS and dependency labels between words as edge labels).
        
        Args:
            pos_tags: a list of tuple (word, {PartOfSpeech: 'N/V/...'}
            dependencies: a list of tupe (relation_type, head word, dependent word)
            
        """
        self.logger = logging.getLogger()
        self.g = gt.Graph()
        self.v_labels = self.g.new_vertex_property('string')
        self.e_labels = self.g.new_edge_property('string')

        #----------------building verties
        self.word2id={}
        self.id2word={}
        #for vertices
        for i, (word, tags) in enumerate(pos_tags):
            tag = tags['PartOfSpeech']
            v = self.g.add_vertex()
            self.v_labels[v] = tag

            if word in self.word2id: #for words occur multiple times in a sentence
                self.logger.warn('One word {} occurs multiple times in sentence {}.'.format(word, ' '.join(self.word2id.keys())))
                self.word2id[word+ '_' + str(i)] = i
            else:
                self.word2id[word] = i

            self.id2word[i] = word
        #for edges
        for rel_type, (head, hp), (tail, tp) in dependencies:
            #start_node = self.word2id[head]
            #tail_node = self.word2id[tail]
            start_node = hp
            tail_node = tp
            e = self.g.add_edge(start_node, tail_node)
            self.e_labels[e] = rel_type
        
        #set labels
        self.g.vertex_properties['pos'] = self.v_labels
        self.g.edge_properties['dependency'] = self.e_labels

    def __init__(self, vertex_pnames=[], vertex_ptypes=[], edge_pnames=[], edge_ptypes=[]):
        '''Init knowledge graph.'''
        self.g = gt.Graph()

        self.vertex_pnames = vertex_pnames
        self.vertex_ptypes = vertex_ptypes
        self.edge_pnames = edge_pnames
        self.edge_ptypes = edge_ptypes

        #setup property
        for name, vtype in zip(self.vertex_pnames, self.vertex_ptypes):
            self.g.vertex_properties[name] = self.g.new_vertex_property(vtype)

        for name, vtype in zip(self.edge_pnames, self.edge_ptypes):
            self.g.edge_properties[name] = self.g.new_edge_property(vtype)

    def add_new_vertex(self):
        return self.g.add_vertex()

    def add_new_edge(self, start_node_id, end_node_id):
        return self.g.add_edge(start_node_id, end_node_id)

    def add_vertex_property(self, v, pname, pvalue):
        self.g.vertex_properties[pname][v]=pvalue

    def add_edge_property(self, edge, pname, pvalue):
        self.g.edge_properties[pname][edge]=pvalue

    def add_new_vertex_with_properties(self, properties_values):
        v = self.add_new_vertex() 
        for pname, pvalue in properties_values:
            self.add_vertex_property(v, pname, pvalue)
        return v

    def add_new_edge_with_properties(self, start_node_id, end_node_id, properties_values):
        e = self.add_new_edge(start_node_id, end_node_id)
        for pname, pvalue in properties_values:
            self.add_edge_property(e, pname, pvalue)
        return e
        
    def get_vertices_by_property(self, pname, find_pvalues):
        """Get all vertices labeled with the given tags."""
        #TODO using graph filtering
        pvalues = self.g.vertex_properties[pname]
        return [v for v in self.g.vertices() if pvalues[v] in find_pvalues]

    def _REMOVE_get_edges_by_relation_type(self, relation_type):
        #TODO Remove the duplicated method
        """Get all edges labeled with the given relation_type."""
        #TODO using graph filtering
        dependencies = self.g.edge_properties['dependency']
        return [e for e in self.g.edges() if dependencies[e] == relation_type]

    def get_edges_by_property(self, pname, pvalue):
        """Get all edges labeled with the given relation_type."""
        #TODO using graph filtering
        pvalues = self.g.edge_properties[pname]
        return [(e.source(), e.target()) for e in self.g.edges() if pvalues[e] == pvalue]

    def get_vertices_title(self, vs):
        """.
        
        Args:
            v is a graph-tool vertex or a set of those ones
        """
        vs = self._be_list(vs)
        return [self.id2word[int(v)] for v in vs]

    def filter_vertices_by_tag(self, vertices, eliminated_tags):
        eliminated_tags = self._be_list(eliminated_tags)
        pos_tags = self.g.vertex_properties['pos']
        return [v for v in vertices if pos_tags[v] not in eliminated_tags]
    
    def _be_list(self, vs):
        if isinstance(vs, tuple):
            vs = list(vs)
            #TODO in some case, these vertices might be swapped their order, should we reorder them bye occurence in sentence??
        if not isinstance(vs, list):
            vs = [vs]
        return vs

    def filter_vertices_by_relation_type(self, vertices, eliminated_types, is_target=True):
        """Filter out vertices which attend either as source of target on the relation types given.
        
        Args:
            is_target: Boolean value, default equals True, meaning eliminat a vertex if it is in target of a edge with the labels given
        """
        eliminated_types = self._be_list(eliminated_types)
        dependencies = self.g.edge_properties['dependency']
        ret_vertices = []

        if is_target:#check all in_neighbours
            for t in vertices:
                passed = True
                in_neighbours = t.in_neighbours()
                for s in in_neighbours:
                    if dependencies[(s, t)] in eliminated_types:
                        passed = False
                        break
                if passed:
                    ret_vertices.append(t)
        else:#check all out_neighbours
            for s in vertices:
                passed = True
                out_neighbours = s.out_neighbours()
                for t in out_neighbours:
                    if dependencies[(s, t)] in eliminated_types:
                        passed = False
                        break
                if passed:
                    ret_vertices.append(s)

        return ret_vertices

    def find_neighbours_by_relation_type(self, vertex, relation_type):
        """Return out neighbours of the given vertex which have connected edges labling as specified relation_type .
        """
        out_neighbours = vertex.out_neighbours()
        dependencies = self.g.edge_properties['dependency']
        ret_vertices = []
        for t in out_neighbours:
            if dependencies[(vertex, t)]==relation_type:
                ret_vertices.append(t)
        return ret_vertices

    def expand_by_relation_types(self, vertex, relation_types, infinite_deep=False):
        """Return a list of vertices which is connected to given vertex by the given relation type. This process is recusively"""
        dependencies = self.g.edge_properties['dependency']
        ret_vertices = [vertex]
        visited_stack = [vertex]
        while len(visited_stack)>0:
            start_node = visited_stack.pop()
            out_neighbours = start_node.out_neighbours()
            for next_node in out_neighbours:
                if dependencies[(start_node, next_node)] in relation_types:
                    ret_vertices.append(next_node)
                    if infinite_deep:
                        visited_stack.append(next_node)
        return ret_vertices

    def get_edge_property_value(self, e, pname):
        return self.g.edge_properties[pname][e]

    def get_vertex_property_value(self, v, pname):
        return self.g.vertex_properties[pname][v]
    
    def get_vertices_property_value(self, vertices, pname):
        pvalues = []
        for v in vertices:
            pvalues.append(self.get_vertex_property_value(v, pname))
        return pvalues

    def get_vetex_properties_values(self, v, pnames):
        pvalues = [] 
        for pname in pnames:
            pvalues.append(self.get_vertex_property_value(v, pname))
        return pvalues

    def get_vertex(self, vertex_id):
        return self.g.vertex(vertex_id)

    def get_edges(self):
        edges = []
        for e in self.g.edges():
            edges.append((e.source(), e.target()))
        return edges

    def get_edge_properties_values(self, e, pnames):
        pvalues = [] 
        for pname in pnames:
            pvalues.append(self.get_edge_property_value(e, pname))
        return pvalues

    def get_description(self):
        return str(self.g)

