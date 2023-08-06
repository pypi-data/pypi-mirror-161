# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['detail']

package_data = \
{'': ['*']}

install_requires = \
['click-default-group>=1.2.2',
 'click>=7.0',
 'formaldict>=0.2.0',
 'jinja2>=2.10.3',
 'python-dateutil>=2.8.1',
 'pyyaml>=5.1.2',
 'requests>=2.22.0']

extras_require = \
{':python_version >= "3.7" and python_version < "3.8"': ['importlib_metadata>=4']}

entry_points = \
{'console_scripts': ['detail = detail.cli:main']}

setup_kwargs = {
    'name': 'detail',
    'version': '0.2.1',
    'description': 'Build automations off of structured notes in your project',
    'long_description': "detail\n#######\n\n``detail`` allows contributors to create structured and configurable notes in a project,\nproviding the ability to do automations such as:\n\n1. Ensuring that contributors add information to pull requests that provide\n   QA instructions, release notes, and associated tickets. The ``detail lint`` command\n   ensures that notes are present in a pull request and adhere to the schema.\n\n2. Rendering dynamic logs from the notes. ``detail log`` provides the ability\n   to slice and dice the commit log however you need, pulling in a ``notes``\n   variable in a Jinja template with all notes that can be grouped and filtered.\n\n3. Other automations, such as version bumping, Slack posting, ticket comments,\n   etc can be instrumented in continuous integration from the structured notes.\n\nWhen contributing a change, call ``detail`` to be prompted for all information\ndefined in the project's detail schema. Information can be collected conditionally\nbased on previous steps all thanks to the `formaldict <https://github.com/Opus10/formaldict>`__ library.\n\nBelow is an example of a contributor creating a structured note with the type\nof change they are making, a summary, a description, and an associated Jira\nticket:\n\n.. image:: https://raw.githubusercontent.com/opus10/detail/master/docs/_static/detail-intro.gif\n    :width: 600\n\nNotes are commited to projects, allowing review of them before they are used to\nperform automations in continuous integration.\n\nDocumentation\n=============\n\n`View the detail docs here\n<https://detail.readthedocs.io/>`_.\n\nInstallation\n============\n\nInstall detail with::\n\n    pip3 install detail\n\n\nContributing Guide\n==================\n\nFor information on setting up detail for development and\ncontributing changes, view `CONTRIBUTING.rst <CONTRIBUTING.rst>`_.\n\nPrimary Authors\n===============\n\n- @wesleykendall (Wes Kendall)\n- @tomage (Tómas Árni Jónasson)\n",
    'author': 'Opus 10 Engineering',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Opus10/detail',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4',
}


setup(**setup_kwargs)
