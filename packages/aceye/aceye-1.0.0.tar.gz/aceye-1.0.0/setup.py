# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aceye']

package_data = \
{'': ['*'],
 'aceye': ['Bridge Domains/CSV/*',
           'Bridge Domains/HTML/*',
           'Bridge Domains/JSON/*',
           'Bridge Domains/Markdown/*',
           'Bridge Domains/Mindmap/*',
           'Bridge Domains/YAML/*',
           'Contexts/CSV/*',
           'Contexts/HTML/*',
           'Contexts/JSON/*',
           'Contexts/Markdown/*',
           'Contexts/Mindmap/*',
           'Contexts/YAML/*',
           'EPG/CSV/*',
           'EPG/HTML/*',
           'EPG/JSON/*',
           'EPG/Markdown/*',
           'EPG/Mindmap/*',
           'EPG/YAML/*',
           'Tenant/CSV/*',
           'Tenant/HTML/*',
           'Tenant/JSON/*',
           'Tenant/Markdown/*',
           'Tenant/Mindmap/*',
           'Tenant/YAML/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'requests>=2.28.1,<3.0.0',
 'rich-click>=1.5.1,<2.0.0']

entry_points = \
{'console_scripts': ['aceye = aceye.script:run']}

setup_kwargs = {
    'name': 'aceye',
    'version': '1.0.0',
    'description': 'Business ready documents from Cisco ACI',
    'long_description': '# ACEye\nBusiness Ready Documents for Cisco ACI\n',
    'author': 'John Capobianco',
    'author_email': 'ptcapo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
