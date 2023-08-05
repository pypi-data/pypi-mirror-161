# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiobungie', 'aiobungie.crates', 'aiobungie.interfaces', 'aiobungie.internal']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp==3.8.1', 'attrs==21.4.0', 'python-dateutil==2.8.2']

setup_kwargs = {
    'name': 'aiobungie',
    'version': '0.2.6',
    'description': 'A Python and Asyncio API for Bungie.',
    'long_description': '# aiobungie\nA statically typed API wrapper for the Bungie\'s REST API written in Python3 and Asyncio.\n\n# Installing\n\nPyPI stable release.\n\n```sh\n$ pip install aiobungie\n```\n\nDevelopment\n```sh\n$ pip install git+https://github.com/nxtlo/aiobungie@master\n```\n\n## Quick Example\n\nSee [Examples for advance usage.](https://github.com/nxtlo/aiobungie/tree/master/examples)\n\n```python\nimport aiobungie\n\nclient = aiobungie.Client(\'YOUR_API_KEY\')\n\nasync def main() -> None:\n\n    # Fetch a clan\n    clan = await client.fetch_clan("Nuanceㅤ")\n\n    # Fetch the clan members.\n    members = await clan.fetch_members()\n\n    # Take the first 2 members.\n    for member in members.take(2):\n        # Get the profile for this clan member.\n        profile = await member.fetch_self_profile(\n            # Passing profile components as a list.\n            components=[aiobungie.ComponentType.CHARACTERS]\n        )\n\n        print(profile.characters)\n\n# You can either run it using the client or just `asyncio.run(main())`\nclient.run(main())\n```\n\n## RESTful clients\nAlternatively, You can use `RESTClient` which\'s designed to only make HTTP requests and return JSON objects.\n\n### Example\n```py\nimport aiobungie\nimport asyncio\n\nasync def main(token: str) -> None:\n    # Single REST client.\n    async with aiobungie.RESTClient("TOKEN") as rest_client:\n        response = await rest_client.fetch_clan_members(4389205)\n        raw_members_payload = response[\'results\']\n\n        for member in raw_members_payload:\n            print(member)\n\nasyncio.run(main("some token"))\n```\n\n### Requirements\n* Python 3.9 or higher\n* aiohttp\n* attrs\n\n## Contributing\nPlease read this [manual](https://github.com/nxtlo/aiobungie/blob/master/CONTRIBUTING.md)\n\n### Getting Help\n* Discord: `Fate 怒#0008` | `350750086357057537`\n* Docs: [Here](https://nxtlo.github.io/aiobungie/).\n',
    'author': 'nxtlo',
    'author_email': 'dhmony-99@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nxtlo/aiobungie',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
