========
gg-start
========

.. image:: https://travis-ci.org/peterbe/gg-start.svg?branch=master
    :target: https://travis-ci.org/peterbe/gg-start

.. image:: https://badge.fury.io/py/gg-start.svg
    :target: https://pypi.python.org/pypi/gg-start

A plugin for `gg <https://github.com/peterbe/gg>`_ for starting new branches.


Installation
============

This is a plugin that depends on `gg <https://github.com/peterbe/gg>`_
which gets automatically
installed if it's not already available::

    pip install gg-start

How to develop
==============

To work on this, first run::

    pip install -U --editable .

That installs the package ``gg`` and its dependencies. It also
installs the executable ``gg``. So now you should be able to run::

    gg start --help


Version History
===============

0.1
  * Proof of concept
