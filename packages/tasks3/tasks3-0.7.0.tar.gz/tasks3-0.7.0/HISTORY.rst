=======
History
=======

0.7.0: (2022-07-30)
-------------------

* Added support to delete a task from the cli.
* Updated dependencies.

0.6.0 (2022-05-16)
------------------

* Added support to edit existing tasks.
* Update dev-requirements.

0.5.1 (2022-05-06)
------------------

* Added shell integration for fish.

0.5.0 (2022-05-06)
------------------

* Added shell integration for zsh and bash.
* Improve the index page.
* Add more info to Contributing page.

0.4.4 (2022-05-03)
------------------

* Improve docs

0.4.3 (2022-05-03)
------------------

* Fix python version in setup.py

0.4.2 (2022-05-03)
------------------

* Upgrade development status to Alpha.

0.4.1 (2022-05-03)
------------------

* Resolve a SNAFU with tags.

0.4.0 (2022-05-03)
------------------

* Add the ability to search for tasks.
* Add json output format for tasks.
* Implement the ``tasks3 task show`` cli endpoint.
* Update docs.
* Add Output format preference to config.
* Make the cli interface easier to use (flatten the task command tree)

0.3.3 (2022-05-02)
------------------

* Switch docs theme to ``sphinx_rtd_theme``.

0.3.2 (2022-05-02)
------------------

* Add workflow to check for package compatability with PyPI.
  This should make sure that the issue with v0.3.0 does not occur again.

0.3.1 (2022-05-02)
------------------

* Fix README to render on PyPI.

0.3.0 (2022-05-02)
------------------

* Remove ``tasks3 db init`` cli command.
* Implement ``tasks3 task add`` cli command.
* Implement ``task.yaml``, ``task.short``, ``task.one_line`` methods to display task.

0.2.8 (2022-05-01)
------------------

* Use dataclass to store configuration settings.
* Flatten tasks3.config module into config.py file.

0.2.7 (2022-04-30)
------------------

* Remove usage of deprecated  SQLAlchemy api ``db_engine.table_names``.
* Remove deprecated pytest configuration option ``collect_ignore``.

0.2.6 (2022-04-30)
------------------

* Flatten tasks3.db.model module into models.py
* Linting changes
* Minor refactoring

0.2.4 (2022-04-30)
------------------

* Remove pytest from dependency and let tox handle testing.

0.2.3 (2022-04-30)
------------------

* Migrate testing to github-workflow
* Update SQLAlchemy package version.
* Switch deployment workflow to python 3.9

0.2.0 (2022-04-30)
------------------

* Drop support for python<=3.8

0.1.0 (2020-08-17)
------------------

* Implement tasks3.add
* Implement tasks3.edit
* Implement tasks3.remove

0.0.11 (2020-08-04)
-------------------

* Add support for a yaml configuration file.
* Add database to store Tasks, db models and api to interact with db.
* Switch to using requirements.txt for managing dependency and add
  back the support for py35.
* Add a bunch of type annotations.
* Update dependency:
   * pip to 20.2
   * pytest to 6.0.1
   * tox to 3.18.1
   * coverage to 5.2.1

0.0.9 - 0.0.10 (2020-07-26)
---------------------------

* Fix version numbers and git tags.

0.0.8 (2020-07-26)
------------------

* Implement a CLI for tasks3.
* Add black (formatter).
* Add some basic test-cases.

0.0.2 - 0.0.7 (2020-07-20)
--------------------------

* Move deployment away from Travis to Github workflow.

0.0.1 (2020-07-20)
------------------

* First release on PyPI.
