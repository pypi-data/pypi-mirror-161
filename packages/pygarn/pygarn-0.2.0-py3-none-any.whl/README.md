# pygarn [![PyPI version](https://badge.fury.io/py/pygarn.svg)](https://badge.fury.io/py/pygarn) ![Tests](https://github.com/innvariant/pygarn/workflows/Tests/badge.svg) [![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/) [![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/) [![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
Forward- and backward operations on graphs with a lot of fuzzyness.

![Example of a forward and backward operation on a graph.](res/pygarn-example-operation.png)

Install via
- **pip**: ``pip install pygarn``
- **poetry**: ``poetry add pygarn``
- or add in your **conda** environment:
```yaml
name: sur-your-env-name
channels:
- defaults
dependencies:
- python>=3.8
- pip
- pip:
  - pygarn
```

# Visuals
![](res/pygarn-example-non-invertible.png)
![](res/pygarn-example-operation-fuzzy.png)
![](res/pygarn-example-forward-backward-fuzzy.png)

# Examples
```python
import networkx as nx
from pygarn.base import RandomVertexSelector
from pygarn.growth import AddCompleteGraph

n_vertices_initial = 20
g_initial = nx.erdos_renyi_graph(n_vertices_initial, 0.3)

op_add_kcomplete = AddCompleteGraph(
    size=3,
    sources=RandomVertexSelector(min=1, max=3),
    targets=RandomVertexSelector(min=1, max=3),
)

g_new = op_add_kcomplete.forward(g_initial)

g_orig = op_add_kcomplete.backward(g_new)

# Should be highly likely:
assert nx.is_isomorphic(g_orig, g_initial)
```

```python
import networkx as nx
from pygarn.base import VertexDegreeSelector
from pygarn.growth import AddVertex

n_vertices_initial = 20
g_initial = nx.erdos_renyi_graph(n_vertices_initial, 0.3)
n_edges_initial = len(g_initial.edges)
degrees_initial = [(v, d) for v, d in g_initial.degree()]

selector = VertexDegreeSelector()
op_add = AddVertex()
n_rounds = 5

g_current = g_initial.copy()
for _ in range(n_rounds):
    g_current = op_add.forward(g_current)

```
