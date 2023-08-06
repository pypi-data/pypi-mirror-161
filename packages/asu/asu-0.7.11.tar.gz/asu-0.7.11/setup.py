# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asu']

package_data = \
{'': ['*'], 'asu': ['static/*', 'templates/*']}

install_requires = \
['PyNaCl>=1.5.0,<2.0.0',
 'connexion[swagger-ui]>=2.12.0,<3.0.0',
 'gunicorn>=20.1.0,<21.0.0',
 'prometheus-client>=0.13.1,<0.14.0',
 'redis>=4.1.1,<5.0.0',
 'requests>=2.27.1,<3.0.0',
 'rq>=1.10.1,<2.0.0']

setup_kwargs = {
    'name': 'asu',
    'version': '0.7.11',
    'description': 'An image on demand server for OpenWrt based distributions',
    'long_description': '# Attendedsysupgrade Server for OpenWrt (GSoC 2017)\n\n[![codecov](https://codecov.io/gh/aparcar/asu/branch/master/graph/badge.svg)](https://codecov.io/gh/aparcar/asu)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![PyPi](https://badge.fury.io/py/asu.svg)](https://badge.fury.io/py/asu)\n\nThis project simplifies the sysupgrade process for upgrading the firmware of\ndevices running OpenWrt or distributions based on it. These tools offer an easy\nway to reflash the router with a new firmware version\n(including all packages) without the need to use `opkg`.\n\nIt\'s called Attended SysUpgrade (ASU) because the upgrade process is not started\nautomatically, but is initiated by a user who waits until it\'s done.\n\nASU is based on an API (described below) to request custom firmware images with\nany selection of packages pre-installed. This avoids the need to set up a build\nenvironment, and makes it possible to create a custom firmware image even using\na mobile device.\n\n## Clients of the Sysupgrade Server\n\n### OpenWrt Firmware Selector\n\nSimple web interface using vanilla JavaScript currently developed by @mwarning.\nIt offers a device search based on model names and show links either to\n[official images](https://downloads.openwrt.org/) or requests images via the\n_asu_ API. Please join in the development at\n[GitLab repository](https://gitlab.com/openwrt/web/firmware-selector-openwrt-org)\n\n![ofs](misc/ofs.png)\n\n### LuCI app\n\nThe package\n[`luci-app-attendedsysupgrade`](https://github.com/openwrt/luci/tree/master/applications/luci-app-attendedsysupgrade)\noffers a simple tool under `System > Attended Sysupgrade`. It requests a new\nfirmware image that includes the current set of packages, waits until it\'s built\nand flashes it. If "Keep Configuration" is checked in the GUI, the device\nupgrades to the new firmware without any need to re-enter any configuration or\nre-install any packages.\n\n![luci](misc/luci.png)\n\n### CLI\n\nThe [`auc`](https://github.com/openwrt/packages/tree/master/utils/auc) package\nperforms the same process as the `luci-app-attendedsysupgrade`\nfrom SSH/the command line.\n\n![auc](misc/auc.png)\n\n## Server\n\nThe server listens for image requests and, if valid, automatically generates\nthem. It coordinates several OpenWrt ImageBuilders and caches the resulting\nimages in a Redis database. If an image is cached, the server can provide it\nimmediately without rebuilding.\n\n### Active server\n\n- [sysupgrade.openwrt.org](https://sysupgrade.openwrt.org)\n- [asu.aparcar.org](https://asu.aparcar.org)\n- ~~[chef.libremesh.org](https://chef.libremesh.org)~~ (`CNAME` to\n  asu.aparcar.org)\n\n## Run your own server\n\nRedis is required to store image requests:\n\n    sudo apt install redis-server tar\n\nInstall _asu_:\n\n    pip install asu\n\nCreate a `config.py`.\nYou can use `misc/config.py` as an example.\n\nStart the server via the following commands:\n\n    export FLASK_APP=asu.asu  # set Flask app to asu\n    flask janitor update      # download upstream profiles/packages - this runs forever\n    flask run                 # run development server - this runs forever\n\nStart the worker via the following comand:\n\n    rq worker                 # this runs forever\n\n### Docker\n\nRun the service inside multiple Docker containers. The services include the _\nASU_ server itself, a _janitor_ service which fills the Redis database with\nknown packages and profiles as well as a `rqworker` which actually builds\nimages.\n\nCurrently all services share the same folder and therefore a very "open" access\nis required. Suggestions on how to improve this setup are welcome.\n\n    mkdir ./asu-service/\n    chmod 777 ./asu-service/\n    cp ./misc/config.py ./asu-service/\n    docker-compose up\n\nA webserver should proxy API calls to port 8000 of the `server` service while\nthe `asu/` folder should be file hosted as-is.\n\n### Production\n\nIt is recommended to run _ASU_ via `gunicorn` proxied by `nginx` or\n`caddyserver`. Find a possible server configurations in the `misc/` folder.\n\nThe _ASU_ server will try `$PWD/config.py` and `/etc/asu/config.py` to find a\nconfiguration. Find an example configuration in the `misc/` folder.\n\n    pip install gunicorn\n    gunicorn "asu.asu:create_app()"\n\nIdeally use the tool `squid` to cache package indexes, which are reloaded every\ntime an image is built. Find a basic configuration in at `misc/squid.conf`\nwhich should be copied to `/etc/squid/squid.conf`.\n\nIf you want to use `systemd` find the service files `asu.service` and\n`worker@.service` in the `misc` folder as well.\n\n### Development\n\nAfter cloning this repository, create a Python virtual environment and install\nthe dependencies:\n\n    python3 -m venv .direnv\n    source .direnv/bin/activate\n    pip install -r requirements.txt\n    export FLASK_APP=asu.asu  # set Flask app to asu\n    export FLASK_APP=tests.conftest:mock_app FLASK_DEBUG=1 # run Flask in debug mode with mock data\n    flask run\n\n### API\n\nThe API is documented via _OpenAPI_ and can be viewed interactively on the\nserver:\n\n[https://sysupgrade.openwrt.org/ui/](https://sysupgrade.openwrt.org/ui/)\n',
    'author': 'Paul Spooren',
    'author_email': 'mail@aparcar.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
