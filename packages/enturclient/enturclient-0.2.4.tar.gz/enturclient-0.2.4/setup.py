# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['enturclient', 'enturclient.dto']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0', 'async_timeout>=3.0.1,<5.0']

setup_kwargs = {
    'name': 'enturclient',
    'version': '0.2.4',
    'description': 'An API client for public transport data from Entur.',
    'long_description': '# Entur API client\n\nPython client for fetching estimated departures from stop places in Norway from [`entur.org`](https://developer.entur.org) API. Information about stop places, platforms and real-time departures.\n\n[![PyPI version fury.io][pypi-version-badge]][pypi-enturclient]\n[![PyPI pyversions][py-versions-badge]][pypi-enturclient]\n\n[![Buy me a coffee][buymeacoffee-shield]][buymeacoffee]\n\n## Usage\n\n```python\nimport aiohttp\nimport asyncio\nfrom enturclient import EnturPublicTransportData\n\nAPI_CLIENT_ID = \'awesome_company - my_application\'\n\nasync def print_bergen_train_delay():\n    async with aiohttp.ClientSession() as client:\n        stops = [\'NSR:StopPlace:548\']\n        quays = [\'NSR:Quay:48550\']\n\n        data = EnturPublicTransportData(\n            client_name=API_CLIENT_ID, # Required\n            stops=stops,\n            quays=quays,\n            omit_non_boarding=True,\n            number_of_departures=5,\n            web_session=client) # recommended argument\n\n        await data.update()\n\n        bergen_train = data.get_stop_info(\'NSR:StopPlace:548\')\n        bergen_train_delay = bergen_train.estimated_calls[0].delay_in_min\n\n        print(bergen_train_delay)\n\nasyncio.run(print_bergen_train_delay())\n```\n\n## Obtaining a stop id\n\n[Entur\'s travel planer](https://en-tur.no) has a map of all stops used in Norway. Use the map to find the stops you\'re interested in. When you have found one of your stops, click on it, and hit "Se alle avganger".\n\nNow the web browser should contain an URL with the id in it. Such as this:\n`https://en-tur.no/nearby-stop-place-detail?id=NSR:StopPlace:32376`\n\nThe stop id is the content after `id=` parameter in the url. Copy paste this into the configuration.\n\nIt\'s also possible to use the [National Stop Register (NSR)](https://stoppested.entur.org).\nFind your stop in the map, click on it and then again at the name. You have to zoom quite a bit in before the stops shows in the map. Information about the stop place, including the stop and quay ids will pop up on the side.\n\n[buymeacoffee-shield]: https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-2.svg\n[buymeacoffee]: https://www.buymeacoffee.com/heine\n[pypi-enturclient]: https://pypi.org/project/enturclient/\n[pypi-version-badge]: https://badge.fury.io/py/enturclient.svg\n[py-versions-badge]: https://img.shields.io/pypi/pyversions/enturclient.svg\n',
    'author': 'Heine Furubotten',
    'author_email': 'hfurubotten@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hfurubotten/enturclient',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
