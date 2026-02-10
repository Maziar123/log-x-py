# LogXPy Examples

Examples demonstrating the **logxpy** structured logging library.

## Quick Start

```bash
# Run basic logging example
python 01_simple_logging.py

# Run decorators example
python 02_decorators.py
```

## Core Examples (01-10)

| # | File | Description |
|---|------|-------------|
| 01 | [01_simple_logging.py](01_simple_logging.py) | Basic message logging with Message.log() |
| 02 | [02_decorators.py](02_decorators.py) | Using @logged, @timed, @retry decorators |
| 03 | [03_context_scopes.py](03_context_scopes.py) | Context management with log.scope() |
| 04 | [04_async_tasks.py](04_async_tasks.py) | Async task logging |
| 05 | [05_error_handling.py](05_error_handling.py) | Exception handling and tracebacks |
| 06 | [06_data_types.py](06_data_types.py) | Logging various data types |
| 07 | [07_generators_iterators.py](07_generators_iterators.py) | Generator and iterator logging |
| 08 | [08_tracing_opentelemetry.py](08_tracing_opentelemetry.py) | OpenTelemetry span integration |
| 09 | [09_configuration.py](09_configuration.py) | Configuration and initialization |
| 10 | [10_advanced_patterns.py](10_advanced_patterns.py) | Advanced usage patterns |

## Real-World Examples (11-13)

| # | File | Description |
|---|------|-------------|
| 11 | [11_complex_ecommerce.py](11_complex_ecommerce.py) | E-commerce system with checkout flow |
| 12 | [12_complex_banking.py](12_complex_banking.py) | Banking system with transaction tracking |
| 13 | [13_complex_data_pipeline.py](13_complex_data_pipeline.py) | ETL pipeline with stage tracking |

## Special Files

| File | Description |
|------|-------------|
| [xx_Color_Methods1.py](xx_Color_Methods1.py) | Color method reference for CLI viewer |

## Legacy Eliot Examples (l_ prefix)

These are original Eliot examples kept for reference. LogXPy evolved from Eliot.

| File | Description |
|------|-------------|
| [l_asyncio_linkcheck.py](l_asyncio_linkcheck.py) | AsyncIO link checker |
| [l_cross_process_client.py](l_cross_process_client.py) | Cross-process client |
| [l_cross_process_server.py](l_cross_process_server.py) | Cross-process server |
| [l_cross_thread.py](l_cross_thread.py) | Cross-thread logging |
| [l_dask_eliot.py](l_dask_eliot.py) | Dask integration |
| [l_journald.py](l_journald.py) | Journald destination |
| [l_linkcheck.py](l_linkcheck.py) | Link checker |
| [l_logfile.py](l_logfile.py) | Log file output |
| [l_rometrip_actions.py](l_rometrip_actions.py) | Rometrip example |
| [l_stdlib.py](l_stdlib.py) | Standard library logging |
| [l_stdout.py](l_stdout.py) | stdout destination |
| [l_trio_say.py](l_trio_say.py) | Trio async framework |

See [l_README.md](l_README.md) for details on Eliot compatibility and migration.

## Features Demonstrated

- **Structured Logging**: Key-value pairs for machine-readable logs
- **Action Tracking**: Hierarchical action context with start_action()
- **Message Types**: info, success, warning, error, critical
- **Decorators**: @logged, @timed, @retry, @generator
- **Context Management**: Nested scopes with additional context
- **Sqid Task IDs**: Short, hierarchical task identifiers
- **Color Hints**: Foreground/background colors for CLI viewer
- **OpenTelemetry**: Span integration for distributed tracing
