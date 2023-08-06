Contributing
============

.. note::

  These instructions are out of date. many of these functions may be invoked using the included ops.sh script.

Preparing your development environment
--------------------------------------

1. Install Python 3, PIP, GIT and GIT Flow.

.. code-block:: bash

    sudo apt install -y python3 python3-pip git git-flow

2. Clone the repository

.. code-block:: bash

  git clone {{ repository_url }}
  cd {{ repository_name }}


3. Install development requirements

.. code-block:: bash

    sudo pip install -r  requirements-dev.txt


Generating the documentation
----------------------------

The documentation for this project is built with Sphinx_. A variety of modules assist in the documentation generation to minimize developer maintainence burden. PBR_ provides some configuration information to Sphinx_, using `Sphinx AutoDoc`_ and `Sphinx AutoModAPI`_. Documentation comments (i.e. docstrings) use NumPyDoc_-formatting, and the produced documentation uses a slightly-tweaked version of the `Read the Docs Sphinx Theme`_.

.. _Sphinx: http://www.sphinx-doc.org/en/master/
.. _PBR: https://docs.openstack.org/pbr/3.0.1/#
.. _Sphinx AutoDoc: http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
.. _Sphinx AutoModAPI: https://sphinx-automodapi.readthedocs.io/en/latest/
.. _NumPyDoc: https://numpydoc.readthedocs.io/en/latest/
.. _Read the Docs Sphinx Theme: https://sphinx-rtd-theme.readthedocs.io/en/latest/index.html

.. code-block:: bash

  cd /path/to/repo
  python3 ./setup.py build_sphinx

The generated documentation can be found in */path/to/repo/doc/build/html/index.html*.


Testing
-------

All-in-one testing is initiated by calling `tox` with no arguments. This will build the source distribution, create several testing environments, install the package in each environment, and run the associated unit tests, code coverage checks, style checks, and so on.

.. code-block:: bash

  cd /path/to/repo
  tox

The following environments are defined:

1. py36 - Test the package against a Python 3.6 interpreter
2. py37 - Test the package against a Python 3.7 interpreter
3. py38 - Test the package against a Python 3.8 interpreter
4. py39 - Test the package against a Python 3.9 interpreter
5. coverage - Assess code coverage of tests
6. quality - Asses code quality
7. style - Test the package for coding style guidelines
8. docs - Ensure documentation builds correctly

Running unit tests
^^^^^^^^^^^^^^^^^^

You may test the code against a specific pyXX environments as follows:

.. code-block:: bash

  cd /path/to/repo
  tox -e ENVIRONMENT

Where `ENVIRONMENT` is one of the pyXX (Python X.X) python-interpreter test environments.


Running coverage tests
^^^^^^^^^^^^^^^^^^^^^^

You may generate a testing code coverage report as follows:

.. code-block:: bash

  cd /path/to/repo
  tox -e coverage

Output will be generated in `doc/source/.static/reports/code_coverage/index.html`


Running style tests
^^^^^^^^^^^^^^^^^^^

To explicitly run style checking, invoke `tox` as follows:

.. code-block:: bash

  cd /path/to/repo
  tox -e style

Alternatively, you may invoke flake8 directly:

.. code-block:: bash

  cd /path/to/repo
  flake8 src

Errors and warnings will be displayed to the shell console.

Running code quality tests
^^^^^^^^^^^^^^^^^^^^^^^^^^

To explicitly run code quality checking, invoke `tox` as follows:

.. code-block:: bash

  cd /path/to/repo
  tox -e xenon

Errors and warnings will be displayed to the shell console.



