# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nwave', 'nwave.base', 'nwave.common', 'nwave.interlocked']

package_data = \
{'': ['*']}

install_requires = \
['SoundFile>=0.10.3,<0.11.0',
 'librosa>=0.9.2,<0.10.0',
 'numba>=0.55.2,<0.57.0',
 'samplerate>=0.1.0,<0.2.0',
 'soxr>=0.3.0,<0.4.0']

setup_kwargs = {
    'name': 'nwave',
    'version': '0.1.2',
    'description': 'Multithread batch resampling and waveform transforms',
    'long_description': '# nwave\n\n[![Build](https://github.com/ionite34/nwave/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/ionite34/nwave/actions/workflows/build.yml)\n[![codecov](https://codecov.io/gh/ionite34/nwave/branch/main/graph/badge.svg?token=ZXM5Y46XBI)](https://codecov.io/gh/ionite34/nwave)\n[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B31224%2Fgithub.com%2Fionite34%2Fnwave.svg?type=shield)](https://app.fossa.com/projects/custom%2B31224%2Fgithub.com%2Fionite34%2Fnwave?ref=badge_shield)\n\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nwave)\n[![PyPI version](https://badge.fury.io/py/nwave.svg)](https://pypi.org/project/nwave/)\n\n\nLow latency multi-thread audio transforms and conversions\n\n## Requirements\n```\nnumba ~= 0.55.2\nSoundFile ~= 0.10.3\nlibrosa ~= 0.9.2\nsamplerate >= 0.1.0\nsoxr >= 0.3.0\n```\n\n## License\nThe code in this project is released under the [MIT License](LICENSE).\n\n[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B31224%2Fgithub.com%2Fionite34%2Fnwave.svg?type=large)](https://app.fossa.com/projects/custom%2B31224%2Fgithub.com%2Fionite34%2Fnwave?ref=badge_large)\n',
    'author': 'ionite34',
    'author_email': 'dev@ionite.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ionite34/nwave',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.2,<3.11',
}


setup(**setup_kwargs)
