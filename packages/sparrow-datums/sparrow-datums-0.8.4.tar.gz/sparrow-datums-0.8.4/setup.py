# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sparrow_datums',
 'sparrow_datums.boxes',
 'sparrow_datums.stream',
 'sparrow_datums.tracking']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.20.0,<2.0.0', 'rich>=10.14.0,<11.0.0', 'typer[all]>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'sparrow-datums',
    'version': '0.8.4',
    'description': 'A Python package for data structures',
    'long_description': '# Sparrow Datums\n\nSparrow Datums is a Python package for vision AI data structures, related operations and serialization/deserialization.\nSpecifically, it makes it easier to work with bounding boxes, key points (TODO), and segmentation masks (TODO).\nIt supports individual objects, frames of objects, multiple frames of objects, objects augmented with class labels and confidence scores, and more.\n\nSparrow Datums also supports object tracking where the identity of the object is maintained. And that data\ncan be streamed instead of keeping it all in a single file.\n\n# Quick Start Example\n\n## Installation\n\n```bash\npip install -U sparrow-datums\n```\n\n## Switching between box parameterizations\n\n```python\nimport numpy as np\nfrom sparrow_datums import FrameBoxes, PType\n\nboxes = FrameBoxes(np.ones((4, 4)), PType.absolute_tlwh)\nboxes.to_tlbr()\n\n# Expected result\n# FrameBoxes([[1., 1., 2., 2.],\n#             [1., 1., 2., 2.],\n#             [1., 1., 2., 2.],\n#             [1., 1., 2., 2.]])\n```\n\n## Slicing\n\nNotice that all "chunk" objects override basic NumPy arrays. This means that some filtering operations work as expected:\n\n```python\nboxes[:2]\n\n# Expected result\n# FrameBoxes([[1., 1., 1., 1.],\n#             [1., 1., 1., 1.]])\n```\n\nBut sub-types do their own validation. For example, `FrameBoxes` must be a `(n, 4)` array. Therefore, selecting a single column throws an error:\n\n```python\nboxes[:, 0]\n\n# Expected exception\n# ValueError: A frame boxes object must be a 2D array\n```\n\nInstead, chunks expose different subsets of the data as properties. For example, you can get the `x` coordinate as an array:\n\n```python\nboxes.x\n\n# Expected result\n# array([1., 1., 1., 1.])\n```\n\nOr the width of the boxes:\n\n```python\nboxes.w\n\n# Expected result\n# array([1., 1., 1., 1.])\n```\n\nIf you need to access the raw data, you can do that with a chunk\'s `array` property:\n\n```python\nboxes.array[0, 0]\n\n# Expected result\n# 1.0\n```\n\n## Operations\n\nSparrow Datums comes with common operations for data types. For example, you can compute the pairwise IoU of two sets of `FrameBoxes`:\n\n```python\nfrom sparrow_datums import pairwise_iou\n\npairwise_iou(boxes, boxes + 0.1)\n\n# array([[0.57857143, 0.57857143, 0.57857143, 0.57857143],\n#        [0.57857143, 0.57857143, 0.57857143, 0.57857143],\n#        [0.57857143, 0.57857143, 0.57857143, 0.57857143],\n#        [0.57857143, 0.57857143, 0.57857143, 0.57857143]])\n```',
    'author': 'Sparrow Computing',
    'author_email': 'ben@sparrow.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sparrowml/sparrow-datums',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
