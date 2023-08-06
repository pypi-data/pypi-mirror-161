# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cybergenetics',
 'cybergenetics.control',
 'cybergenetics.envs',
 'cybergenetics.envs.assets.crn',
 'cybergenetics.wrappers']

package_data = \
{'': ['*']}

install_requires = \
['gym>=0.21.0,<0.22.0',
 'imageio>=2.20.0,<3.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'torch>=1.12.0,<2.0.0']

entry_points = \
{'console_scripts': ['poetry = cybergenetics.cli:main']}

setup_kwargs = {
    'name': 'cybergenetics',
    'version': '0.0.4',
    'description': 'Cybergenetics is a controlled simulating environment for chemical reaction networks (CRNs) and co-cultures.',
    'long_description': "# Cybergenetics\n\nCybergenetics is a controlled simulating environment for chemical reaction networks (CRNs) and co-cultures.\n\n\n\nCybergenetics supports\n\n* OpenAI Gym API\n* `.py` configuration file\n\n\n\n## Installation\n\n```bash\npip install cybergenetics\n```\n\n\n\n## Quick Start\n\nWrite your own configuration file `config.py` under working directory.\n\n```python\n\nimport cybergenetics\n\nfrom config import configs\n\nenv = crn.make('CRN-v0', configs)\nenv.seed(42)\nenv.action_space.seed(42)\n\nobservation = env.reset()\n\nwhile True:\n    action = env.action_space.sample()\n    observation, reward, terminated, info = env.step(action)\n    if terminated:\n        break\n\nenv.close()\n```\n\n\n\n### Tutorial\n\n> * [Guide to Cybergenetics](https://colab.research.google.com/drive/1-tp5uV4ONEG8qzlEgtnrdxNNN_RLICSm?usp=sharing)\n\n\n\n## Contributing\n\n\n\n## License\n\nCybergenetics has an BSD-3-Clause license, as found in the [LICENSE](https://github.com/imyizhang/cybergenetics/blob/main/LICENSE) file.\n",
    'author': 'Yi Zhang, Quentin Badolle',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://cybergenetics.readthedocs.io/en/latest/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
