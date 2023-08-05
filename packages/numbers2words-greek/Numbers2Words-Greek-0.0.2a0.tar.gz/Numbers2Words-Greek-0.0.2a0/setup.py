# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['num2word_greek']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1']

entry_points = \
{'console_scripts': ['num2word_greek = num2word_greek.numbers2words:cmdline']}

setup_kwargs = {
    'name': 'numbers2words-greek',
    'version': '0.0.2a0',
    'description': 'Numbers2Words Greek',
    'long_description': '# Numbers2Words Greek\n\n[![PyPI](https://img.shields.io/pypi/v/Numbers2Words-Greek.svg)][pypi_]\n[![Status](https://img.shields.io/pypi/status/Numbers2Words-Greek.svg)][status]\n[![Python Version](https://img.shields.io/pypi/pyversions/Numbers2Words-Greek)][python version]\n[![License](https://img.shields.io/pypi/l/Numbers2Words-Greek)][license]\n\n[![Read the documentation at https://Numbers2Words-Greek.readthedocs.io/](https://img.shields.io/readthedocs/Numbers2Words-Greek/latest.svg?label=Read%20the%20Docs)][read the docs]\n[![Tests](https://github.com/geoph9/Numbers2Words-Greek/workflows/Tests/badge.svg)][tests]\n[![Codecov](https://codecov.io/gh/geoph9/Numbers2Words-Greek/branch/main/graph/badge.svg)][codecov]\n\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]\n\n[pypi_]: https://pypi.org/project/Numbers2Words-Greek/\n[status]: https://pypi.org/project/Numbers2Words-Greek/\n[python version]: https://pypi.org/project/Numbers2Words-Greek\n[read the docs]: https://Numbers2Words-Greek.readthedocs.io/\n[tests]: https://github.com/geoph9/Numbers2Words-Greek/actions?workflow=Tests\n[codecov]: https://app.codecov.io/gh/geoph9/Numbers2Words-Greek\n[pre-commit]: https://github.com/pre-commit/pre-commit\n[black]: https://github.com/psf/black\n\n## Features\n\n\nThis repository contains code for converting converting numbers \nto words (e.g. 10 -> δέκα) up until `10^13 - 1` (1 trillion minus one).\n\n- Convert numbers to greek words.\n- Support for ordinals.\n- Support for certain time formats.\n\n## Installation:\n\n\nYou can install _Numbers2Words Greek_ via [pip] from [PyPI]:\n\n```console\n$ pip install Numbers2Words-Greek\n```\n\nIf using `poetry`, then you can do `poetry add Numbers2Words-Greek`.\n\nTo install this repository locally, in editable mode, do the following:\n\n```\ngit clone https://github.com/geoph9/Numbers2Words-Greek.git\ncd Numbers2Words-Greek\npip install -e .\n```\n\nIf no error occurs then you are fine. To make sure, you may run: \n`python -c "import num2word"`.\n\n## Usage\n\n### The `numbers2words.py` script:\nThis script contains functionality to convert numbers to their\ncorresponding words in Greek. It only handles positive numbers \n(you can easily change it to handle negative ones) and can also \nhandle decimals (only if the decimal part is separated using "," \ninstead of ".") and hours (e.g. 2:30 -> δύο και μισή). It is \nimportant to note that this algorithm does not take into account \nthe gender of the noun following each number.\nAlso, the numbers will be converted as is and there is **no** \npost-processing like "2.5 ευρώ" -> "δυόμιση ευρώ" (the output \nwill be "δύο κόμμα πέντε ευρώ").\n\nIf you only need to convert numbers to words then you may use this \nscript as described below:\n\n`python -m num2word [--test-word <<WORD>>] [--path <<PATH>>] \n[--extension .lab] [--out-path]`\n\nArguments:\n- `-t` or `--test-word`: Use this only for testing. Put a word or \nnumber after it and check the result.\n  E.g. `python -m num2word -t 150` should print `εκατόν πενήντα`.\n\n- `-p` or `--path`: Provide a valid path. The path must be either a text file \nor a directory containing many files (the extension of these files is defined \nby the `-e` or `--extension` option, defaults to `.txt`). Cases:\n    1. *Directory*: Inside this directory there needs to be multiple \n    text files which you want to convert. The words inside the file will \n    not be change and only the numbers will be replaced by their \n    corresponding words.\n    2. *File*: If you provide a file then the same thing will happen but \n    just for this file.\n- `-e` or `--extension`: Use this to change the extension of the text \nfiles you have provided in `--path`. This only matters if you have \nprovided a directory. \n\nExample:\n\n```\n# num2word is the package and numbers2words.py is the script.\npython -m num2word --path /home/user/data/transcriptions \\\n                   --extension .txt\n```\n\nThe above will read all the `.txt` files inside the `transcriptions` \ndirectory and will change the numbers to their corresponding greek words.\n\n---\n\n## Future Work:\n\n1. Handle fractions in `numbers2words`. E.g. Convert "1/10" to "ένα δέκατο".\n2. Handle time input in `numbers2words`. E.g. Convert "11:20" to "έντεκα και είκοσι"\n\n\n## Contributing\n\nContributions are very welcome.\nTo learn more, see the [Contributor Guide].\n\n## License\n\nDistributed under the terms of the [MIT license][license],\n_Numbers2Words Greek_ is free and open source software.\n\n## Issues\n\nIf you encounter any problems,\nplease [file an issue] along with a detailed description.\n\n## Credits\n\nThis project was generated from [@cjolowicz]\'s [Hypermodern Python Cookiecutter] template.\n\n[@cjolowicz]: https://github.com/cjolowicz\n[pypi]: https://pypi.org/\n[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n[file an issue]: https://github.com/geoph9/Numbers2Words-Greek/issues\n[pip]: https://pip.pypa.io/\n\n<!-- github-only -->\n\n[license]: https://github.com/geoph9/Numbers2Words-Greek/blob/main/LICENSE\n[contributor guide]: https://github.com/geoph9/Numbers2Words-Greek/blob/main/CONTRIBUTING.md\n[command-line reference]: https://Numbers2Words-Greek.readthedocs.io/en/latest/usage.html\n',
    'author': 'Georgios K.',
    'author_email': 'geoph9@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/geoph9/Numbers2Words-Greek',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
