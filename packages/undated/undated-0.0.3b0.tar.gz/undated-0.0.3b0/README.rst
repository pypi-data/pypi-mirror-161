Undated - *"For when dates aren't dates"*
=========================================

*undated* is a Python package that simplifies the process of working with dates that are stored as numbers or strings.

Whilst datatypes should fit their purpose, date types do not always transport well and are converted to a number or string,
such as `ISO 8601 <https://iso.org/iso-8601-date-and-time-format.html>`_, for transportation in text based files like json or csv.

*undated* provides:
 - Functionality to handle dates that are stored in number formats
 - Ability to derive the date format from provided data
 - Direct manipulation to avoid costly type conversions

.. note::

   Although *undated* is whizzy with dates, operating with time elements is out of its scope. 

Inception
=========

*undated* came about due to the need to process large amounts of data from various sources. These were received as csv files
where the format of the date was dependant on either the country of origin, source system, or which ever way the wind blew.
One solution was required to enable big data to be processed regardless of its date formatting... *undated*.

Supported Versions
==================

Supported on Python 3.7, 3.8, 3.9 and 3.10

Installation
============

The package can be found on `GitHub <https://github.com/rikfair/undated>`_ and `PyPI <https://pypi.org/project/undated/>`_,
so naturally it can be installed with `pip`

.. code-block::

   pip install undated

Requirements
============

The ``undated`` package itself has no requirements.

To use the unittests and timings modules ``dateutils`` is required.

.. code-block::

   pip install python-dateutil>=2.8.2

To generate the Sphinx documentation, Sphinx and the RTD template are required.

.. code-block::

   pip install Sphinx>=5.0.2
   pip install sphinx-rtd-theme>=1.0.0

Licence
=======

This software is released under the MIT licence
