import graphviz

class node(object):
    maxid = 0

    def __init__(self, t='const', val=None,  ch=None, no=None, pos=None):
        self.id = node.maxid
        node.maxid += 1
        self.type = t
        self.value = val
        self.child = ch or []
        self.lineno = no
        self.lexpos = pos

    def __repr__(self):
        return f'{self.type} {self.value}'

    def _repr_graph(self):
        return f'{self.id}, {self.type}, {self.value}'

    
    def add_edges(self, graph):
        if self is None:
            return
        if isinstance(self.child, list):
            for child in self.child:
                graph.edge(self._repr_graph(), child._repr_graph())
                child.add_edges(graph)
        elif isinstance(self.child, node):
            graph.edge(self._repr_graph(), self.child._repr_graph())
            self.child.add_edges(graph)
        elif isinstance(self.child, dict):
            for key, value in self.child.items():
                if value:
                    graph.edge(self._repr_graph(), value._repr_graph())
                    value.add_edges(graph)

    def visualize(self, name = 'tree'):
        if name:
            graph = graphviz.Digraph(name)
            self.add_edges(graph)
            graph.render(directory='Graphs')