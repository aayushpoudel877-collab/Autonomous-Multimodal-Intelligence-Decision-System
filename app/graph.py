import re
import networkx as nx
class KnowledgeGraph:
    def __init__(self): self.g=nx.MultiDiGraph()
    def add_text(self,sid,text):
        self.g.add_node(sid,type="source")
        for e in sorted(set(re.findall(r"\b[A-Z][A-Za-z0-9_-]{2,}\b",text))):
            self.g.add_node(e,type="entity")
            self.g.add_edge(sid,e,relation="mentions")
    def export(self):
        return {"nodes":[{"id":n,**d} for n,d in self.g.nodes(data=True)],
                "edges":[{"source":u,"target":v,**d} for u,v,d in self.g.edges(data=True)]}
knowledge_graph=KnowledgeGraph()
