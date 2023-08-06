from __future__ import annotations

import copy

from functools import partial
from typing import Set
from typing import TypeVar
from typing import Union

import networkx as nx
import numpy as np


T_Graph = TypeVar("T_Graph", bound=nx.Graph)  # T_Graph = Type[nx.Graph]


def apply_potentially_inplace(obj, fn_inplace):
    _obj = fn_inplace(obj)
    if _obj is not None:
        obj = _obj
    return obj


def get_unused_vertices_and_relabel(
    graph: T_Graph, n_new_vertices: int = 1
) -> Set[int]:
    assert n_new_vertices > 0
    vertex_new_lower_bound = len(graph.nodes)
    if graph.has_node(vertex_new_lower_bound):
        nx.relabel_nodes(
            graph, {name: ix for ix, name in enumerate(graph.nodes)}, copy=False
        )
    return np.arange(vertex_new_lower_bound, vertex_new_lower_bound + n_new_vertices)


def pass_param_or_call(
    param: Union[int, float, callable], graph: T_Graph
) -> Union[int, float]:
    if callable(param):
        param = param(graph)
    return param


def sampler_random_uniform(candidates: Union[int, str], min: int, max: int):
    if len(candidates) == 0:
        return set()

    if min > len(candidates):
        raise ValueError(
            f"Can not sample from a candidate list of size {len(candidates)} which is smaller than the given minimum {min}"
        )
    if max is None:
        max = len(candidates)
    elif max < min:
        raise ValueError(
            f"Minimum {min} is larger than given maximum {max} for range [{min},{max}]."
        )
    size = np.random.randint(
        min, np.maximum(np.minimum(max + 1, len(candidates)), min + 1)
    )
    return np.random.choice(list(candidates), size, replace=False)


class GraphOperation(object):
    def applicable(self, graph: T_Graph) -> bool:
        raise NotImplementedError()

    def forward(self, graph: T_Graph, inplace: bool = False) -> T_Graph:
        assert graph is not None
        if not inplace:
            graph = copy.deepcopy(graph)
        return apply_potentially_inplace(graph, self.forward_inplace)

    def forward_inplace(self, graph: T_Graph) -> T_Graph:
        raise NotImplementedError()

    def backward(
        self, graph: T_Graph, inplace: bool = False, return_fuzzy: bool = False
    ) -> Union[T_Graph, Set[T_Graph]]:
        assert graph is not None
        if not inplace:
            graph = copy.deepcopy(graph)

        return apply_potentially_inplace(
            graph, partial(self.backward_inplace, return_fuzzy=return_fuzzy)
        )

    def backward_inplace(
        self, graph: T_Graph, return_fuzzy: bool = False
    ) -> Union[T_Graph, Set[T_Graph]]:
        raise NotImplementedError()


class Selector(object):
    def __init__(self, min: int, max: int = None, sampler=sampler_random_uniform):
        self._sampler = sampler
        self._sample_min = min
        self._sample_max = max

    def forward_suggest(self, graph: T_Graph) -> Set[Union[int, str]]:
        raise NotImplementedError("Concrete selectors need to implement this method.")

    def forward_sample(self, graph: T_Graph) -> Union[int, str]:
        return self._sampler(
            self.forward_suggest(graph),
            min=pass_param_or_call(self._sample_min, graph),
            max=pass_param_or_call(self._sample_max, graph),
        )


class VertexSelector(Selector):
    def forward_suggest(self, graph: T_Graph) -> Set[Union[int, str]]:
        raise NotImplementedError(
            "Concrete vertex selectors need to implement this method."
        )


class RandomVertexSelector(VertexSelector):
    def forward_suggest(self, graph: T_Graph) -> Set[Union[int, str]]:
        return set(graph.nodes)


class VertexDegreeSelector(VertexSelector):
    def __init__(
        self,
        descending: bool = True,
        limit: int = 3,
        min: int = 1,
        max: int = None,
        min_degree: int = None,
        max_degree: int = None,
        sampler=sampler_random_uniform,
    ):
        super().__init__(sampler=sampler, min=min, max=max)
        self._descending = descending
        self._min_degree = min_degree
        self._max_degree = max_degree
        self._limit = limit if limit is not None else None

    def forward_suggest(self, graph: T_Graph) -> Set[Union[int, str]]:
        limit = pass_param_or_call(self._limit, graph)
        min_degree = pass_param_or_call(self._min_degree, graph)
        max_degree = pass_param_or_call(self._max_degree, graph)

        degree_vertices = [
            (v, d)
            for v, d in graph.degree()
            if (min_degree is None or min_degree is not None and d >= min_degree)
            and (max_degree is None or max_degree is not None and d <= max_degree)
        ]
        order_vertices = [
            v
            for (v, d) in sorted(
                degree_vertices, key=lambda tup: tup[1], reverse=self._descending
            )
        ]
        return order_vertices if limit is None else order_vertices[:limit]


class RandomEdgeSelector(Selector):
    def __init__(
        self,
        min: Union[int, callable],
        max: Union[int, callable] = None,
        sampler=sampler_random_uniform,
    ):
        super().__init__(sampler=sampler, min=min, max=max)
        self._sampler = sampler
        self._sample_min = min
        self._sample_max = max

    def forward_suggest(self, graph: T_Graph) -> Set[Union[int, str]]:
        return set(graph.edges)
