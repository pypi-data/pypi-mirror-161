# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dynnode2vec']

package_data = \
{'': ['*']}

install_requires = \
['chardet>=5.0.0,<6.0.0',
 'gensim>=4.2.0,<5.0.0',
 'networkx>=2.8.5,<3.0.0',
 'numpy>=1.23.1,<2.0.0',
 'stellargraph>=1.2.1,<2.0.0']

setup_kwargs = {
    'name': 'dynnode2vec',
    'version': '0.2.0',
    'description': 'dynnode2vec is a package to embed dynamic graphs',
    'long_description': '# dynnode2vec\n\n<div align="center">\n\n[![Python Version](https://img.shields.io/pypi/pyversions/dynnode2vec.svg)](https://pypi.org/project/dynnode2vec/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/pedugnat/dynnode2vec/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)\n![Coverage Report](assets/images/coverage.svg)\n\n</div>\n\n<h4>\n\n`dynnode2vec` is a package to embed dynamic graphs. \n\nIt is the python implementation of [S. Mahdavi, S. Khoshraftar, A. An: dynnode2vec: Scalable Dynamic Network Embedding. IEEE BigData 2018](http://www.cs.yorku.ca/~aan/research/paper/dynnode2vec.pdf)\n\n</h4>\n\n## Installation\n\n```bash\npip install -U dynnode2vec\n```\n\n## Usage\n\n```python\nimport pickle\n\nfrom dynnode2vec.dynnode2vec import DynNode2Vec\nfrom dynnode2vec.utils import generate_dynamic_graphs\n\n# Create random graphs\ngraphs = generate_dynamic_graphs(\n  n_base_nodes=100, n_steps=50, base_density=0.05\n)\n\n# Instantiate dynnode2vec object\ndynnode2vec = DynNode2Vec(\n    p=1., \n    q=1., \n    walk_length=10, \n    n_walks_per_node=20, \n    embedding_size=64\n)\n\n# Embed the dynamic graphs\nembeddings = dynnode2vec.compute_embeddings(graphs)\n\n# Save embeddings to disk\nwith open(\'example_embeddings.pkl\', \'wb\') as f:\n    pickle.dump(embeddings, f)\n```\n\n## Parameters\n- `DynNode2Vec` class:\n  - `p`: Return hyper parameter (default: 1)\n  - `q`: Inout parameter (default: 1)\n  - `walk_length`: Number of nodes in each walk (default: 80)\n  - `n_walks_per_node`: Number of walks per node (default: 10)\n  - `embedding_size`: Embedding dimensions (default: 128)\n  - `seed`: Number of workers for parallel execution (default: 1)\n  - `parallel_processes`: Number of workers for parallel execution (default: 1)\n  - `use_delta_nodes`: Number of workers for parallel execution (default: 1)\n\n- `DynNode2Vec.fit` method:\n  - `graphs`: list of nx.Graph (ordered by time)\n\n## TO DO \n- [x] remove pandas use in embeddings formatting\n- [ ] code examples of synthetic and real-life uses\n- [ ] get rid of Stellar Graph dependency\n\n\n## Releases\n\nYou can see the list of available releases on the [GitHub Releases](https://github.com/pedugnat/dynnode2vec/releases) page.\n\n## License\n\nThis project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/pedugnat/dynnode2vec/blob/master/LICENSE) for more details.\n\n## Citation\n\n```bibtex\n@misc{dynnode2vec,\n  author = {Paul-Emile Dugnat},\n  title = {dynnode2vec, a package to embed dynamic graphs},\n  year = {2022},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {\\url{https://github.com/pedugnat/dynnode2vec}}\n}\n```\n\nThis project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)\n',
    'author': 'pedugnat',
    'author_email': ' ',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pedugnat/dynnode2vec',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.9.0',
}


setup(**setup_kwargs)
