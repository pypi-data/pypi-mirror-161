# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['formaldict', 'formaldict.tests']

package_data = \
{'': ['*']}

install_requires = \
['kmatch>=0.3.0', 'prompt-toolkit>=3.0.2', 'python-dateutil>=2.8.1']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['importlib_metadata>=4']}

setup_kwargs = {
    'name': 'formaldict',
    'version': '1.0.4',
    'description': 'Formal structured dictionaries parsed from a schema',
    'long_description': 'formaldict\n###########\n\n``formaldict`` provides the constructs for parsing structured dictionaries\nthat adhere to a schema. Along with a simple and flexible schema definition\nto parse and validate dictionaries, ``formaldict`` is integrated with\n`python-prompt-toolkit <https://github.com/prompt-toolkit/python-prompt-toolkit>`__.\nThis integration allows users to easily construct flows for command line\ninterfaces (CLIs) when parsing structured user input.\n\nBelow is an example user input flow constructed with a ``formaldict``\nschema used by `git-tidy <https://github.com/jyveapp/git-tidy>`__:\n\n.. image:: https://raw.githubusercontent.com/jyveapp/formaldict/master/docs/_static/prompt.gif\n   :width: 600\n\nCheck out the `docs <https://formaldict.readthedocs.io/>`__ for a\ntutorial on how to use ``formaldict`` as the backbone for parsing\nstructured input in your library.\n\nDocumentation\n=============\n\n`View the formaldict docs here\n<https://formaldict.readthedocs.io/>`_.\n\nInstallation\n============\n\nInstall formaldict with::\n\n    pip3 install formaldict\n\n\nContributing Guide\n==================\n\nFor information on setting up formaldict for development and\ncontributing changes, view `CONTRIBUTING.rst <CONTRIBUTING.rst>`_.\n\n\nPrimary Authors\n===============\n\n- @wesleykendall (Wes Kendall)\n',
    'author': 'Wes Kendall',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Opus10/formaldict',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.0,<4',
}


setup(**setup_kwargs)
