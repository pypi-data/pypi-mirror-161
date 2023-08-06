# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tests',
 'xedocs',
 'xedocs.schemas',
 'xedocs.schemas.analysis',
 'xedocs.schemas.calibrations',
 'xedocs.schemas.corrections',
 'xedocs.schemas.operations_reports',
 'xedocs.schemas.pmt_data']

package_data = \
{'': ['*']}

install_requires = \
['click', 'rframe>=0.1.19,<0.2.0', 'rich']

extras_require = \
{'db': ['pymongo'], 'gui': ['pydantic-panel>=0.1.8,<0.2.0']}

entry_points = \
{'console_scripts': ['xedocs = xedocs.cli:main']}

setup_kwargs = {
    'name': 'xedocs',
    'version': '0.1.23',
    'description': 'Top-level package for xedocs.',
    'long_description': "===========================================\nXeDocs - AKA Corrections Managment Tool 2.0\n===========================================\nxedocs is meant to replace cmt and bodega as well as helping tracking all shared documents especially if\nthey need to be versioned.\n\nBasic Usage\n-----------\n\nExplore the available schemas\n\n.. code-block:: python\n\n    import xedocs\n\n    >>> xedocs.list_schemas()\n    >>> ['bodega',\n        'fax_configs',\n        'plugin_lineages',\n        'context_lineages',\n        'pmt_gains',\n        'global_versions',\n        'electron_drift_velocities',\n        ...]\n\n    >>> xedocs.help('pmt_gains')\n\n    >>>\n            Schema name: pmt_gains\n            Index fields: ['version', 'time', 'detector', 'pmt']\n            Column fields: ['created_date', 'comments', 'value']\n    \n\nRead data from the default data source\n\n.. code-block:: python\n\n    import xedocs\n\n    docs = xedocs.find('pmt_gains',  version='v1', pmt=[1,2,3,5], time='2021-01-01T00:00:00', detector='tpc')\n    gains = [doc.value for doc in docs]\n\n    doc = xedocs.find_one('pmt_gains',  version='v1', pmt=1, time='2021-01-01T00:00:00', detector='tpc')\n    pmt1_gain = doc.value\n\n\nYou can also query documents directly from the scham class, \nSchemas will query the mongodb cmt2 database by default, if no explicit datasource is given.\n\n.. code-block:: python\n    \n    drift_velocity = xedocs.Bodega.find_one(field='drift_velocity', version='v1')\n    \n    # Returns a Bodega object with attributes value, description etc.\n    drift_velocity.value\n\n    all_v1_documents = xedocs.Bodega.find(version='v1')\n\n\n\nRead data from alternative data sources specified by path, \ne.g csv files which will be loaded by pandas.\n\n.. code-block:: python\n\n    import xedocs\n    \n    g1_doc = xedocs.find_one('bodega', datasource='/path/to/file.csv', version='v1', field='g1')\n    g1_value = g1_doc.value\n    g1_error = g1_doc.uncertainty\n\nThe path can also be a github URL or any other URL supported by fsspec. \n\n.. code-block:: python\n\n    import xedocs\n    \n    g1_doc = xedocs.find_one('bodega',\n                             datasource='github://org:repo@/path/to/file.csv', \n                             version='v1', \n                             field='g1')\n\n\nSupported data sources\n\n    - MongoDB collections\n    - TinyDB tables\n    - JSON files\n    - REST API clients\n\nPlease open an issue on rframe_ if you want support for an additional data format.\n\n\nDocumentation\n-------------\nFull documentation hosted by Readthedocs_\n\nCredits\n-------\n\n\nThis package was created with Cookiecutter_ and the `briggySmalls/cookiecutter-pypackage`_ project template.\n\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`briggySmalls/cookiecutter-pypackage`: https://github.com/briggySmalls/cookiecutter-pypackage\n.. _Readthedocs: https://xedocs.readthedocs.io/en/latest/\n.. _rframe: https://github.com/jmosbacher/rframe",
    'author': 'Yossi Mosbacher',
    'author_email': 'joe.mosbacher@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/XENONnT/xedocs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
