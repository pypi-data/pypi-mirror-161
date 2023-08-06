# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pygarn']

package_data = \
{'': ['*']}

install_requires = \
['networkx>=2.7.1,<3.0.0']

setup_kwargs = {
    'name': 'pygarn',
    'version': '0.2.0',
    'description': '',
    'long_description': '# pygarn [![PyPI version](https://badge.fury.io/py/pygarn.svg)](https://badge.fury.io/py/pygarn) ![Tests](https://github.com/innvariant/pygarn/workflows/Tests/badge.svg) [![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/) [![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/) [![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)\nForward- and backward operations on graphs with a lot of fuzzyness.\n\n![Example of a forward and backward operation on a graph.](res/pygarn-example-operation.png)\n\nInstall via\n- **pip**: ``pip install pygarn``\n- **poetry**: ``poetry add pygarn``\n- or add in your **conda** environment:\n```yaml\nname: sur-your-env-name\nchannels:\n- defaults\ndependencies:\n- python>=3.8\n- pip\n- pip:\n  - pygarn\n```\n\n# Visuals\n![](res/pygarn-example-non-invertible.png)\n![](res/pygarn-example-operation-fuzzy.png)\n![](res/pygarn-example-forward-backward-fuzzy.png)\n\n# Examples\n```python\nimport networkx as nx\nfrom pygarn.base import RandomVertexSelector\nfrom pygarn.growth import AddCompleteGraph\n\nn_vertices_initial = 20\ng_initial = nx.erdos_renyi_graph(n_vertices_initial, 0.3)\n\nop_add_kcomplete = AddCompleteGraph(\n    size=3,\n    sources=RandomVertexSelector(min=1, max=3),\n    targets=RandomVertexSelector(min=1, max=3),\n)\n\ng_new = op_add_kcomplete.forward(g_initial)\n\ng_orig = op_add_kcomplete.backward(g_new)\n\n# Should be highly likely:\nassert nx.is_isomorphic(g_orig, g_initial)\n```\n\n```python\nimport networkx as nx\nfrom pygarn.base import VertexDegreeSelector\nfrom pygarn.growth import AddVertex\n\nn_vertices_initial = 20\ng_initial = nx.erdos_renyi_graph(n_vertices_initial, 0.3)\nn_edges_initial = len(g_initial.edges)\ndegrees_initial = [(v, d) for v, d in g_initial.degree()]\n\nselector = VertexDegreeSelector()\nop_add = AddVertex()\nn_rounds = 5\n\ng_current = g_initial.copy()\nfor _ in range(n_rounds):\n    g_current = op_add.forward(g_current)\n\n```\n',
    'author': 'Julian Stier',
    'author_email': 'julian.stier@uni-passau.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/innvariant/pygarn',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
