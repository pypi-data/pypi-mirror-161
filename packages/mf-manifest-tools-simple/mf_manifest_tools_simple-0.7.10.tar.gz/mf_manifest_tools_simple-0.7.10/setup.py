# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mf_manifest_tools_simple',
 'mf_manifest_tools_simple.generators',
 'mf_manifest_tools_simple.generators.excel',
 'mf_manifest_tools_simple.generators.huawei_ap',
 'mf_manifest_tools_simple.generators.mf_manifest',
 'mf_manifest_tools_simple.generators.mfr',
 'mf_manifest_tools_simple.hackers',
 'mf_manifest_tools_simple.parser',
 'mf_manifest_tools_simple.searcher']

package_data = \
{'': ['*']}

install_requires = \
['PyPDF2>=1.26.0',
 'docopt>=0.6.2',
 'graphviz>=0.16',
 'inflection>=0.5.1',
 'jsonschema>=3.2.0',
 'loguru>=0.5.3',
 'lxml>=4.6.3',
 'openpyxl>=3.0.7',
 'pyyaml>=5.4.1']

extras_require = \
{':python_version < "3.7"': ['dataclasses>=0.8,<0.9']}

entry_points = \
{'console_scripts': ['mf_manifest_tools_simple = '
                     'mf_manifest_tools_simple:main']}

setup_kwargs = {
    'name': 'mf-manifest-tools-simple',
    'version': '0.7.10',
    'description': 'MF Manifest Tools Simple',
    'long_description': None,
    'author': 'xx',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
