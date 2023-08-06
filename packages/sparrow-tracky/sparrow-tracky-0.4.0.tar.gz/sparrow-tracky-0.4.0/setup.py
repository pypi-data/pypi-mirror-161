# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sparrow_tracky', 'sparrow_tracky.deepsort', 'sparrow_tracky.metrics']

package_data = \
{'': ['*']}

install_requires = \
['scipy>=1.8,<2.0', 'sparrow-datums>=0.8.1,<0.9.0']

setup_kwargs = {
    'name': 'sparrow-tracky',
    'version': '0.4.0',
    'description': 'Object tracking and metrics',
    'long_description': '# Sparrow Tracky\n\nSparrow Tracky is a Python package that implements basic object tracking and related metrics. The object tracking algorithm is a simplification of SORT and is designed for prototyping in Python -- not for production. The metrics Multi-Object Detection Accuracy (MODA) and Multi-Object Tracking Accuracy (MOTA) are useful for measuring the quality of box predictions.\n\n# Quick Start Example\n\n## Installation\n\n```bash\npip install -U sparrow-tracky\n```\n\n## Measuring MODA on frame boxes\n\n```python\nimport numpy as np\nfrom sparrow_datums import FrameBoxes, PType\nfrom sparrow_tracky import compute_moda\n\nboxes = FrameBoxes(np.ones((4, 4)), PType.absolute_tlwh)\nmoda = compute_moda(boxes, boxes + 0.1)\nmoda\n\n# Expected result\n# MODA(false_negatives=0, false_positives=0, n_truth=4)\n\nmoda.value\n\n# Expected result\n# 1.0\n```\n\n## Adding MODA objects\n\n```python\nmoda + moda\n\n# Expected result\n# MODA(false_negatives=0, false_positives=0, n_truth=8)\n\n(moda + moda).value\n\n# Expected result\n# 1.0\n```',
    'author': 'Sparrow Computing',
    'author_email': 'ben@sparrow.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sparrowml/sparrow-tracky',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
