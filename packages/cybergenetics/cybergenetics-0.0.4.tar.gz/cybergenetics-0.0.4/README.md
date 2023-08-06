# Cybergenetics

Cybergenetics is a controlled simulating environment for chemical reaction networks (CRNs) and co-cultures.



Cybergenetics supports

* OpenAI Gym API
* `.py` configuration file



## Installation

```bash
pip install cybergenetics
```



## Quick Start

Write your own configuration file `config.py` under working directory.

```python

import cybergenetics

from config import configs

env = crn.make('CRN-v0', configs)
env.seed(42)
env.action_space.seed(42)

observation = env.reset()

while True:
    action = env.action_space.sample()
    observation, reward, terminated, info = env.step(action)
    if terminated:
        break

env.close()
```



### Tutorial

> * [Guide to Cybergenetics](https://colab.research.google.com/drive/1-tp5uV4ONEG8qzlEgtnrdxNNN_RLICSm?usp=sharing)



## Contributing



## License

Cybergenetics has an BSD-3-Clause license, as found in the [LICENSE](https://github.com/imyizhang/cybergenetics/blob/main/LICENSE) file.
