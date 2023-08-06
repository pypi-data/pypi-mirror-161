======
tasks3
======


.. image:: https://img.shields.io/pypi/v/tasks3.svg
        :target: https://pypi.python.org/pypi/tasks3

.. image:: https://github.com/hXtreme/tasks3/actions/workflows/tox-test.yml/badge.svg
        :target: https://github.com/hXtreme/tasks3/actions/workflows/tox-test.yml

.. image:: https://readthedocs.org/projects/tasks3/badge/?version=latest
        :target: https://tasks3.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status



A commandline tool to create and manage tasks and todos.

Most task management tools are their own applications, so to manage tasks you have to
perform context switching by leaving what you're working on
to go to the task manager application.

``tasks3`` aims to solve that by bringing your tasks to you instead.

Each task is automatically assigned to the directory it was created in
and you can easily retrieve tasks under a directory.


* Free software: GNU General Public License v3
* Documentation: https://tasks3.readthedocs.io.


Features
--------

Help
====

It is easy to explore all capabilities of ``tasks3`` by running ``tasks3 --help``.
Each command also has its own help page which can be accessed by running:

.. code-block:: console

        $ tasks3 <command> --help

Create Tasks
============

Easily create tasks from the commandline and delegate them to folders.

Create a task in a specific folder with default settings.

.. code-block:: console

        $ tasks3 add --title "Think of a cool name" \
            --folder "~/Documents/story" \
            --yes
        Added Task:
        [e1c100] Think of a cool name (⏰⏰    ) (🚨🚨  )
          [path: ~/Documents/story]

Create a task in a current folder with custom settings and description.

.. code-block:: console

        $ tasks3 add --title "Try new model" \
            --urgency 4 --importance 3 \
            --description "Try:\n - model with 3 layers.\n - model with 4 layers." \
            --yes
        Added Task:
        [a0a5f4] Try new model (⏰⏰⏰⏰) (🚨🚨🚨 )
            Try:
             - model with 3 layers.
             - model with 4 layers.

Edit Existing Tasks
===================

You can edit existing tasks with the ``tasks3 edit`` command.

For example: You can use ``edit`` to update the urgency of a task.

.. code-block:: console

        $ tasks3 edit --urgency 4 e1c100
        Updated Task:
        [e1c100] Think of a cool name (⏰⏰⏰⏰) (🚨🚨  )
          [path: ~/Documents/story]

Search Tasks
============

You can search for tasks using various filters.

You can search for tasks with a specific importance value.

.. code-block:: console

        $ tasks3 search --importance 2
        [4a14d0] What is right here and now
        [f79155] Think of a cool name [path: /home/<user>/Documents/project]
        [2ce91b] See home [path: /home]

You can restrict search to a folder and its sub-directories.

.. code-block:: console

        $ tasks3 search --folder ~/Documents/project --output-format yaml
        title: Think of a Cool name
        urgency: 2
        importance: 2
        tags: null
        folder: /home/<user>/Documents/project

You can also search for sub-strings in task title or description.
It is also possible to restrict the search to tasks that have a specific set of tags.
Run ``tasks3 search --help`` to get see a full list off options.

Show Tasks
==========

You can show all tasks under current directory.

.. code-block:: console

        $ tasks3 show
        [a0a5f4] Try new model (⏰⏰⏰⏰) (🚨🚨🚨 )
            Try:
             model with 3 layers.
             model with 4 layers.
        [4a14d0] What is right here and now (⏰⏰    ) (🚨🚨  )

You can also show a particular task by specifying its id.

.. code-block:: console

        $ tasks3 show 1d8a9a
        [1d8a9a] Give a Title to this Task. (⏰⏰    ) (🚨🚨🚨🚨)
          (Hello tasks3)
            Task with
            multi-line
            desc

If you prefer to see the task in a different format, you can use the ``--output-format`` option.

.. code-block:: console

        $ tasks3 show --output-format json 1d8a9a
        {
          "id": "1d8a9a",
          "title": "Give a Title to this Task.",
          "urgency": 2,
          "importance": 4,
          "tags": [
            "Hello tasks3"
          ],
          "folder": "/home/<user>/Documents/tasks3",
          "description": "Task with \nmulti-line \ndesc"
        }


Delete Tasks
============

You can use the ``tasks3 delete <task_id>`` command to delete a task.

.. note:: I will be adding a way to simply mark a task as done in the future,
        prefer using that instead of deleting tasks.

.. code-block:: console

        $ tasks3 remove --yes 2e0b84
        Removed Task: [2e0b84] Adding support for task deletion (⏰⏰    ) (🚨🚨  )

Shell Integration
=================

tasks3 supports shell integration for bash, zsh, and fish; tasks3 will automatically
run ``tasks3 show -o oneline`` when you ``cd`` into a directory to show
the tasks in that directory.

You can setup shell integration by adding the following command to your ``.rc`` file.

.. code-block:: shell

        eval "$(tasks3 shell $(basename $SHELL))"

.. note:: Pull requests to support additional shells are greatly appreciated.
        Please see Contributing_ page for information on how to contribute.

* TODO: Delete tasks.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Contributing: ./contributing.html
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
