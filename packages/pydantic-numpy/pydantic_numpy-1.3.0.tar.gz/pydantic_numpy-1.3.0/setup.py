# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydantic_numpy']

package_data = \
{'': ['*']}

install_requires = \
['numpy', 'pydantic']

setup_kwargs = {
    'name': 'pydantic-numpy',
    'version': '1.3.0',
    'description': 'Seamlessly integrate numpy arrays into pydantic models',
    'long_description': '[![Build Status](https://github.com/cheind/pydantic-numpy/actions/workflows/python-package.yml/badge.svg)](https://github.com/cheind/pydantic-numpy/actions/workflows/python-package.yml)\n\n# pydantic-numpy\nThis library provides support for integrating numpy `np.ndarray`\'s into pydantic models. \n\n## Usage\nFor more examples see [test_ndarray.py](./tests/test_ndarray.py)\n\n```python\nfrom pydantic import BaseModel\n\nimport pydantic_numpy.dtype as pnd\nfrom pydantic_numpy import NDArray, NDArrayFp32\n\n\nclass MyPydanticNumpyModel(BaseModel):\n    K: NDArray[pnd.float32]\n    C: NDArrayFp32  # <- Shorthand for same type as K\n\n\n# Instantiate from array\ncfg = MyPydanticNumpyModel(K=[1, 2])\n# Instantiate from numpy file\ncfg = MyPydanticNumpyModel(K={"path": "path_to/array.npy"})\n# Instantiate from npz file with key\ncfg = MyPydanticNumpyModel(K={"path": "path_to/array.npz", "key": "K"})\n\ncfg.K\n# np.ndarray[np.float32]\n```\n\n### Subfields\nThis package also comes with `pydantic_numpy.dtype`, which adds subtyping support such as `NDArray[pnd.float32]`. All subfields must be from this package as numpy dtypes have no [Pydantic support](https://pydantic-docs.helpmanual.io/usage/types/#generic-classes-as-types).\n\n\n## Install\n```shell\npip install pydantic-numpy\n```\n\n## History\nThe original idea originates from [this discussion](https://gist.github.com/danielhfrank/00e6b8556eed73fb4053450e602d2434), but stopped working for `numpy>=1.22`. This repository picks up where the previous discussion ended\n - added designated repository for better handling of PRs\n - added support for `numpy>1.22`\n - Dtypes are no longer strings but `np.generics`. I.e. `NDArray[\'np.float32\']` becomes `NDArray[np.float32]`\n - added automated tests and continuous integration for different numpy/python versions\n ',
    'author': 'Christoph Heindl, Can H. Tartanoglu',
    'author_email': 'canhtart@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
