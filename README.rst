===========
utopian-cli
===========

.. image:: https://img.shields.io/pypi/v/utopian.svg
  :target: https://pypi.python.org/pypi/utopian

.. image:: https://img.shields.io/pypi/pyversions/utopian.svg
  :target: https://pypi.python.org/pypi/utopian

A command-line interface for `Utopian.io<https://utopian.io>`_. created using `Click<http://click.pocoo.org/6/>`_.

------------
Installation
------------
The recommended way to install utopian-cli is via `pip`

.. code-block:: bash
    
    $ pip3 install utopian

-----
Usage
-----

.. code-block::

    Usage: utopian [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      contributions
      moderators


Contributions
-------------
    
.. code-block::
    
    Usage: utopian contributions [OPTIONS]

    Options:
      --category [all|blog|ideas|sub-projects|development|bug-hunting|translations|graphics|analysis|social|documentation|tutorials|video-tutorials|copywriting]
                                      Category of the contribution.
      --limit INTEGER                 Limit of amount of contributions to
                                      retrieve.
      --tags TEXT                     Tags to filter the contributions by.
      --author TEXT                   Username to filter the contributions by.
      --reviewed / --unreviewed       Show only reviewed or unreviewed
                                      contributions.
      --title TEXT                    String that should be in title of the
                                      contribution.
      --help                          Show this message and exit.
      
Moderators
----------

.. code-block::

    Usage: utopian moderators [OPTIONS]

    Options:
      --supervisor
      --reviewed INTEGER  Minimum amount of contributions reviewed.
      --help              Show this message and exit.
