# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['incremental_tasks']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.2,<2.0.0']

entry_points = \
{'console_scripts': ['generate_tasks_cli = incremental_tasks.cli:main']}

setup_kwargs = {
    'name': 'incremental-tasks',
    'version': '0.1.3',
    'description': 'A benchmark of progressively more difficult AI tasks to measure learning speed of ML systems ',
    'long_description': '# Incremental tasks\n\n[![PyPI Version][pypi-image]][pypi-url]\n[![Incremental tasks CI](https://github.com/hugcis/incremental_tasks/actions/workflows/build.yml/badge.svg)](https://github.com/hugcis/incremental_tasks/actions/workflows/build.yml)\n[![][versions-image]][versions-url]\n\n<!-- Badges: -->\n\n[pypi-image]: https://img.shields.io/pypi/v/incremental_tasks\n[pypi-url]: https://pypi.org/project/incremental_tasks/\n[versions-image]: https://img.shields.io/pypi/pyversions/incremental_tasks/\n[versions-url]: https://pypi.org/project/incremental_tasks/\n\nThis is a modular and extendable benchmark of progressively more difficult AI tasks to measure learning speed of ML systems.\n\nThis repository contains the code to generate the incremental task dataset used\nin [[1]](#ref).\n    \n\n## Installation\n\nThis package can also be used as a library. Just install it from PyPI (ideally\nin a virtual env if you don\'t want the CLI command to pollute your path).\n\n```bash\npip install incremental_tasks\n```\nThis installs the library as well as an executable `generate_tasks_cli`\n\n## Task generation\n\nThe command `generate_tasks_cli` can be used to directly generate sequences from\nthe command line. They are printed to stdout and can be saved to a file to\nquickly create a dataset.\n\n\n## Interactive task solving\n\nA user can try the tasks by himself by running `generate_tasks_cli`. This will\nstart an interactive session that will show random examples from the tasks of\nthe benchmarks, starting from the easiest.\n\nOnce a task is solved, it switches to a new harder one.\n\nAn example interactive session:\n\n<pre><code>$ generate_tasks_cli  --interactive\n\n======================================================================\n0 1 1 0 0 0 1 1 0 1 1 0 0 0 1 1 0 1 1 <b  style="color:blue">{?} {?} {?} {?} {?}</b>\nType you answers (space separated) 0 0 0 1 1\nOK!\n0 1 1 0 0 0 1 1 0 1 1 0 0 0 1 1 0 1 1 <b style="color:green">0 0 0 1 1</b>\n\n======================================================================\n1 0 0 0 1 0 0 0 <b  style="color:blue">{?} {?} {?} {?} {?}</b>\nType you answers (space separated) 0 1 1 1 0\nWrong! right answer was:\n1 0 0 0 1 0 0 0 <b style="color:red">1 0 0 0 1</b>\n</code></pre>\n\nIn [[1]](#ref) the human evaluation score were computed using this interactive\ngame with the extra flag `--human-eval` which maps every token to a random one\nso the player doesn\'t have any prior knowledge about the text and needs to do\npattern matching like a neural network would.\n\n## Library\n\nYou can use the library in your own code to generate the data on the fly: \n\n``` python\nfrom incremental_tasks import ElementaryLanguageWithWorldDef\n\ntask = ElementaryLanguageWithWorldDef()\n```\nTo generate a single sentence from the task use `generate_single`:\n``` python\nprint(task.generate_single())\n# This will print ([\'I\', \'DO\', \'NOT\', \'SMELL\', \'PETER\', \'.\', \'DO\', \'I\', \'SMELL\', \'PETER\', \'?\', \'NO\'], [11])\n```\n\n\nTo generate `n` unique sequences (will be less than `n` if there aren\'t enough\navailable unique sequences): \n\n``` python\ntask.generate_tasks(max_n_seq=n)\n```\n\nA task can also create a generator that will yield an endless stream of\nsequences (not necessarily unique):\n``` python\ntask.generate_tasks_generator(max_n_seq=None)\n```\n\n### References\n\n- <a name="ref"></a>[1] Cisneros, H., Mikolov, T., & Sivic, J. (2022).\nBenchmarking Learning Efficiency in Deep Reservoir Computing. 1st Conference on\nLifelong Learning Agents, Montreal, Canada.\n \n',
    'author': 'hugcis',
    'author_email': 'hmj.cisneros@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
