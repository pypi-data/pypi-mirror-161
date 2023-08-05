# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['servd']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'servd',
    'version': '1.0.0',
    'description': 'Python daemonizer for Unix, Linux and OS X.',
    'long_description': 'Servd\n=====\n*Python daemonizer for Unix, Linux and OS X.*\n\nThis library is a fork of `python-daemon <https://github.com/serverdensity/python-daemon>`_ developed originally by `serverdensity <https://github.com/serverdensity>`_.\n\n\nInstall\n-------\n.. code-block:: bash\n    \n    pip install servd\n\n\nUsage\n-----\nIt has a very simple usage and only requires a pid file to keep track of the daemon. The *run()* method should be overrided.\n\n.. code-block:: python\n    \n    from servd import Daemon\n\n\n    class Service(Daemon):\n        def __init__(self, pidfile) -> None:\n            super().__init__(pidfile)\n\n        def run(self) -> None:\n            """Service code."""\n\n\n    service = Service("service.pid")\n\n    # Start service daemon\n    service.start()\n\n    # Restart service daemon\n    service.restart()\n\n    # Stop service daemon\n    service.stop()\n',
    'author': 'Server Density',
    'author_email': None,
    'maintainer': 'LW016',
    'maintainer_email': None,
    'url': 'https://github.com/lw016/servd',
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
