# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['homeassistant_api', 'homeassistant_api.models']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp-client-cache>=0.6.1,<0.7.0',
 'aiohttp>=3.8.1,<4.0.0',
 'pydantic<=1.9.0',
 'requests-cache>=0.9.2,<0.10.0',
 'requests==2.27.1',
 'simplejson>=3.17.6,<4.0.0']

setup_kwargs = {
    'name': 'homeassistant-api',
    'version': '4.0.0.post1',
    'description': "Python Wrapper for Homeassistant's REST API",
    'long_description': '# HomeassistantAPI\n\n[![Code Coverage](https://img.shields.io/codecov/c/github/GrandMoff100/HomeAssistantAPI/dev?style=for-the-badge&token=SJFC3HX5R1)](https://codecov.io/gh/GrandMoff100/HomeAssistantAPI)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/HomeAssistant-API?style=for-the-badge)](https://pypi.org/project/homeassistant_api)\n![GitHub commits since latest release (by date including pre-releases)](https://img.shields.io/github/commits-since/GrandMoff100/HomeassistantAPI/latest/dev?include_prereleases&style=for-the-badge)\n[![Read the Docs (version)](https://img.shields.io/readthedocs/homeassistantapi?style=for-the-badge)](https://homeassistantapi.readthedocs.io/en/latest/?badge=latest)\n[![GitHub release (latest by date)](https://img.shields.io/github/v/release/GrandMoff100/HomeassistantAPI?style=for-the-badge)](https://github.com/GrandMoff100/HomeassistantAPI/releases)\n\n[![Home Assistant Logo](https://github.com/GrandMoff100/HomeAssistantAPI/blob/7edb4e6298d37bda19c08b807613c6d351788491/docs/images/homeassistant-logo.png?raw=true)](https://home-assistant.io)\n\n## Python wrapper for Homeassistant\'s [REST API](https://developers.home-assistant.io/docs/api/rest/)\n\nHere is a quick example.\n\n```py\nfrom homeassistant_api import Client\n\nwith Client(\n    \'<API Server URL>\',\n    \'<Your Long Lived Access-Token>\'\n) as client:\n\n    light = client.get_domain("light")\n\n    light.turn_on(entity_id="light.living_room_lamp")\n```\n\nAll the methods also support async!\n\n## Documentation\n\nAll documentation, API reference, contribution guidelines and pretty much everything else\nyou\'d want to know is on our readthedocs site [here](https://homeassistantapi.readthedocs.io)\n\nIf there is something missing, open an issue and let us know! Thanks!\n\nGo make some cool stuff! Maybe come back and tell us about it in a\n[discussion](https://github.com/GrandMoff100/HomeAssistantAPI/discussions)?\nWe\'d love to hear about how you use our library!!\n\n## License\n\nThis project is under the GNU GPLv3 license, as defined by the Free Software Foundation.\n',
    'author': 'GrandMoff100',
    'author_email': 'minecraftcrusher100@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/GrandMoff100/HomeAssistantAPI',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0.0',
}


setup(**setup_kwargs)
