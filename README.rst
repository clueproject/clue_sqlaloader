===============
clue_sqlaloader
===============

Overview
========

*clue_sqlaloader* provides a mechanism for populating a sql database
using `SQLAlchemy <http://www.sqlalchemy.org/>`_ and
`YAML <http://www.yaml.org/>`_.

Usage
=====

*clue_sqlaloader* was primarily meant to run from inside other
applications as a framework piece but can be run from the command-line
as follows::

  $ python -m clue_sqlaloader.__init__ sqlite:///somefile.db data.yaml

The typical way to use the loader from within Python is as follows::

  from clue_sqlaloader import Loader
  loader = Loader(sqlalchemy_session)
  loader.load_from_yamlf('somefile.yaml')


Credits
=======

Written and maintained by Rocky Burt <rocky@serverzen.com>
