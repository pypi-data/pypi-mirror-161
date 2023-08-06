Principled Technologies Boilerplate Utilities
=============================================

.. cut-here

This library provides oft-reused boilerplate functions and classes. This library is under construction.  Please see LICENSE.txt for licensing information.
For the moment the `GitLab repository <https://www.gitlab.com/principled.technologies/community/ptutils>`_ is private, but will be made available soon.

Usage
-----

Install with PIP
^^^^^^^^^^^^^^^^

Install the package (or add it to your ``requirements.txt`` file):

.. code-block:: bash

    pip install ptutils


Import in Python
^^^^^^^^^^^^^^^^

Import the library in python:

.. code-block:: python

    from logging import getLogger
    from ptutils.io import File
    from ptutils.encoding import pretty_json

    logger = getLogger(__name__)
    f      = File('/etc/docker/daemon.json')
    data   = f.content
    text   = pretty_json( data )
    
    logger.debug( text )
