# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vysion', 'vysion.client', 'vysion.model', 'vysion.taxonomy']

package_data = \
{'': ['*']}

install_requires = \
['pydantic==1.9.1', 'pymisp==2.4.159', 'requests==2.27.1']

setup_kwargs = {
    'name': 'vysion',
    'version': '0.3.2',
    'description': 'The official Python client library for Vysion',
    'long_description': "\n# References\n\n- https://pydantic-docs.helpmanual.io/\n- https://python-patterns.guide/\n- https://docs.pytest.org/en/7.1.x/getting-started.html#get-started\n- https://github.com/samuelcolvin/pydantic\n- https://python-poetry.org/docs/pyproject\n- https://github.com/wemake-services/wemake-python-package\n\n## Style\n\n- https://code.visualstudio.com/docs/languages/python\n- https://code.visualstudio.com/docs/python/linting\n- https://code.visualstudio.com/api/language-extensions/snippet-guide\n- https://semver.org/\n- https://snyk.io/blog/python-poetry-package-manager/\n\n### Taxonomy\n\n- https://github.com/MISP/misp-taxonomies/blob/main/tools/machinetag.py\n- https://www.misp-project.org/taxonomies.html#_mapping_of_taxonomies\n- https://github.com/MISP/misp-taxonomies\n- https://github.com/MISP/misp-taxonomies/blob/main/tools/docs/images/taxonomy-explanation.png\n\n## Entorno\n\n- vs-code\n    - Extensiones:\n        - snyk\n        - flake8\n\n## The Zen of Python\n\n```python\nimport this\n> The Zen of Python, by Tim Peters\n> \n> Beautiful is better than ugly.\n> Explicit is better than implicit.\n> Simple is better than complex.\n> Complex is better than complicated.\n> Flat is better than nested.\n> Sparse is better than dense.\n> Readability counts.\n> Special cases aren't special enough to break the rules.\n> Although practicality beats purity.\n> Errors should never pass silently.\n> Unless explicitly silenced.\n> In the face of ambiguity, refuse the temptation to guess.\n> There should be one-- and preferably only one --obvious way to do it.\n> Although that way may not be obvious at first unless you're Dutch.\n> Now is better than never.\n> Although never is often better than *right* now.\n> If the implementation is hard to explain, it's a bad idea.\n> If the implementation is easy to explain, it may be a good idea.\n> Namespaces are one honking great idea -- let's do more of those!\n```\n\n# Ackowledgement\n\nWe really appreciate the documentation of https://github.com/VirusTotal/vt-py\n",
    'author': 'Javier Junquera-Sánchez',
    'author_email': 'javier.junquera@byronlabs.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://vysion.ai',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
