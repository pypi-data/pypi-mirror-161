# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['slippers', 'slippers.templatetags']

package_data = \
{'': ['*']}

install_requires = \
['Django>=2.2,<4.2', 'PyYAML>=5.4.0,<7.0.0']

setup_kwargs = {
    'name': 'slippers',
    'version': '0.3.2',
    'description': 'Build reusable components in Django without writing a single line of Python.',
    'long_description': '[![Slippers](https://mitchel.me/slippers/img/slippers.svg)](https://github.com/mixxorz/slippers)\n\n---\n\n[![PyPI version](https://badge.fury.io/py/slippers.svg)](https://badge.fury.io/py/slippers)\n[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/slippers.svg)](https://pypi.python.org/pypi/slippers/)\n[![PyPI Supported Django Versions](https://img.shields.io/pypi/djversions/slippers.svg)](https://docs.djangoproject.com/en/dev/releases/)\n[![GitHub Actions (Code quality and tests)](https://github.com/mixxorz/slippers/workflows/Code%20quality%20and%20tests/badge.svg)](https://github.com/mixxorz/slippers)\n\nBuild reusable components in Django without writing a single line of Python.\n\n```django\n{% #quote %}\n  {% quote_photo src="/project-hail-mary.jpg" %}\n\n  {% #quote_text %}\n    “I penetrated the outer cell membrane with a nanosyringe."\n    "You poked it with a stick?"\n    "No!" I said. "Well. Yes. But it was a scientific poke\n    with a very scientific stick.”\n  {% /quote_text %}\n\n  {% #quote_attribution %}\n    Andy Weir, Project Hail Mary\n  {% /quote_attribution %}\n{% /quote %}\n```\n\n## What is Slippers?\n\nThe Django Template Language is awesome. It\'s fast, rich in features, and overall pretty great to work with.\n\nSlippers aims to augment DTL, adding just enough functionality to make building interfaces just that bit more _comfortable_.\n\nIt includes additional template tags and filters, but its headline feature is **reusable components**.\n\n```django\n{% #button variant="primary" %}See how it works{% /button %}\n```\n\n[See how it works](https://mitchel.me/slippers/docs/getting-started/)\n\n## Installation\n\n```\npip install slippers\n```\n\nAdd it to your `INSTALLED_APPS`:\n\n```python\nINSTALLED_APPS = [\n    ...\n    \'slippers\',\n    ...\n]\n```\n\n## Documentation\n\nFull documentation can be found on the [Slippers documentation site](https://mitchel.me/slippers/).\n\n## Contributors\n\n[![Contributors](https://contrib.rocks/image?repo=mixxorz/slippers)](https://github.com/mixxorz/slippers/graphs/contributors)\n\n## License\n\nMIT\n',
    'author': 'Mitchel Cabuloy',
    'author_email': 'mixxorz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mixxorz/slippers',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
