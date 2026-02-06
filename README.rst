logxpy: Structured Logging with Action Tracing
===============================================

**logxpy** is a Python logging library that outputs structured, actionable logs
tracing causal chains of actions—helping you understand *why* things happened
in your application.

Why logxpy?
-----------

Python's built-in ``logging`` and similar systems output a stream of factoids:
they're interesting, but hard to trace.

* Why is your application slow?
* What caused this code path to be chosen?
* Why did this error happen?

Standard logging can't answer these questions easily.

With **logxpy**, you get **causal chains of actions**: actions can spawn other
actions, and eventually they either **succeed or fail**. The resulting logs tell
you the story of what your software did.

Features
--------

* **Structured Logging** - JSON output for easy parsing and analysis
* **Action Tracing** - Track operations from start to finish with timing
* **Hierarchical Tasks** - Nested actions show the full call chain
* **Python 3.12+ Ready** - Built with modern Python features
* **Async Support** - Works with asyncio and async/await patterns
* **Type Safety** - Full type hints throughout

Quick Start
-----------

Install logxpy::

    pip install logxpy

Basic usage::

    from logxpy import start_action, Message, to_file

    # Output to a file
    to_file(open("app.log", "w"))

    # Log messages
    Message.log(message_type="app:startup", version="1.0.0")

    # Trace actions
    with start_action(action_type="http:request", method="POST", path="/api/users"):
        with start_action(action_type="database:query", table="users"):
            Message.log(message_type="database:result", rows=10)

Output is structured JSON that's easy to parse, visualize, and analyze.

Core API
--------

.. list-table:: Core Logging Functions
   :header-rows: 1
   :widths: 30 40 30

   * - Function
     - Purpose
     - Example
   * - ``Message.log(**fields)``
     - Log structured message
     - ``Message.log(info="starting")``
   * - ``start_action(action_type, **fields)``
     - Begin hierarchical action
     - ``with start_action("db_query"):``
   * - ``start_task(action_type, **fields)``
     - Create top-level action
     - ``with start_task("process"):``
   * - ``log(message_type, **fields)``
     - Log in current action
     - ``log(message_type="event")``
   * - ``to_file(output_file)``
     - Set log output file
     - ``to_file(open("app.log", "w"))``
   * - ``current_action()``
     - Get current action context
     - ``action = current_action()``
   * - ``write_traceback()``
     - Log exception traceback
     - ``except: write_traceback()``

LoggerX Level Methods
---------------------

.. list-table:: Logging Level Methods
   :header-rows: 1
   :widths: 30 15 55

   * - Method
     - Level
     - Example
   * - ``log.debug(msg, **fields)``
     - DEBUG
     - ``log.debug("starting", count=5)``
   * - ``log.info(msg, **fields)``
     - INFO
     - ``log.info("user login", user="alice")``
   * - ``log.success(msg, **fields)``
     - SUCCESS
     - ``log.success("completed", total=100)``
   * - ``log.note(msg, **fields)``
     - NOTE
     - ``log.note("checkpoint", step=3)``
   * - ``log.warning(msg, **fields)``
     - WARNING
     - ``log.warning("slow query", ms=5000)``
   * - ``log.error(msg, **fields)``
     - ERROR
     - ``log.error("failed", code=500)``
   * - ``log.critical(msg, **fields)``
     - CRITICAL
     - ``log.critical("system down")``
   * - ``log.checkpoint(msg, **fields)``
     - CHECKPOINT
     - ``log.checkpoint("step1")``
   * - ``log.exception(msg, **fields)``
     - ERROR + traceback
     - ``except: log.exception("error")``

Decorators
----------

.. list-table:: Logging Decorators
   :header-rows: 1
   :widths: 30 40 30

   * - Decorator
     - Purpose
     - Example
   * - ``@logged(level, ...)``
     - Universal logging decorator
     - ``@logged(level="DEBUG")``
   * - ``@timed(metric)``
     - Timing-only decorator
     - ``@timed("db.query")``
   * - ``@retry(attempts, delay)``
     - Retry with backoff
     - ``@retry(attempts=5)``
   * - ``@log_call(action_type)``
     - Log function calls
     - ``@log_call(action_type="func")``

System Message Types
--------------------

.. list-table:: Built-in Message Types
   :header-rows: 1
   :widths: 40 60

   * - Message Type
     - Purpose
   * - ``eliot:traceback``
     - Exception traceback logging
   * - ``loggerx:debug``
     - Debug level messages
   * - ``loggerx:info``
     - Info level messages
   * - ``loggerx:success``
     - Success level messages
   * - ``loggerx:warning``
     - Warning level messages
   * - ``loggerx:error``
     - Error level messages
   * - ``loggerx:critical``
     - Critical level messages

Viewing Logs
------------

Use the companion ``logxpy-cli-view`` package to render logs as beautiful
colored trees::

    pip install logxpy-cli-view
    logxpy-cli-view app.log

Or use the standalone viewer from the examples::

    python examples-log-view/view_tree.py app.log

CLI Commands
------------

.. list-table:: CLI Commands
   :header-rows: 1
   :widths: 50 50

   * - Command
     - Description
   * - ``logxpy-view <file>``
     - View log as tree
   * - ``logxpy-view <file> --failed``
     - Show only failed actions
   * - ``logxpy-view <file> --filter "db_*"``
     - Filter by action name
   * - ``logxpy-view <file> --export json``
     - Export as JSON
   * - ``logxpy-view <file> --export csv``
     - Export as CSV
   * - ``logxpy-view <file> --export html``
     - Export as HTML
   * - ``logxpy-view <file> --tail``
     - Live log monitoring
   * - ``logxpy-view <file> --stats``
     - Show statistics

Filter Functions
----------------

.. list-table:: Filter Functions
   :header-rows: 1
   :widths: 50 50

   * - Function
     - Purpose
   * - ``filter_by_action_status(tasks, status)``
     - Filter by status (succeeded/failed)
   * - ``filter_by_action_type(tasks, pattern)``
     - Filter by action name pattern
   * - ``filter_by_duration(tasks, min_seconds)``
     - Filter by duration range
   * - ``filter_by_keyword(tasks, keyword)``
     - Search in values
   * - ``filter_by_jmespath(tasks, query)``
     - JMESPath query filter

Export Functions
----------------

.. list-table:: Export Functions
   :header-rows: 1
   :widths: 40 60

   * - Function
     - Purpose
   * - ``export_json(tasks, file)``
     - Export as JSON
   * - ``export_csv(tasks, file)``
     - Export as CSV
   * - ``export_html(tasks, file)``
     - Export as HTML
   * - ``export_logfmt(tasks, file)``
     - Export as logfmt

Requirements
------------

* Python 3.9 or newer (including PyPy3)

Links
-----

* `Documentation <https://github.com/logxpy/logxpy/>`_
* `Issue Tracker <https://github.com/logxpy/logxpy/issues>`_

License
-------

Apache 2.0 License
