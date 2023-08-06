# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['plagdef', 'plagdef.gui', 'plagdef.model', 'plagdef.model.pipeline']

package_data = \
{'': ['*'], 'plagdef': ['config/*'], 'plagdef.gui': ['res/*', 'ui/*']}

install_requires = \
['Werkzeug>=2.2,<3.0',
 'beautifulsoup4>=4.10,<5.0',
 'click>=8.1,<9.0',
 'deep-translator>=1.7,<2.0',
 'jsonpickle>=2.2,<3.0',
 'langdetect>=1.0,<2.0',
 'networkx>=2.7,<3.0',
 'numpy>=1.22,<2.0',
 'ocrmypdf>=13.7,<14.0',
 'pdfplumber>=0.6,<0.7',
 'pyside6',
 'python-magic>=0.4,<0.5',
 'sortedcontainers>=2.4,<3.0',
 'stanza>=1.4,<2.0',
 'tqdm>=4.63,<5.0',
 'urlextract>=1.6,<2.0']

entry_points = \
{'console_scripts': ['plagdef = plagdef.app:cli',
                     'plagdef-gui = plagdef.app:gui']}

setup_kwargs = {
    'name': 'plagdef',
    'version': '1.4.11',
    'description': 'A tool which makes life hard for students who try to make theirs simple.',
    'long_description': "# PlagDef\n\n[![PyPI version](https://badge.fury.io/py/plagdef.svg)](https://badge.fury.io/py/plagdef)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/plagdef)\n![GitHub](https://img.shields.io/github/license/devWhyqueue/plagdef)\n[![Test](https://github.com/devWhyqueue/plagdef/actions/workflows/cd.yml/badge.svg)](https://github.com/devWhyqueue/plagdef/actions/workflows/test.yml)\n[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=devWhyqueue_plagdef&metric=coverage)](https://sonarcloud.io/dashboard?id=devWhyqueue_plagdef)\n\nA tool which makes life hard for students who try to make theirs simple.\n\n# Installation\n\nGet it from PyPI:\n\n```\n$ pip install plagdef\n````\n\nOr build it yourself:\n\n```\n$ git clone git://github.com/devWhyqueue/plagdef\n$ poetry build\n$ pip install dist/plagdef-{VERSION}.tar.gz\n````\n\n# Requirements\n\n## OCRMyPDF\n\nThis library is used for improved PDF text extraction.\\\nTo install its necessary dependencies for your operating system take a look at:\\\nhttps://ocrmypdf.readthedocs.io/en/latest/installation.html\n\nAnd don't forget to download the German language pack to your _tessdata_ folder from here:\\\nhttps://github.com/tesseract-ocr/tessdata\n\n## Libmagic\n\n**After** (important!) you installed PlagDef, install the libmagic library.\\\nPlagDef uses it to detect character encodings.\\\nFurther instructions can be found here:\\\nhttps://github.com/ahupp/python-magic#installation\n\n# Usage\n\nRun the GUI:\n\n```\n$ plagdef-gui\n````\n\nOr if you prefer a CLI:\n\n```\n$ plagdef -h\n````\n\n# Development\n\nClone the repo and install dependencies:\n\n```\n$ git clone git://github.com/devWhyqueue/plagdef\n$ poetry install\n````\n\n# Publish to PyPI\n\nIn your virtual environment build and upload PlagDef:\n\n```\n$ poetry publish --build\n````\n",
    'author': 'Yannik Queisler',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/devWhyqueue/plagdef',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
