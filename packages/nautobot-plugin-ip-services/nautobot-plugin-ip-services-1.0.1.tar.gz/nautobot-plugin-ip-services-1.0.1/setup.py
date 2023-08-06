# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nautobot-plugin-ip-services', 'nautobot-plugin-ip-services.tests']

package_data = \
{'': ['*'],
 'nautobot-plugin-ip-services': ['templates/nautobot_plugin_ip_services/*']}

setup_kwargs = {
    'name': 'nautobot-plugin-ip-services',
    'version': '1.0.1',
    'description': 'View/Manage Services from IPAM',
    'long_description': '# Nautobot IP Services Plugin\n\nNautobot natively provides the ability to add Services such as TCP/UDP ports that are exposed on an Interface of a Device using the "Assign service" button on the Device view. The Services can also optionally be assigned to an IP address from the Device view.  This plugin for [Nautobot](https://www.github.com/nautobot) extends the functionality by adding the ability to view and add Services from the IP Address view in IPAM.  \n  \nWith the plugin installed, users can see the list of services associated with an IP address in IPAM.\n\n![image](https://user-images.githubusercontent.com/6945229/182711099-9d07c716-a8a0-44f0-93eb-7d2763f77388.png)\n\nIn addition, users can also use the `Assign service` button to define new Services associated with the IP Address.  The IP address from the previous IP Address view is automatically programmed into the `IP Addresses` field on the form. \n\n![image](https://user-images.githubusercontent.com/6945229/182711414-a1f1636f-74cc-4d67-ba69-0867263e9076.png)\n\n## Setup\n1. Install the package on the Nautobot server:\n```bash\npip install nautobot-plugin-ip-services\n```\n  \n2. Add plugin to `PLUGINS` in `nautobot_config.py`:\n```python\nPLUGINS = [\n    "nautobot-plugin-ip-services",\n]\n```\n3. Restart the Nautobot services:\n```bash\nsudo systemctl restart nautobot nautobot-worker nautobot-scheduler \n```\n\n\n',
    'author': 'Matt Mullen',
    'author_email': 'mullenmd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mamullen13316/nautobot-plugin-ip-services',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
