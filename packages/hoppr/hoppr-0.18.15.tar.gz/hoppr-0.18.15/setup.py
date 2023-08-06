# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hoppr',
 'hoppr.base_plugins',
 'hoppr.configs',
 'hoppr.core_plugins',
 'hoppr.types',
 'hoppr.types.cyclonedx_1_3',
 'hoppr.types.cyclonedx_1_4']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click==8.1.3',
 'cyclonedx-python-lib>=2.0.0,<3.0.0',
 'jsonschema>=4.4.0,<5.0.0',
 'packageurl-python>=0.10.0,<0.11.0',
 'pydantic[email]>=1.9.0,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'typer>=0.4.0,<0.5.0',
 'types-PyYAML>=6.0.5,<7.0.0',
 'urllib3>=1.26.9,<2.0.0']

entry_points = \
{'console_scripts': ['hopctl = hoppr.main:app']}

setup_kwargs = {
    'name': 'hoppr',
    'version': '0.18.15',
    'description': 'A tool for defining, verifying, and transferring software dependencies between environments.',
    'long_description': '# Hoppr\n\n---\n\n**Documentation**: <a href="https://hoppr.dev/" target="_blank">https://hoppr.dev/</a>\n\n**Source Code**: <a href="https://gitlab.com/lmco/hoppr/hoppr" target="_blank">https://gitlab.com/lmco/hoppr/hoppr</a>\n\n---\n\n**Hoppr** helps your applications and build dependencies _hop_ between air gapped environments. It is a framework that\nsupports packaging, transfer, and delivery of dependencies. **Hoppr** relies on the principles of Linux Foundation\'s focus\non [SPDX](https://spdx.dev/) and the extended functionality of [CycloneDX](https://cyclonedx.org) to define Software\nBill-of-Materials and supply chain management.\n\n**Goals**:\n\n- ```Package``` Framework to collect disparate software products and build dependencies for consolidated packaging\n- ```Verify``` Secure Software Supply Chain Management of these dependencies\n- ```Transfer``` Abstract the transfer method across environment boundaries\n- ```Delivery``` Consolidated packages delivered to target repositories\n\n**Key Features**:\n\n- Standardized workflow\n- Extendable With plugins\n- Core plugins for common operations\n\n## Install\nInstall [hoppr from PyPI](https://pypi.org/project/hoppr/).\n```\npip install hoppr\n```\n\n## Links\n- **(TBD)** Getting Started\n- **(TBD)** Examples\n- **(TBD)** Customizing\n- **(TBD)** Questions\n- **(TBD)** Contributing\n',
    'author': 'LMCO Open Source',
    'author_email': 'open.source@lmco.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://hoppr.dev/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
