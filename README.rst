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
      contributions  Get information about all contributions made...
      moderators     Command used for printing information about...
      performance    Takes a given account and either shows the...
      project        Get information about the contributions made...
      sponsors       Command used for printing information about...
      stats          Returns statistics about the given category...


Contributions
-------------
    
.. code-block::
    
    Usage: utopian contributions [OPTIONS]

      Get information about all contributions made to Utopian.io.

    Options:
      --category [all|blog|ideas|sub-projects|development|bug-hunting|translations|graphics|analysis|social|documentation|tutorials|video-tutorials|copywriting]
                                      Category of the contribution.
      --limit INTEGER                 Limit of amount of contributions to
                                      retrieve.
      --tags TEXT                     Tags to filter the contributions by.
      --author TEXT                   Username to filter the contributions by.
      -f, --filter_by [all|review|active|inactive]
                                      Filter contribution by
      --title TEXT                    String that should be in title of the
                                      contribution.
      -st, --status [any|pending|reviewed]
                                      Status to filter contributions by.
      -si, --similarity TEXT          Filter contributions by similar title and
                                      body.
      --help                          Show this message and exit.

      
Moderators
----------

.. code-block::

    Usage: utopian moderators [OPTIONS]

      Command used for printing information about Utopian.io moderators and
      supervisors.

    Options:
      -s, --supervisor                Flag for only showing supervisors.
      -m, --moderator                 Flag for only showing moderators.
      --data                          Print moderator in JSON format.
      -a, --account TEXT              Specific moderator account.
      --reviewed INTEGER              Minimum amount of contributions reviewed.
      -s, --sort [id|moderator|referrer|reviewed|rewards]
                                      Column to sort the table by.
      --help                          Show this message and exit.

Sponsors
--------

.. code-block::

    Usage: utopian sponsors [OPTIONS]

      Command used for printing information about Utopian.io sponsors.

    Options:
      --data                          Print sponsor in JSON format.
      -a, --account TEXT              Sponsor's account name.
      --witness                       Sort sponsors by sponsors that are
                                      witnesses.
      --not-witness                   Sort sponsors by sponsors that are
                                      witnesses.
      -s, --sort [id|sponsor|witness|percentage|shares]
                                      Column to sort the table by.
      --help                          Show this message and exit.

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
      -i, --individual
      --help                          Show this message and exit.

Project
-------

.. code-block::

    Usage: utopian project [OPTIONS] REPOSITORY

      Get information about the contributions made to a specific project on
      GitHub.

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
                                      Category to sort the contributions by.
      --help                          Show this message and exit.
