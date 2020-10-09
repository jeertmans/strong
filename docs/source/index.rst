.. strong documentation master file, created by
   sphinx-quickstart on Wed Oct  7 21:57:09 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. image:: https://raw.githubusercontent.com/jeertmans/strong/main/img/logo.png
   :align: center
   :height: 300

======================================
Strong: from type-hint to real typing!
======================================

Quickstart
==========

.. _installation-guide:

Installation
------------

To install **Strong**, simply using pip:

.. code::

   python<version> -m pip install strong


.. note::

   This package mostly relies on the quite recent **inspect** and **typing**
   package features. This package therefore require a Python installation
   with version >= 3.5.

Read the documentation
----------------------

.. toctree::
   :maxdepth: 1
   :caption: Modules

   core/core
   utils/utils

Contributor Guide
=================

If you want to help in any way, feel free to check the `Github repository
<https://github.com/jeertmans/strong>`_. This package follows the same
coding guidelines as the one used by default with the Flake8 tool:

.. code::

   flake8 strong
   flake8 tests

And Strong provide additional checks on typing:

.. code::

   strong strong

Code reformatting is done using Black tool:

.. code::

   black strong -l 79
   black tests -l 79

Lastly, make sure to run the tests:

.. code::

   pytest tests

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
