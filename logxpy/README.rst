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

Viewing Logs
------------

Use the companion ``logxpy-cli-view`` package to render logs as beautiful
colored trees::

    pip install logxpy-cli-view
    logxpy-cli-view app.log

Or use the standalone viewer from the examples::

    python examples-log-view/view_tree.py app.log

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
