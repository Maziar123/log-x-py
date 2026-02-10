logxpy: Modern Structured Logging with Sqid Task IDs
====================================================

**log-x-py** is a modern structured logging ecosystem with three components: logging library, tree viewer, and log parser.

**Documentation:**

* `Complete API Reference <https://github.com/Maziar123/log-x-py/blob/main/logxpy-api-reference.html>`_ - Full API docs with examples
* `CodeSite Migration Guide <https://github.com/Maziar123/log-x-py/blob/main/DOC-X/cross-docs/cross-lib1.html>`_ - CodeSite vs logxpy cross-reference

---

Component 1: logxpy - Logging Library
=====================================

**Structured logging library with Sqid task IDs, fluent API, and minimal dependencies**

.. image:: https://img.shields.io/badge/python-3.12+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.12+

.. image:: https://img.shields.io/badge/dependencies-boltons%2C%20more--itertools-green.svg
   :alt: Dependencies

.. image:: https://img.shields.io/badge/license-Apache%202.0-blue.svg
   :alt: License

Features
--------

* **Type Safe** - Full type hints with Python 3.12+ syntax
* **Fast** - Dataclasses with slots (-40% memory), pattern matching (+10% speed)
* **Minimal Dependencies** - Uses boltons (pure Python utility library)
* **Fluent API** - All methods return self for method chaining
* **Sqid Task IDs** - 89% smaller than UUID4 (4-12 chars vs 36)
* **Compact Field Names** - 1-2 character field names minimize log size
* **Nested Actions** - Track hierarchical operations with context
* **Status Tracking** - Automatic start/success/failed tracking
* **Color Support** - Foreground/background colors for CLI viewer rendering

Quick Start
-----------

Install logxpy::

    pip install logxpy

Basic usage::

    from logxpy import start_action, Message, to_file

    to_file(open("app.log", "w"))

    with start_action(action_type="http:request", method="POST", path="/api/users"):
        with start_action(action_type="database:query", table="users"):
            Message.log(message_type="database:result", rows=10)

Sqid Task IDs
-------------

LogXPy uses **Sqids** - ultra-short hierarchical task IDs that are 89% smaller than UUID4:

+-----------+------------------+--------+------------------+
| Format    | Example          | Length | Use Case         |
+===========+==================+========+==================+
| Root      | ``"Xa.1"``       | 4 chars| Top-level task   |
+-----------+------------------+--------+------------------+
| Child     | ``"Xa.1.1"``     | 6 chars| Nested action    |
+-----------+------------------+--------+------------------+
| Deep      | ``"Xa.1.1.2"``   | 8 chars| 3 levels deep    |
+-----------+------------------+--------+------------------+
| UUID4     | ``"59b00..."``   | 36 chars| Distributed mode|
+-----------+------------------+--------+------------------+

**Benefits:**

* Human-readable hierarchy (dots show depth)
* Process-isolated (PID prefix prevents collisions)
* 238K entries per process before wrap

**Force UUID4 for distributed systems:**

.. code-block:: bash

    export LOGXPY_DISTRIBUTED=1

Compact Field Names
-------------------

LogXPy uses **1-2 character field names** to minimize log size:

+-----------+-------------------+-------------------------------------------+
| Compact   | Legacy            | Meaning                                   |
+===========+===================+===========================================+
| ``ts``    | ``timestamp``     | Unix timestamp (seconds)                  |
+-----------+-------------------+-------------------------------------------+
| ``tid``   | ``task_uuid``     | Task ID (Sqid format)                     |
+-----------+-------------------+-------------------------------------------+
| ``lvl``   | ``task_level``    | Hierarchy level array                     |
+-----------+-------------------+-------------------------------------------+
| ``mt``    | ``message_type``  | Log level (info, success, error)          |
+-----------+-------------------+-------------------------------------------+
| ``at``    | ``action_type``   | Action type (for emoji)                   |
+-----------+-------------------+-------------------------------------------+
| ``st``    | ``action_status`` | started/succeeded/failed                  |
+-----------+-------------------+-------------------------------------------+
| ``dur``   | ``duration``      | Duration in seconds                       |
+-----------+-------------------+-------------------------------------------+
| ``msg``   | ``message``       | Log message text                          |
+-----------+-------------------+-------------------------------------------+

**Using compact field constants:**

.. code-block:: python

    from logxpy import TS, TID, LVL, MT, AT, ST, DUR, MSG

    entry = {
        TS: time.time(),
        TID: sqid(),
        LVL: [1],
        MT: "info",
        MSG: "Hello, World!"
    }

Core API
--------

+-----------------------+--------------------------------------+----------------------------------------------+
| Function              | Purpose                              | Example                                      |
+=======================+======================================+==============================================+
| ``Message.log()``     | Log structured message               | ``Message.log(info="starting", count=5)``    |
+-----------------------+--------------------------------------+----------------------------------------------+
| ``start_action()``    | Begin hierarchical action            | ``with start_action("db_query", table="users")``|
+-----------------------+--------------------------------------+----------------------------------------------+
| ``start_task()``      | Create top-level action              | ``with start_task("process")``               |
+-----------------------+--------------------------------------+----------------------------------------------+
| ``log()``             | Log in current action                | ``log(message_type="event", x=1)``           |
+-----------------------+--------------------------------------+----------------------------------------------+
| ``to_file()``         | Set log output file                  | ``to_file(open("app.log", "w"))``            |
+-----------------------+--------------------------------------+----------------------------------------------+
| ``current_action()``  | Get current action context           | ``action = current_action()``                |
+-----------------------+--------------------------------------+----------------------------------------------+
| ``write_traceback()`` | Log exception traceback              | ``except: write_traceback()``                |
+-----------------------+--------------------------------------+----------------------------------------------+

LoggerX - Fluent API
--------------------

LoggerX provides a **fluent API** where all methods return ``self`` for method chaining:

.. code-block:: python

    from logxpy import log

    # Method chaining
    log.debug("starting").info("processing").success("done")

    # All level methods return self
    log.set_foreground("cyan").info("Cyan text").reset_foreground()

LoggerX Level Methods
~~~~~~~~~~~~~~~~~~~~~

+-------------------------+------------------+-----------------------------------------------+
| Method                  | Level            | Example                                       |
+=========================+==================+===============================================+
| ``log.debug()``         | DEBUG            | ``log.debug("starting", count=5)``            |
+-------------------------+------------------+-----------------------------------------------+
| ``log.info()``          | INFO             | ``log.info("user login", user="alice")``      |
+-------------------------+------------------+-----------------------------------------------+
| ``log.success()``       | SUCCESS          | ``log.success("completed", total=100)``       |
+-------------------------+------------------+-----------------------------------------------+
| ``log.note()``          | NOTE             | ``log.note("checkpoint", step=3)``            |
+-------------------------+------------------+-----------------------------------------------+
| ``log.warning()``       | WARNING          | ``log.warning("slow query", ms=5000)``        |
+-------------------------+------------------+-----------------------------------------------+
| ``log.error()``         | ERROR            | ``log.error("failed", code=500)``             |
+-------------------------+------------------+-----------------------------------------------+
| ``log.critical()``      | CRITICAL         | ``log.critical("system down")``               |
+-------------------------+------------------+-----------------------------------------------+
| ``log.checkpoint()``    | CHECKPOINT       | ``log.checkpoint("step1")``                   |
+-------------------------+------------------+-----------------------------------------------+
| ``log.exception()``     | ERROR + traceback| ``except: log.exception("error")``            |
+-------------------------+------------------+-----------------------------------------------+

LoggerX Data Type Methods
~~~~~~~~~~~~~~~~~~~~~~~~~

+---------------------+-----------------------------------+----------------------------------------+
| Method              | Purpose                           | Example                                |
+=====================+===================================+========================================+
| ``log.color()``     | Log RGB/hex colors                | ``log.color((255, 0, 0), "Theme")``    |
+---------------------+-----------------------------------+----------------------------------------+
| ``log.currency()``  | Log currency with precision       | ``log.currency("19.99", "USD")``       |
+---------------------+-----------------------------------+----------------------------------------+
| ``log.datetime()``  | Log datetime in multiple formats  | ``log.datetime(dt, "StartTime")``      |
+---------------------+-----------------------------------+----------------------------------------+
| ``log.enum()``      | Log enum with name/value          | ``log.enum(Status.ACTIVE)``            |
+---------------------+-----------------------------------+----------------------------------------+
| ``log.ptr()``       | Log object identity               | ``log.ptr(my_object)``                 |
+---------------------+-----------------------------------+----------------------------------------+
| ``log.variant()``   | Log any value with type info      | ``log.variant(data, "Input")``         |
+---------------------+-----------------------------------+----------------------------------------+
| ``log.sset()``      | Log set/frozenset                 | ``log.sset({1, 2, 3}, "Tags")``        |
+---------------------+-----------------------------------+----------------------------------------+
| ``log.df()``        | Log DataFrame                     | ``log.df(df, "Results")``              |
+---------------------+-----------------------------------+----------------------------------------+
| ``log.tensor()``    | Log Tensor                        | ``log.tensor(tensor, "Weights")``      |
+---------------------+-----------------------------------+----------------------------------------+
| ``log.json()``      | Log JSON with formatted output    | ``log.json({"key": "val"}, "Config")`` |
+---------------------+-----------------------------------+----------------------------------------+
| ``log.img()``       | Log Image                         | ``log.img(image, "Screenshot")``       |
+---------------------+-----------------------------------+----------------------------------------+
| ``log.plot()``      | Log Plot/Figure                   | ``log.plot(fig, "Chart")``             |
+---------------------+-----------------------------------+----------------------------------------+
| ``log.tree()``      | Log tree structure                | ``log.tree(data, "Hierarchy")``        |
+---------------------+-----------------------------------+----------------------------------------+
| ``log.table()``     | Log table (list of dicts)         | ``log.table(rows, "Users")``           |
+---------------------+-----------------------------------+----------------------------------------+

Color and Style Methods (for CLI Viewer)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: https://raw.githubusercontent.com/Maziar123/log-x-py/main/docs/images/logxpy-colors-demo.png
    :alt: Color Methods Demo

These methods create **colored blocks or lines** when viewed with logxpy-cli-view:

+----------------------------+-----------------------------------+---------------------------------------------------+
| Method                     | Purpose                           | Example                                           |
+============================+===================================+===================================================+
| ``log.set_foreground()``   | Set foreground color              | ``log.set_foreground("cyan")``                     |
+----------------------------+-----------------------------------+---------------------------------------------------+
| ``log.set_background()``   | Set background color              | ``log.set_background("yellow")``                   |
+----------------------------+-----------------------------------+---------------------------------------------------+
| ``log.reset_foreground()`` | Reset foreground color            | ``log.reset_foreground()``                         |
+----------------------------+-----------------------------------+---------------------------------------------------+
| ``log.reset_background()`` | Reset background color            | ``log.reset_background()``                         |
+----------------------------+-----------------------------------+---------------------------------------------------+
| ``log.colored()``          | One-shot colored message          | ``log.colored("Important!", "red", "yellow")``     |
+----------------------------+-----------------------------------+---------------------------------------------------+

**Available colors**: black, red, green, yellow, blue, magenta, cyan, white, light_gray, dark_gray, light_red, light_green, light_blue, light_yellow, light_magenta, light_cyan

Viewing Logs
------------

Use the companion **logxpy-cli-view** package to render logs as beautiful colored trees:

.. image:: https://raw.githubusercontent.com/Maziar123/log-x-py/main/docs/images/logxpy-nested-demo.png
    :alt: Nested Actions Demo

.. code-block:: bash

    pip install logxpy-cli-view
    logxpy-view app.log

Or use the standalone viewer from the examples:

.. code-block:: bash

    python examples/cli_view/complete-example-01/view_tree.py app.log

Requirements
------------

* Python 3.12 or newer (uses modern Python 3.12+ features)

Links
-----

* `Source Code <https://github.com/Maziar123/log-x-py>`_
* `Documentation <https://github.com/Maziar123/log-x-py/blob/main/README.md>`_
* `Issue Tracker <https://github.com/Maziar123/log-x-py/issues>`_

License
-------

Apache 2.0 License

---

**Python 3.12+ | Sqid Task IDs | Fluent API | Type Safe**
