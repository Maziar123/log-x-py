logxpy: High-Performance Structured Logging with Async Support
===============================================

**logxpy** is a Python logging library that outputs structured, actionable logs
tracing causal chains of actions—helping you understand *why* things happened
in your application.

The **log-x-py** project consists of three components:

* **logxpy** - Zero-dependency structured logging library (Python 3.12+)
* **logxpy-cli-view** - Colored tree viewer for logs
* **logxy-log-parser** - Log parsing, analysis, and monitoring library

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
* **Async Threaded Logging** - 140K+ logs/sec with background writer thread
* **Asyncio Support** - Works with asyncio and async/await patterns
* **Type Safety** - Full type hints throughout

---
## Component 1: logxpy (Logging Library)
---------------------------------------

### Installation

Install logxpy::

    pip install logxpy

### Quick Start

.. code-block:: python

    from logxpy import start_action, Message, to_file

    # Output to a file
    to_file(open("app.log", "w"))

    # Log messages
    Message.log(message_type="app:startup", version="1.0.0")

    # Trace actions
    with start_action(action_type="http:request", method="POST", path="/api/users"):
        with start_action(action_type="database:query", table="users"):
            Message.log(message_type="database:result", rows=10)

### Core API

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

### LoggerX Level Methods

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

### LoggerX Data Type Methods (Clean API)

.. list-table:: Data Type Logging Methods
   :header-rows: 1
   :widths: 30 40 30

   * - Method
     - Purpose
     - Example
   * - ``log.color(value, title)``
     - Log RGB/hex colors
     - ``log.color((255, 0, 0), "Theme")``
   * - ``log.currency(amount, code)``
     - Log currency with precision
     - ``log.currency("19.99", "USD")``
   * - ``log.datetime(dt, title)``
     - Log datetime in multiple formats
     - ``log.datetime(dt, "StartTime")``
   * - ``log.enum(enum_value, title)``
     - Log enum with name/value
     - ``log.enum(Status.ACTIVE)``
   * - ``log.ptr(obj, title)``
     - Log object identity
     - ``log.ptr(my_object)``
   * - ``log.variant(value, title)``
     - Log any value with type info
     - ``log.variant(data, "Input")``
   * - ``log.sset(s, title)``
     - Log set/frozenset
     - ``log.sset({1, 2, 3}, "Tags")``
   * - ``log.system_info()``
     - Log OS/platform info
     - ``log.system_info()``
   * - ``log.memory_status()``
     - Log memory statistics
     - ``log.memory_status()``
   * - ``log.memory_hex(data)``
     - Log bytes as hex dump
     - ``log.memory_hex(buffer)``
   * - ``log.stack_trace(limit)``
     - Log current call stack
     - ``log.stack_trace(limit=10)``
   * - ``log.file_hex(path)``
     - Log file as hex dump
     - ``log.file_hex("data.bin")``
   * - ``log.file_text(path)``
     - Log text file contents
     - ``log.file_text("app.log")``
   * - ``log.stream_hex(stream)``
     - Log binary stream as hex
     - ``log.stream_hex(bio)``
   * - ``log.stream_text(stream)``
     - Log text stream contents
     - ``log.stream_text(io)``

### Decorators

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

### System Message Types

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

---
## Component 2: logxpy-cli-view (Tree Viewer)
--------------------------------------------

### Installation

Install logxpy-cli-view::

    pip install logxpy-cli-view

### Quick Start

.. code-block:: bash

    # View logs as tree
    logxpy-view app.log

### CLI Commands

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

### Filter Functions

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

### Export Functions

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

---
## Component 3: logxy-log-parser (Log Parser & Analyzer)
--------------------------------------------------------

### Installation

Install logxy-log-parser::

    pip install logxy-log-parser

### Quick Start

.. code-block:: python

    from logxy_log_parser import parse_log, check_log, analyze_log

    # One-line parsing
    entries = parse_log("app.log")

    # Parse + validate
    result = check_log("app.log")
    print(f"Valid: {result.is_valid}, Entries: {result.entry_count}")

    # Full analysis
    report = analyze_log("app.log")
    report.print_summary()

### Core Classes

.. list-table:: Core Classes
   :header-rows: 1
   :widths: 30 70

   * - Class
     - Purpose
   * - ``LogFile``
     - File handle + real-time monitoring
   * - ``LogParser``
     - Parse log files
   * - ``LogEntries``
     - Collection with filtering/export
   * - ``LogFilter``
     - Chainable filters
   * - ``LogAnalyzer``
     - Performance/error analysis
   * - ``TaskTree``
     - Hierarchical task tree

### LogFile API (Real-time Monitoring)

.. list-table:: LogFile API
   :header-rows: 1
   :widths: 40 60

   * - Method
     - Purpose
   * - ``LogFile.open(path)``
     - Open and validate
   * - ``logfile.entry_count``
     - Get entry count (fast)
   * - ``logfile.contains_error()``
     - Check for errors
   * - ``logfile.watch()``
     - Iterate new entries
   * - ``logfile.wait_for_message(text, timeout)``
     - Wait for message
   * - ``logfile.wait_for_error(timeout)``
     - Wait for error

### Filter Methods

.. list-table:: Filter Methods
   :header-rows: 1
   :widths: 40 60

   * - Method
     - Purpose
   * - ``by_level(*levels)``
     - Filter by log level
   * - ``by_message(pattern)``
     - Filter by message text
   * - ``by_time_range(start, end)``
     - Filter by time range
   * - ``by_task_uuid(*uuids)``
     - Filter by task UUID
   * - ``by_action_type(*types)``
     - Filter by action type
   * - ``by_field(field, value)``
     - Filter by field value
   * - ``by_duration(min, max)``
     - Filter by duration
   * - ``with_traceback()``
     - Entries with tracebacks
   * - ``failed_actions()``
     - Failed actions only
   * - ``slow_actions(threshold)``
     - Slow actions only

---
## Installation
------------

Install all three components::

    pip install logxpy logxpy-cli-view logxy-log-parser

Or install from source::

    # Library
    cd logxpy && pip install -e .

    # Viewer
    cd logxpy_cli_view && pip install -e .

    # Parser
    cd logxy-log-parser && pip install -e .

---
## Requirements
------------

* **logxpy**: Python 3.9 or newer (3.12+ recommended for modern features)
* **logxpy-cli-view**: Python 3.9 or newer
* **logxy-log-parser**: Python 3.12 or newer

---
## Links
-----

* `Documentation <https://github.com/logxpy/logxpy/>`_
* `Issue Tracker <https://github.com/logxpy/logxpy/issues>`_

---
## License
-------

Apache 2.0 License
