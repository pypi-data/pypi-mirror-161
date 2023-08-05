Servd
=====
*Python daemonizer for Unix, Linux and OS X.*

This library is a fork of `python-daemon <https://github.com/serverdensity/python-daemon>`_ developed originally by `serverdensity <https://github.com/serverdensity>`_.


Install
-------
.. code-block:: bash
    
    pip install servd


Usage
-----
It has a very simple usage and only requires a pid file to keep track of the daemon. The *run()* method should be overrided.

.. code-block:: python
    
    from servd import Daemon


    class Service(Daemon):
        def __init__(self, pidfile) -> None:
            super().__init__(pidfile)

        def run(self) -> None:
            """Service code."""


    service = Service("service.pid")

    # Start service daemon
    service.start()

    # Restart service daemon
    service.restart()

    # Stop service daemon
    service.stop()
