===========
utopian-cli
===========

.. image:: https://img.shields.io/pypi/v/utopian.svg
  :target: https://pypi.python.org/pypi/utopian

.. image:: https://img.shields.io/pypi/pyversions/utopian.svg
  :target: https://pypi.python.org/pypi/utopian

A command-line interface for `Utopian.io <https://utopian.io>`_. created using `Click <http://click.pocoo.org/6/>`_.

------------
Installation
------------
The recommended way to install utopian-cli is via `pip`

.. code-block:: bash
    
    $ pip install utopian

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
      performance
      sponsors
      stats

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
      --supervisor        Flag for only showing supervisors.
      --j                 Print moderator in JSON format.
      --account TEXT      Specific moderator account.
      --reviewed INTEGER  Minimum amount of contributions reviewed.
      --help              Show this message and exit.
            Show this message and exit.

Sponsors
--------

.. code-block::

    Usage: utopian sponsors [OPTIONS]

    Options:
      --j             Print sponsor in JSON format.
      --account TEXT  Sponsor's account name.
      --help          Show this message and exit.
      
Performance
-----------
 
.. code-block::
 
    Usage: utopian performance [OPTIONS]

      Takes a given account and either shows the account's performance as a
      contributor or as a moderator (if applicable) in a given time period.

    Options:
      -a, --account TEXT              [required]
      --date DATE                     See performance for the time period [NOW] -
                                      [DATE]
      --days INTEGER                  See performance for the last N days.
      --contributor                   See performance as a contributor.
      --moderator                     See performance as a moderator.
      --supervisor                    See performance of a supervisor's team.
      --details                       See more details about who you have
                                      reviewed/has reviewed you.
      --limit INTEGER                 Limit the --details table to the top N
                                      authors/moderators.
      --sort [total|accepted|rejected]
                                      Value to sort the table by.
      --help                          Show this message and exit.

Project
-------

.. code-block::

    Usage: utopian project [OPTIONS] REPOSITORY

    Options:
      --date DATE                     See performance for the time period [NOW] -
                                      [DATE]
      --days INTEGER                  See performance for the last N days.
      --details                       See more details about who you have
                                      reviewed/has reviewed you.
      --limit INTEGER                 Limit the --details table to the top N
                                      authors/moderators.
      --sort [total|accepted|rejected]
                                      Value to sort the table by.
      -a, --author TEXT               Author to filter the table by.
      -c, --category [all|blog|ideas|sub-projects|development|bug-hunting|translations|graphics|analysis|social|documentation|tutorials|video-tutorials|copywriting]
      --help                          Show this message and exit.

