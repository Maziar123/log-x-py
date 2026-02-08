logxpy: Structured Logging with Action Tracing
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
* **Color Support** - Foreground/background colors for log entries (rendered by logxpy-cli-view)
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

Color Support
-------------

LogXPy supports foreground/background colors that render beautifully in the CLI viewer::

    from logxpy import log

    # Set foreground color for subsequent messages
    log.set_foreground("cyan")
    log.info("This renders with cyan text")
    log.reset_foreground()

    # Set background color
    log.set_background("yellow")
    log.warning("Yellow background warning")
    log.reset_background()

    # Combined colors
    log.set_foreground("white").set_background("red")
    log.error("White text on red background")
    log.reset_foreground().reset_background()

    # One-shot colored message for highlighted blocks
    log.colored(
        "╔═══════════════════════════════════╗\n"
        "║  ⚠️  IMPORTANT HIGHLIGHTED BLOCK  ║\n"
        "╚═══════════════════════════════════╝",
        foreground="black",
        background="yellow"
    )

Available colors: black, red, green, yellow, blue, magenta, cyan, white, light_cyan, dark_gray, light_gray

Viewing Logs
------------

Use the companion ``logxpy-cli-view`` package to render logs as beautiful
colored trees::

    pip install logxpy-cli-view
    logxpy-view app.log

Or use the standalone viewer from the examples::

    python examples-log-view/view_tree.py app.log

LoggerX API
-----------

LogXPy provides a modern LoggerX class with fluent API::

    from logxpy import log

    # Level methods (return self for chaining)
    log.debug("Debug message", count=5)
    log.info("User login", user="alice")
    log.success("Operation completed", total=100)
    log.note("Checkpoint reached", step=3)
    log.warning("Slow query", ms=5000)
    log.error("Request failed", code=500)
    log.critical("System down")

    # Data type methods
    log.color((255, 0, 0), "Theme Color")
    log.currency("19.99", "USD")
    log.datetime(dt, "Start Time")
    log.enum(Status.ACTIVE)
    log.ptr(my_object)
    log.variant(data, "Input")
    log.sset({1, 2, 3}, "Tags")

    # System methods
    log.system_info()
    log.memory_status()
    log.stack_trace(limit=10)

    # File/stream methods
    log.file_hex("data.bin")
    log.file_text("app.log")
    log.memory_hex(buffer)
    log.stream_hex(bio)
    log.stream_text(io)

Requirements
------------

* Python 3.12 or newer (uses modern Python 3.12+ features)

Links
-----

* `Documentation <https://github.com/logxpy/logxpy/>`_
* `Issue Tracker <https://github.com/logxpy/logxpy/issues>`_

License
-------

Apache 2.0 License
