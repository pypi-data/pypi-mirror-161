# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hassbridge']

package_data = \
{'': ['*']}

install_requires = \
['anyio', 'asyncclick>=7', 'dbus_next>=0.1.3', 'websockets>=10.0']

entry_points = \
{'console_scripts': ['hassbridge = hassbridge.cli:cli']}

setup_kwargs = {
    'name': 'homeassistant-mpris-bridge',
    'version': '0.0.2',
    'description': 'Control your Home Assistant media players using MPRIS',
    'long_description': '# Control your Home Assistant media players from your desktop using MPRIS!\n\n## What?\n\nThis project bridges your Home Assistant instance and your desktop to control media players known to your Home Assistant instance.\n\nIt works by by communicating with Home Assistant using its websocket API, and exposes media players to your desktop using widely-implemented MPRIS ("Media Player Remote Interfacing Specification") interfaces.\n\n### Features\n\n* Shows information about what\'s currently being played (artist, album, title, cover art)\n* Basic playback controls (play, pause, previous, next)\n* Volume controlling\n* Seeking forwards/backwards\n* Minimal configuration needed, autodetects players as they come!\n\n\n## tl;dr:\n\n![Demo](hassbridge_demo.gif)\n\n## I want it right now, but how?!\n\n1. Install from PyPI, the simplest way is to use [pipx](https://github.com/pypa/pipx). Alternatively, simple clone this repository and run `poetry install`\n\n```\npipx install homeassistant-mpris-bridge\n```\n\n2. Launch `hassbridge`\n\n```\nhassbridge --endpoint http://192.168.123.123:8123 --token <long lived token>\n```\n\nInstead of using `--endpoint` and `--token` you can also define the following environment variables to achieve the same:\n\n```\nexport HASSBRIDGE_ENDPOINT="http://192.168.123.123:8123"\nexport HASSBRIDGE_TOKEN="<long lived token>"\n```\n\n### Running as systemd service\n\nThe simplest way to make sure the bridge is started alongside your desktop session is to create a systemd user service for it:\n\n1. Create a service file `~/.config/systemd/user/hassbridge.service` with the following content:\n\n```\n[Unit]\nDescription=hassbridge\n\n[Service]\nExecStart=<PATH TO HASSBRIDGE>\nEnvironment="HASSBRIDGE_TOKEN=<YOUR TOKEN>"\nEnvironment="HASSBRIDGE_ENDPOINT=<URL TO HOMEASSISTANT>"\n\n[Install]\nWantedBy=multi-user.target\n```\n\nYou have to do the following substitutions:\n* Replace `<PATH TO HASSBRIDGE>` with the location of the `hassbridge` script (use `which hassbridge`)\n* Replace `<YOUR TOKEN>` with your long-lived token (https://www.home-assistant.io/docs/authentication/#your-account-profile)\n* Replace `<URL TO HOMEASSISTANT>` with the URL to your instance (e.g., http://192.168.123.123:8123).\n\n2. Start the service and verify that it is running correctly\n\n```\nsystemctl --user start hassbridge\nsystemctl --user status hassbridge\n```\n\n3. Enable the service so that it starts automatically when you log in\n\n```\nsystemctl --user enable hassbridge\n```\n\n### hassbridge --help\n\n```\n$ hassbridge --help\nUsage: hassbridge [OPTIONS] COMMAND [ARGS]...\n\n  hass-mpris bridge.\n\nOptions:\n  --endpoint TEXT\n  --token TEXT\n  -d, --debug\n  --help           Show this message and exit.\n\nCommands:\n  connect\n\n```\n\n## How does it work?\n\nHomeassistant connectivity is achived with [homeassistant\'s websockets API](https://developers.home-assistant.io/docs/api/websocket/).\nEvery `media_player` entity in the homeassistant instance will then be exposed over D-Bus to other applications to use, implementing two MPRIS interfaces:\n\n* org.mpris.MediaPlayer2\n* org.mpris.MediaPlayer2.Player\n\nEach time homeassistant informs over websocket API about a state change,\nthe details for known entities are signaled over the D-Bus interfaces to clients.\n\n### Specs\n\n* https://developers.home-assistant.io/docs/api/websocket/\n* https://specifications.freedesktop.org/mpris-spec/2.2/\n\n\n## Contributing\n\nContributions in form of pull requests are more than welcome.\nBefore submitting a PR, verify that the code is correctly formatted by calling `tox -e lint`.\nAlternatively, you can use `pre-commit` to enforce the checks:\n\n```\n$\xa0pre-commit install\n```\n',
    'author': 'Teemu R.',
    'author_email': 'tpr@iki.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rytilahti/homeassistant-mpris-bridge',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
