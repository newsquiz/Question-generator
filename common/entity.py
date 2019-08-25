class Entity(list):
    '''An entity in a document.
    
    A entity is comprised of one or more vertices. Here a  vertex is a word in a document.
    '''

    def __init__(self, vertices = [], text=None, refer=None):
        super(Entity, self).__init__()
        self.extend(vertices)
        self.text = text
        self.refer = refer
