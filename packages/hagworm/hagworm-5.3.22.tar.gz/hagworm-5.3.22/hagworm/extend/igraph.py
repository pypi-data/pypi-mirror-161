# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from typing import List, Tuple, Dict
from igraph import Graph, Vertex, VertexSeq, Edge, EdgeSeq


class DiGraph:

    def __init__(self, name: str):

        self._graph = Graph(directed=True, graph_attrs={r'name': name})
        self._vertices = {}

    def __len__(self):

        return len(self._vertices)

    def __repr__(self):

        return f'<DiGraph: {self.name}, vertices: {self._graph.vcount()}, edges: {self._graph.ecount()}>'

    @property
    def name(self) -> str:

        return self._graph[r'name']

    @property
    def graph(self) -> Graph:

        return self._graph

    @property
    def vertex_seq(self) -> VertexSeq:

        return self._graph.vs

    @property
    def edge_seq(self) -> EdgeSeq:

        return self._graph.es

    def clear(self):

        self._graph.clear()
        self._vertices.clear()

    def find_vertex(self, name: str) -> Vertex:

        return self._vertices.get(name)

    def find_vertices(self, names: List[str]) -> List[Vertex]:

        return [self._vertices.get(name) for name in names if name in self._vertices]

    def add_vertex(self, name: str) -> Vertex:

        vertex = self._vertices.get(name)

        if vertex is None:
            vertex = self._vertices[name] = self._graph.add_vertex(name)

        return vertex

    def init_edges(self, edges: List[Tuple[Vertex]]):

        self._graph.add_edges(edges)

    def find_edges(self, source: Vertex, target: Vertex) -> List[Edge]:

        edges = self._graph.es.select(_source=source.index, _target=target.index).indices

        return [self._graph.es[_e] for _e in edges]

    def add_edge(self, source: Vertex, target: Vertex) -> Edge:

        edges = self.find_edges(source, target)

        if edges:
            return edges[0]
        else:
            return self._graph.add_edge(source, target)

    def del_edge(self, source: Vertex, target: Vertex):

        edges = self._graph.es.select(_source=source.index, _target=target.index).indices

        if edges:
            self._graph.delete_edges(edges)

    def find_in(self, name: str) -> List[Vertex]:

        vertex = self.find_vertex(name)

        if vertex is None:
            return None

        return vertex.predecessors()

    def find_out(self, name: str) -> List[Vertex]:

        vertex = self.find_vertex(name)

        if vertex is None:
            return None

        return vertex.successors()

    def find_all(self, name: str, mode=r'out') -> List[str]:

        vertex = self.find_vertex(name)

        if vertex is None:
            return []

        vertices = self._graph.subcomponent(vertex.index, mode=mode)

        return [self._graph.vs[_v][r'name'] for _v in vertices if _v != vertex.index]

    def find_tree(self, name: str, depth=0xff, mode=r'out') -> Dict[str, List[str]]:

        vertex = self.find_vertex(name)

        if vertex is None:
            return {}

        nodes = {}
        vertices = [vertex]

        for _ in range(depth):

            _vertices = vertices.copy()
            vertices.clear()

            for _vertex in _vertices:

                _sub_vertices = _vertex.successors() if mode == r'out' else _vertex.predecessors()

                if _sub_vertices:

                    _nodes = nodes[_vertex[r'name']] = []

                    for _sub_vertex in _sub_vertices:

                        if _sub_vertex[r'name'] not in nodes:
                            vertices.append(_sub_vertex)

                        _nodes.append(_sub_vertex[r'name'])

        return nodes
