==
gg
==

.. image:: https://travis-ci.org/peterbe/gg.svg?branch=master
    :target: https://travis-ci.org/peterbe/gg

Git and GitHub command line swiss army knife for the productivity addicted.

``gg`` is a base command, and all the work to create branches, list branches,
clean up branches, connect to Bugzilla etc. are done by
`plugins <https://github.com/peterbe/gg/blob/master/PLUGINS.rst>`_.

``gg`` is stateful. Meaning, plugins (not all!) need to store additional
information that is re-used for other commands. For example, to
connect to your GitHub account might need to store a GitHub Access Token.


Installation
============

``gg`` requires Python 3.

The idea is that you install ``gg`` globally::

    sudo pip install gg

But that's optional, you can also just install it in your current
virtual environment::

    pip install gg

If you don't want to install ``gg`` and its dependencies in either the
current working virtual environment *or* in your global system Python,
you can first install `pipx <https://pypi.python.org/pypi/pipx>`_
then once you've installed and set that up::

    pipx install gg

Next, you need to install some plugins. See
`PLUGINS.rst <https://github.com/peterbe/gg/blob/master/PLUGINS.rst>`_
for a list of available plugins.

Bash completion
===============

First download
`gg-complete.sh <https://raw.githubusercontent.com/peterbe/gg/master/gg-complete.sh>`_
and save it somewhere on your computer. Then put this line into your `.bashrc`
(or `.bash_profile` if you're on OSX)::

    source /path/to/gg-complete.sh


How to develop
==============

To work on this, first run::

    pip install -U --editable .

Now you can type::

    gg --help

If you have install more plugins they will be listed under the same
``--help`` command.

Linting
=======

This project tracks `black <https://pypi.org/project/black/>`_ and expects
all files to be as per how ``black`` wants them. Please see its repo for how to
set up automatic formatting.

All code needs to be ``flake8`` conformant. See ``setup.cfg`` for the rules.

To test both, run::

    tox -e lint


How to write a plugin
=====================

To write your own custom plugin, (similar to ``gg/builtins/commands/commit``)
these are the critical lines you need to you have in your ``setup.py``::

    setup(
        ...
        install_requires=['gg'],
        entry_points="""
            [gg.plugin]
            cli=gg_myplugin:start
        """,
        ...
    )

This assumes you have a file called ``gg_myplugin.py`` that has a function
called ``start``.

Version History
===============

0.1
  * Proof of concept
