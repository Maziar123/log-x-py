log-x-py: Modern Structured Logging Ecosystem
===============================================

**Structured logging library with Sqid task IDs, fluent API, tree viewer, and log parser.**

.. image:: https://img.shields.io/badge/python-3.12+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.12+

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :alt: License

----

Features
========

* **High Performance** - 140,000+ logs/sec with async logging
* **Sqid Task IDs** - 89% smaller than UUID4 (4-12 chars vs 36)
* **Fluent API** - Method chaining for clean code
* **Structured** - JSON output with compact field names
* **Colored Output** - ANSI colors and emoji indicators
* **Powerful Filtering** - JMESPath, date ranges, action types
* **Analytics** - Statistics, time series, anomaly detection
* **Minimal Dependencies** - Uses boltons

Quick Start
===========

Install::

    pip install logxpy logxpy-cli-view

Basic usage::

    from logxpy import log
    
    log.init()              # Auto-generate filename
    log.info("Hello!")      # Simple logging
    log.success("Done")     # Success message

View logs::

    logxpy-view script.log

Async Logging
=============

**Configurable flush modes:**

Timer-Based::

    log.init("app.log", flush=0.1)  # Flush every 100ms

Size-Based::

    log.init("app.log", size=500)   # Flush every 500 messages

On-Demand::

    log.init("app.log")
    log.info("Critical")
    log.flush()  # Force immediate

Sync Mode::

    with log.sync_mode():
        log.critical("Blocks until written")

Backpressure Policies
---------------------

========= ================================= =================================
Policy    Behavior                          Use Case
========= ================================= =================================
block     Pause until written (default)     No data loss
replace   Replace oldest pending            Fixed memory
skip      Skip new message                  Overflow OK
warn      Skip + warning                    Debug
========= ================================= =================================

Components
==========

logxpy - Logging Library
------------------------

**Sqid Task IDs:**

+-----------+------------------+--------+
| Format    | Example          | Length |
+===========+==================+========+
| Root      | ``"Xa.1"``       | 4 chars|
+-----------+------------------+--------+
| Child     | ``"Xa.1.1"``     | 6 chars|
+-----------+------------------+--------+
| Deep      | ``"Xa.1.1.2"``   | 8 chars|
+-----------+------------------+--------+

**Fluent API:**

.. code-block:: python

    # Method chaining
    log.debug("starting").info("processing").success("done")
    
    # With fields
    log.info("User action", user_id=123, action="login")
    
    # Context
    with log.scope(user_id=123):
        log.info("Processing")

logxpy-cli-view - Tree Viewer
------------------------------

**Render logs as colored ASCII trees:**

.. code-block:: bash

    # View
    logxpy-view app.log
    
    # Filter
    logxpy-view --status failed app.log
    logxpy-view --action-type "db:*" app.log
    
    # Export
    logxpy-view export -f json -o out.json app.log

logxy-log-parser - Log Analyzer
--------------------------------

**Parse and analyze logs:**

.. code-block:: python

    from logxy_log_parser import parse_log, analyze_log
    
    entries = parse_log("app.log")
    report = analyze_log("app.log")
    report.print_summary()

Documentation
=============

* `GUIDE.md`_ - Complete usage guide
* `FLUSH_TECHNIQUES.md`_ - Flush mechanisms deep dive
* `AGENTS.md`_ - Developer guide
* `logxpy-api-reference.html`_ - Full API reference

.. _GUIDE.md: ./GUIDE.md
.. _FLUSH_TECHNIQUES.md: ./FLUSH_TECHNIQUES.md
.. _AGENTS.md: ./AGENTS.md
.. _logxpy-api-reference.html: ./logxpy-api-reference.html

Requirements
============

* Python 3.12 or newer

License
=======

MIT License

----

**Python 3.12+ | Sqid Task IDs | Fluent API | Async Logging**
