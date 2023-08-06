# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from typing import List, Tuple, Dict
from igraph import Graph, Vertex, VertexSeq, Edge, EdgeSeq


class DiTree:

    def __init__(self, graph: Graph, vertex: Vertex):

        self._graph = graph

        self._steps = [[vertex]]
        self._nodes = {}

    @property
    def steps(self) -> List[List[Vertex]]:

        return self._steps

    @property
    def nodes(self) -> Dict[str, List[Vertex]]:

        return self._nodes

    def find_in(self) -> Dict[str, List[Vertex]]:

        pre_step = self._steps[-1]

        if not pre_step:
            return None

        nodes = {}
        vertices = []

        for vertex in pre_step:

            _vertices = vertex.predecessors()

            if _vertices:

                _nodes = nodes[vertex[r'name']] = []

                for _v in _vertices:

                    if _v[r'name'] not in self._nodes:
                        vertices.append(_v)

                    _nodes.append(_v[r'name'])

        if nodes:
            self._nodes.update(nodes)

        self._steps.append(vertices)

        return nodes

    def find_out(self) -> Dict[str, List[Vertex]]:

        pre_step = self._steps[-1]

        if not pre_step:
            return None

        nodes = {}
        vertices = []

        for vertex in pre_step:

            _vertices = vertex.successors()

            if _vertices:

                _nodes = nodes[vertex[r'name']] = []

                for _v in _vertices:

                    if _v[r'name'] not in self._nodes:
                        vertices.append(_v)

                    _nodes.append(_v[r'name'])

        if nodes:
            self._nodes.update(nodes)

        self._steps.append(vertices)

        return nodes


class DiGraph:

    def __init__(self, name: str):

        self._name = name

        self._graph = Graph(directed=True)
        self._vertices = {}

    def __len__(self):

        return len(self._vertices)

    def __repr__(self):

        return f'<DiGraph: {self._name}, vertices: {self._graph.vcount()}, edges: {self._graph.ecount()}>'

    @property
    def name(self) -> str:

        return self._name

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

        return [edge for edge in source.out_edges() if edge.target == target.index]

    def add_edge(self, source: Vertex, target: Vertex) -> Edge:

        edges = self.find_edges(source, target)

        if edges:
            return edges[0]
        else:
            return self._graph.add_edge(source, target)

    def del_edges(self, source: Vertex, target: Vertex):

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

    def tree(self, name: str) -> DiTree:

        vertex = self.find_vertex(name)

        if vertex is None:
            return None

        return DiTree(self._graph, vertex)
