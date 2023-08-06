from collections import Counter
from typing import Set
from typing import TypeVar
from typing import Union

import networkx as nx
import numpy as np

from pygarn.base import GraphOperation
from pygarn.base import RandomVertexSelector
from pygarn.base import VertexSelector
from pygarn.base import get_unused_vertices_and_relabel


T_Graph = TypeVar("T_Graph", bound=nx.Graph)  # T_Graph = Type[nx.Graph]


class RemoveVertex(GraphOperation):
    def __init__(self, selector: VertexSelector = RandomVertexSelector(min=1, max=1)):
        self._selector = selector

    def applicable(self, graph: T_Graph) -> bool:
        return graph is not None and len(graph.nodes) > 0

    def forward_inplace(self, graph: T_Graph) -> T_Graph:
        vertices = self._selector.forward_sample(graph)
        graph.remove_nodes_from(vertices)

    def backward_inplace(
        self, graph: T_Graph, return_fuzzy: bool = False
    ) -> Union[T_Graph, Set[T_Graph]]:
        guess_n_removed_vertices = np.random.randint(
            self._selector._sample_min, self._selector._sample_max + 1
        )
        vertices_new = get_unused_vertices_and_relabel(
            graph, n_new_vertices=guess_n_removed_vertices
        )
        edges_new = []

        if len(graph.nodes) < 1:
            graph.add_nodes_from(vertices_new)
            return

        # TODO add edges based on some heuristic
        degree = [d for v, d in graph.degree()] + [1]
        degree_counts = Counter(degree)
        degree_max = np.max(degree)
        degree_hist = [
            (d, degree_counts[d]) for d in np.arange(1, degree_max + 1)
        ]  # explicitly enforce at least one edge
        if len(degree_hist) < 3:
            count_total = np.sum([c for _, c in degree_hist])
            probs = [c / count_total for d, c in degree_hist]
            edges_per_vertex = np.random.choice(
                [d for d, c in degree_hist],
                size=len(vertices_new),
                p=probs,
                replace=True,
            )
            for v, num_edges in zip(vertices_new, edges_per_vertex):
                targets = np.random.choice(
                    list(set(graph.nodes) - {v}), size=num_edges, replace=False
                )
                edges_new = [(v, t) for t in targets]

        graph.add_nodes_from(vertices_new)
        graph.add_edges_from(edges_new)


class VertexContraction(GraphOperation):
    def __init__(self, selector: VertexSelector = RandomVertexSelector(min=1, max=1)):
        self._selector = selector

    def applicable(self, graph: T_Graph) -> bool:
        return graph is not None and len(graph.nodes) > 1

    def forward_inplace(self, graph: T_Graph) -> T_Graph:
        # vertices = self._selector.forward_sample(graph)
        raise NotImplementedError()

    def backward_inplace(
        self, graph: T_Graph, return_fuzzy: bool = False
    ) -> Union[T_Graph, Set[T_Graph]]:
        raise NotImplementedError()
