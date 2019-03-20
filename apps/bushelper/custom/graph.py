
class Graph(object):
    class Vertex:
        def __init__(self, name=None):
            self.name = name

    def __init__(self):
        self.vertices = {}

    def push_edge(self, src, dst):
        if src not in self.vertices:
            self.vertices[src] = []
            self.vertices[src].append(dst)

    def __len__(self):
        self.vertices.__len__()

