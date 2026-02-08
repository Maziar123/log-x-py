#!/usr/bin/env python3
"""Comprehensive logxpy sample - demonstrates all 14 API categories.

Categories: Basic Messages, Method Tracing, Errors, System/Memory, File/Stream,
Data Types, Component/Object, Conditional/Formatted, Checkpoints, Categories,
XML, Registry/Version, Write Methods, logxpy-Specific Features.

Usage: python example_09_comprehensive.py && python view_tree.py example_09_comprehensive.log
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "logxpy"))

from logxpy import (  # noqa: E402
    ActionType, CategorizedLogger, Field, MessageType, aaction,
    category_context, get_current_category, log,
    set_category, start_action, start_task, write_traceback,
)

# Import all demo data from separate module
from demo_data_01 import (  # noqa: E402
    Color, Status, DemoObject, UserProfile,
    SAMPLE_TAGS, SAMPLE_IDS, SAMPLE_COLOR_RGB, SAMPLE_COLOR_HEX,
    SAMPLE_CURRENCY_AMOUNT, SAMPLE_CURRENCY_STRING, SAMPLE_DATETIME,
    SAMPLE_POINTER_OBJ, SAMPLE_VARIANT_LIST, SAMPLE_VARIANT_DICT,
    DEBUG_MODE, SAMPLE_COUNT, SAMPLE_USER, SAMPLE_SCORE,
    SAMPLE_ITEMS, SAMPLE_BINARY_BUFFER, SAMPLE_XML_STRING, SAMPLE_XML_SUMMARY,
    TempFiles, create_binary_stream, create_text_stream,
    sample_async_operation, create_retry_simulator,
    DEMO_OBJECT, USER_PROFILE,
)

try:
    from logxpy.decorators import logged, retry, timed, generator, aiterator, trace
except ImportError:
    from collections.abc import Callable
    from typing import Any, TypeVar
    F = TypeVar('F', bound=Callable[..., Any])
    def logged(fn: F | None = None, **_kw: Any) -> Any:
        def decorator(f: F) -> F:
            return f
        return decorator(fn) if fn else decorator
    def timed(fn: F | None = None, **_kw: Any) -> Any:
        def decorator(f: F) -> F:
            return f
        return decorator(fn) if fn else decorator
    def retry(fn: F | None = None, **_kw: Any) -> Any:
        def decorator(f: F) -> F:
            return f
        return decorator(fn) if fn else decorator


def demo_basic_messages() -> None:
    """Category 1: 📨 Basic Message Sending - log.info(), log.debug(), log.send(), log.note()."""
    log.info("Hello World", source="basic_messages")
    log.debug("Debug information", detail="verbose output")
    log.send("User", {"name": "John", "id": 12345})
    log.note("This is a note message")
    log.info("custom_event", event_data="sample", category="basic")


def demo_method_tracing() -> None:
    """Category 2: 🔍 Method Tracing - start_action(), @logged."""
    with start_action(action_type="database:query", table="users") as action:
        log.info("Executing query", sql="SELECT * FROM users")
        action.add_success_fields(rows_found=42, duration_ms=15)

    @logged(level="INFO", capture_args=True, capture_result=True)
    def process_data(x: int, y: int) -> int:
        return x + y
    process_data(10, 20)

    @logged(level="DEBUG", capture_args=True)
    def helper(name: str) -> str:
        return f"Hello, {name}"
    helper("World")


def demo_errors_warnings() -> None:
    """Category 3: ⚠️ Error & Warning - log.error(), log.warning(), log.critical(), write_traceback()."""
    log.error("Connection failed", code=500, retry_count=3)
    log.error("Database error", sql="SELECT * FROM missing_table", error_code="42P01")
    log.critical("System crash imminent", memory_usage="98%", pid=1234)
    log.warning("Low memory warning", available_mb=512, threshold_mb=1024)

    try:
        1 / 0
    except ZeroDivisionError:
        write_traceback()

    try:
        raise ValueError("Invalid input")
    except ValueError:
        log.exception("Caught ValueError", context="demo_errors_warnings")


def demo_system_memory() -> None:
    """Category 4: 💻 System & Memory - log.system_info(), log.memory_status(), log.memory_hex(), log.stack_trace()."""
    log.system_info()
    log.memory_status()
    log.memory_hex(SAMPLE_BINARY_BUFFER, "Memory Buffer", max_size=128)
    log.stack_trace("Call Stack", limit=5)


def demo_file_stream() -> None:
    """Category 5: 📁 File & Stream - log.file_hex(), log.file_text(), log.stream_hex(), log.stream_text()."""
    with TempFiles() as files:
        log.file_hex(files.binary_path, "Binary File", max_size=64)
        log.file_text(files.text_path, "Text File", max_lines=100, encoding='utf-8')
        log.stream_hex(create_binary_stream(), "Binary Stream", max_size=32)
        log.stream_text(create_text_stream(), "Text Stream", max_lines=3)


def demo_data_types() -> None:
    """Category 6: 📊 Data Types - log.color(), log.currency(), log.datetime(), log.enum(), log.ptr(), log.sset(), log.variant()."""
    log.color(SAMPLE_COLOR_RGB, 'Theme')
    log.color(SAMPLE_COLOR_HEX, 'Background')
    log.currency(SAMPLE_CURRENCY_AMOUNT, 'USD', 'Price')
    log.currency(SAMPLE_CURRENCY_STRING, 'USD', 'Total')
    log.datetime(SAMPLE_DATETIME, 'StartTime')
    log.datetime(title='Current')  # Uses datetime.now()
    if DEBUG_MODE:
        log.datetime(SAMPLE_DATETIME, 'DebugTime')
    # Skipped when False - Pythonic: use simple if statement
    log.enum(Color.GREEN, 'Color')
    log.enum(Status.ACTIVE, 'Status')
    log.sset(SAMPLE_TAGS, 'Tags')
    log.sset(SAMPLE_IDS, 'Ids')
    log.ptr(SAMPLE_POINTER_OBJ, 'SampleObject')
    log.variant(SAMPLE_VARIANT_LIST, 'Variant1')
    log.variant(SAMPLE_VARIANT_DICT, 'Variant2')


def demo_component_object() -> None:
    """Category 7: 🔧 Component & Object - vars(), dir(), repr(), getattr(), list()."""
    log.send('ObjectProperties', vars(DEMO_OBJECT))
    public_attrs = [a for a in dir(DEMO_OBJECT) if not a.startswith('_')]
    log.send('PublicAttributes', public_attrs)
    log.send('ObjectRepr', repr(DEMO_OBJECT))
    attr_value = getattr(DEMO_OBJECT, 'name')
    log.send('DynamicProperty', {'name': attr_value})
    log.send('CollectionItems', list(SAMPLE_ITEMS.items()))


def demo_conditional_formatted() -> None:
    """Category 8: 🎯 Conditional & Formatted - if statements, log.if_(), f-strings."""
    # Simple Python if - most flexible
    if DEBUG_MODE:
        log('DebugInfo', {'value': SAMPLE_COUNT, 'threshold': 100})
    if SAMPLE_COUNT > 0:
        log('PositiveCount', {'count': SAMPLE_COUNT})
    
    # Using log() callable with condition
    if "I exist":
        log('AssignedValue', {'value': "I exist", 'type': 'string'})
    # None check skipped - Pythonic way
    
    # Formatted messages - f-strings are preferred
    log('Formatted', {
        'message': f"User: Alice, ID: {12345}",
        'template': "User: {}, ID: {}"
    })
    log('Formatted', {
        'message': f"Value: {3.14159:.2f}",
        'template': "Value: {:.2f}"
    })
    log.info(f"User {SAMPLE_USER} scored {SAMPLE_SCORE:.1f}%")


def demo_checkpoints() -> None:
    """Category 9: 🚩 Checkpoints - log.checkpoint(), manual separators."""
    log.checkpoint('Initialization complete')
    log.checkpoint('Data loaded')
    log.checkpoint('Processing started')
    log.info('=' * 50)
    log.info('--- SECTION BREAK ---')
    log.info('=' * 50)
    log.checkpoint('Processing complete')


def demo_category_management() -> None:
    """Category 10: 🏷️ Category Management - CategorizedLogger(), category_context(), set_category()."""
    _ = CategorizedLogger('Database')
    with category_context('Network'):
        log.info('Network operation', operation='connect')
        current = get_current_category()
        log.info('Current category', category=current)
    log.info('Back to default category')
    set_category('Security')
    log.info('Security event', event='login_attempt')
    set_category(None)


def demo_xml_data() -> None:
    """Category 11: 📄 XML Data - xml.etree + log.send()."""
    log.send('ConfigXML', SAMPLE_XML_STRING)
    log.send('ParsedXML', SAMPLE_XML_SUMMARY)


def demo_registry_version() -> None:
    """Category 12: 🗄️ Registry & Version - importlib.metadata.version()."""
    try:
        from importlib.metadata import version as get_version
        try:
            logxpy_version = get_version('logxpy')
            log.send('PackageVersion', {'package': 'logxpy', 'version': logxpy_version})
        except (ImportError, ValueError):
            log.info('logxpy version not available')
    except (ImportError, ModuleNotFoundError):
        log.info('importlib.metadata not available')
    log.send('PythonVersion', {
        'version': sys.version,
        'version_info': sys.version_info[:3],
        'platform': sys.platform
    })


def demo_write_methods() -> None:
    """Category 13: ✍️ Write Methods - log() callable, log.send() with timestamps."""
    log('Simple message via log()')
    log('Auto-titled data', {'key': 'value'})
    log({'raw': 'data'})
    log.info('Another timestamped message', category='demo')
    log.color(SAMPLE_COLOR_HEX, 'ColorValue')
    log.currency(SAMPLE_CURRENCY_AMOUNT, 'USD', 'CurrencyValue')
    log.datetime(SAMPLE_DATETIME, 'DateTimeValue')


async def async_operation() -> str:
    await asyncio.sleep(0.01)
    return "async result"


def demo_decorators() -> None:
    """Category 14: 🎨 Decorators - @logged, @timed, @retry, @generator, @aiterator, @trace."""
    
    # @logged - Universal logging decorator (most comprehensive)
    @logged(level="INFO", capture_args=True, capture_result=True, exclude={"password"})
    def process_user_login(username: str, password: str, ip_address: str) -> dict:
        """Demonstrates @logged with sensitive field masking."""
        return {"user_id": 12345, "status": "authenticated", "ip": ip_address}
    
    result = process_user_login("alice", "secret123", "192.168.1.100")
    log.info('Logged decorator completed', result=result)
    
    # @logged - Another example with timer disabled
    @logged(level="INFO", capture_args=True, timer=False)
    def legacy_function(x: int, y: int) -> int:
        """Demonstrates @logged with timer disabled."""
        return x * y
    
    legacy_result = legacy_function(10, 20)
    log.info('Legacy function completed', result=legacy_result)
    
    # @timed - Timing-only decorator (lightweight)
    @timed("database.query_time")
    def simulate_database_query() -> list:
        """Demonstrates @timed for performance monitoring."""
        import time
        time.sleep(0.01)  # Simulate 10ms query
        return [{"id": 1, "data": "result"}]
    
    query_results = simulate_database_query()
    log.info('Timed query completed', rows=len(query_results))
    
    # @retry - Retry with exponential backoff
    attempt_counter = {"count": 0}
    
    @retry(attempts=3, delay=0.01, backoff=2.0)
    def flaky_network_call() -> str:
        """Demonstrates @retry with simulated failures."""
        attempt_counter["count"] += 1
        if attempt_counter["count"] < 3:
            raise ConnectionError(f"Simulated network error (attempt {attempt_counter['count']})")
        return "success_after_retries"
    
    try:
        retry_result = flaky_network_call()
        log.info('Retry decorator succeeded', result=retry_result, attempts=attempt_counter["count"])
    except ConnectionError:
        log.error('Retry decorator failed after all attempts')
    
    # @generator - Generator progress tracking
    @generator(name="batch_processor", every=50)
    def process_batch_items(count: int):
        """Demonstrates @generator for progress tracking."""
        for i in range(count):
            yield {"item_id": i, "processed": True}
    
    processed = list(process_batch_items(120))  # Will log at 50, 100
    log.info('Generator processing complete', total_items=len(processed))
    
    # @aiterator - Async iterator progress tracking
    @aiterator(name="async_fetcher", every=30)
    async def fetch_async_items(count: int):
        """Demonstrates @aiterator for async iteration."""
        for i in range(count):
            await asyncio.sleep(0.001)  # Simulate async work
            yield {"async_id": i, "fetched": True}
    
    async def run_async_iterator():
        async_items = []
        async for item in fetch_async_items(75):  # Will log at 30, 60
            async_items.append(item)
        return async_items
    
    async_results = asyncio.run(run_async_iterator())
    log.info('Async iterator complete', total_items=len(async_results))
    
    # @trace - OpenTelemetry tracing (gracefully degrades if OTel not installed)
    @trace(name="payment_process", kind="internal", attributes={"service": "billing"})
    def process_payment(order_id: str, amount: float) -> dict:
        """Demonstrates @trace for distributed tracing."""
        return {"transaction_id": f"TX-{order_id}", "amount": amount, "status": "completed"}
    
    payment_result = process_payment("ORD-12345", 99.99)
    log.info('Trace decorator completed', payment=payment_result)
    
    # Combining multiple decorators (deterministic - no random failures)
    call_count = {"count": 0}
    
    @logged(level="DEBUG", capture_args=True, capture_result=True)
    @timed("combined_operation")
    @retry(attempts=3, delay=0.01)
    def combined_decorator_example(value: int) -> dict:
        """Demonstrates stacking @logged, @timed, and @retry."""
        call_count["count"] += 1
        # Fail first 2 times, succeed on 3rd
        if call_count["count"] < 3:
            raise RuntimeError(f"Simulated failure (attempt {call_count['count']})")
        return {"input": value, "output": value * 2, "transformed": True}
    
    combined_result = combined_decorator_example(42)
    log.info('Combined decorators completed', result=combined_result, attempts=call_count["count"])


def demo_logxpy_specific() -> None:
    """Category 15: 🚀 logxpy-Specific - start_task(), aaction(), MessageType, ActionType, Field."""
    with start_task(action_type='main_application', version='1.0.0') as task:
        log.info('Task started', task_uuid=task.task_uuid)

        @timed(metric="timed_operation")
        def slow_operation():
            import time
            time.sleep(0.01)
            return "done"
        slow_operation()

        simulator = create_retry_simulator(fail_count=3)
        @retry(attempts=3, delay=0.01, backoff=2.0)
        def flaky_operation():
            return simulator()
        try:
            flaky_operation()
        except ConnectionError:
            pass

    async def run_async_demo():
        async with aaction(action_type='async_fetch', url='http://example.com'):
            result = await sample_async_operation()
            log.info('Async operation complete', result=result)
    asyncio.run(run_async_demo())

    try:
        user_login = MessageType(
            "user:login",
            [Field("username", str), Field("success", bool)],
            "User login event"
        )
        user_login.log(username='alice', success=True)
        log.info('MessageType logging succeeded')
    except (AttributeError, TypeError) as e:
        log.error('MessageType logging failed', error=str(e))

    try:
        db_query = ActionType(
            "db:query",
            [Field("table", str), Field("query", str)],
            [],
            "Database query action"
        )
        with db_query(table='users', query='SELECT *'):
            log.info('ActionType context succeeded')
    except (AttributeError, TypeError) as e:
        log.error('ActionType failed', error=str(e))

    _ = Field("username", str)
    log.info('Field created', field_name='username', serializer='str')


def demo_colors_for_viewer() -> None:
    """Category 16: 🎨 Color Demo - log.set_foreground() / log.set_background() methods."""
    # Method 1: Using set_foreground / set_background for sections
    log.set_foreground("cyan")
    log.info("This message has CYAN foreground (via set_foreground)")
    log.info("This also has cyan foreground (context persists)")
    log.reset_foreground()
    log.info("Back to normal foreground")
    
    # Method 2: Using set_background
    log.set_background("blue")
    log.info("This message has BLUE background")
    log.warning("Warning also has blue background")
    log.reset_background()
    
    # Method 3: Combined foreground + background
    log.set_foreground("white").set_background("red")
    log.error("White text on RED background - ERROR style")
    log.reset_foreground().reset_background()
    
    # Method 4: One-shot colored() method
    log.colored("One-shot colored message", foreground="yellow", background="black")
    log.colored("Green on black", foreground="green", background="black", priority="high")
    log.colored("Magenta highlight", foreground="magenta", background="white")
    
    # HIGHLIGHT BLOCK: Yellow background + Black font (classic warning highlight)
    # Using single multiline message for continuous block effect
    log.colored(
        "╔══════════════════════════════════════════════════════════════════╗\n"
        "║  ⚠️  IMPORTANT WARNING: Yellow background with BLACK font        ║\n"
        "║     This is a highlighted block for critical attention           ║\n"
        "╚══════════════════════════════════════════════════════════════════╝",
        foreground="black",
        background="yellow"
    )
    
    # Method 5: Context-based colors (affects all subsequent logs)
    log.set_foreground("light_cyan")
    log.info("Light cyan text 1")
    log.info("Light cyan text 2")
    log.set_background("dark_gray")
    log.info("Light cyan on dark gray")
    log.reset_foreground().reset_background()
    log.info("Back to default colors")


def main() -> None:
    """Run all 14 category demonstrations."""
    log.init(mode='w')

    log.info('Starting comprehensive logxpy demonstration')
    log.info('=' * 60)

    demo_basic_messages()
    demo_method_tracing()
    demo_errors_warnings()
    demo_system_memory()
    demo_file_stream()
    demo_data_types()
    demo_component_object()
    demo_conditional_formatted()
    demo_checkpoints()
    demo_category_management()
    demo_xml_data()
    demo_registry_version()
    demo_write_methods()
    demo_decorators()
    demo_logxpy_specific()
    demo_colors_for_viewer()  # 4+ foreground/background colors

    log.info('=' * 60)
    log.info('Comprehensive demonstration complete', categories=15)
    print(f"Log written to: {log._auto_log_file}")
    print(f"View with: python view_tree.py {log._auto_log_file}")


if __name__ == '__main__':
    main()
