# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gokart', 'gokart.slack', 'gokart.testing', 'gokart.tree']

package_data = \
{'': ['*']}

install_requires = \
['APScheduler',
 'boto3',
 'google-api-python-client',
 'google-auth',
 'luigi',
 'matplotlib',
 'numpy',
 'pandas',
 'pyarrow',
 'redis',
 'slack-sdk>=3,<4',
 'tqdm',
 'uritemplate']

setup_kwargs = {
    'name': 'gokart',
    'version': '1.2.0',
    'description': 'Gokart solves reproducibility, task dependencies, constraints of good code, and ease of use for Machine Learning Pipeline. [Documentation](https://gokart.readthedocs.io/en/latest/)',
    'long_description': '# gokart\n\n<p align="center">\n  <img src="https://raw.githubusercontent.com/m3dev/gokart/master/docs/gokart_logo_side_isolation.svg" width="90%">\n<p>\n\n[![Test](https://github.com/m3dev/gokart/workflows/Test/badge.svg)](https://github.com/m3dev/gokart/actions?query=workflow%3ATest)\n[![](https://readthedocs.org/projects/gokart/badge/?version=latest)](https://gokart.readthedocs.io/en/latest/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/gokart.svg)](https://pypi.org/project/gokart/)\n[![](https://img.shields.io/pypi/v/gokart)](https://pypi.org/project/gokart/)\n![](https://img.shields.io/pypi/l/gokart)\n\nGokart solves reproducibility, task dependencies, constraints of good code, and ease of use for Machine Learning Pipeline.\n\n\n[Documentation](https://gokart.readthedocs.io/en/latest/) for the latest release is hosted on readthedocs.\n\n\n# About gokart\n\nHere are some good things about gokart.\n\n- The following meta data for each Task is stored separately in a `pkl` file with hash value\n    - task output data\n    - imported all module versions\n    - task processing time\n    - random seed in task\n    - displayed log\n    - all parameters set as class variables in the task\n- Automatically rerun the pipeline if parameters of Tasks are changed.\n- Support GCS and S3 as a data store for intermediate results of Tasks in the pipeline.\n- The above output is exchanged between tasks as an intermediate file, which is memory-friendly\n- `pandas.DataFrame` type and column checking during I/O\n- Directory structure of saved files is automatically determined from structure of script\n- Seeds for numpy and random are automatically fixed\n- Can code while adhering to [SOLID](https://en.wikipedia.org/wiki/SOLID) principles as much as possible\n- Tasks are locked via redis even if they run in parallel\n\n**All the functions above are created for constructing Machine Learning batches. Provides an excellent environment for reproducibility and team development.**\n\n\nHere are some non-goal / downside of the gokart.\n- Batch execution in parallel is supported, but parallel and concurrent execution of task in memory.\n- Gokart is focused on reproducibility. So, I/O and capacity of data storage can become a bottleneck.\n- No support for task visualize.\n- Gokart is not an experiment management tool. The management of the execution result is cut out as [Thunderbolt](https://github.com/m3dev/thunderbolt).\n- Gokart does not recommend writing pipelines in toml, yaml, json, and more. Gokart is preferring to write them in Python.\n\n# Getting Started\n\nWithin the activated Python environment, use the following command to install gokart.\n\n```\npip install gokart\n```\n\n\n# Quickstart\n\nA minimal gokart tasks looks something like this:\n\n\n```python\nimport gokart\n\nclass Example(gokart.TaskOnKart):\n    def run(self):\n        self.dump(\'Hello, world!\')\n\ntask = Example()\noutput = gokart.build(task)\nprint(output)\n```\n\n`gokart.build` return the result of dump by `gokart.TaskOnKart`. The example will output the following.\n\n\n```\nHello, world!\n```\n\n\nThis is an introduction to some of the gokart.\nThere are still more useful features.\n\nPlease See [Documentation](https://gokart.readthedocs.io/en/latest/) .\n\nHave a good gokart life.\n\n# Achievements\n\nGokart is a proven product.\n\n- It\'s actually been used by [m3.inc](https://corporate.m3.com/en) for over 3 years\n- Natural Language Processing Competition by [Nishika.inc](https://nishika.com) 2nd prize : [Solution Repository](https://github.com/vaaaaanquish/nishika_akutagawa_2nd_prize)\n\n\n# Thanks\n\ngokart is a wrapper for luigi. Thanks to luigi and dependent projects!\n\n- [luigi](https://github.com/spotify/luigi)\n',
    'author': 'M3, inc.',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/m3dev/gokart',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
