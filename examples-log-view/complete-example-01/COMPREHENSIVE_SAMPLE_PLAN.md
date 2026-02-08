# Comprehensive Sample Plan for logxpy

## Overview

This document outlines the plan for creating a comprehensive but minimal sample file that demonstrates all logxpy functionality based on the cross-reference analysis in `DOC-X/cross-docs/cross-lib1.html`.

## Step 1: Library Analysis Summary

The logxpy library provides:

- **Core Logging**: Structured JSON logging with hierarchical actions
- **LoggerX API**: Fluent interface with level methods (debug, info, warning, error, etc.)
- **CodeSite Compatibility**: Send* methods for Delphi/CodeSite migration
- **System Information**: Memory, heap, stack trace utilities
- **File/Stream Operations**: Hex dumps, text file reading
- **Data Types**: Colors, currency, datetime, enums, sets, pointers
- **Decorators**: @logged, @timed, @retry for function instrumentation
- **Async Support**: aaction() for coroutines
- **Validation**: MessageType/ActionType schemas with Field validators

## Step 2: AI_CONTEXT.md Status

The `AI_CONTEXT.md` file is comprehensive and up-to-date. Key sections:
- Complete API reference with all public functions
- LoggerX API with level methods and type methods
- Decorators module documentation
- Viewer (`logxpy-cli-view`) CLI commands and API
- System message types (Eliot & LoggerX)

No updates needed to AI_CONTEXT.md.

## Step 3: Categories from cross-lib1.html

### 3.1 Category List (14 Categories)

| # | Category | Emoji | Description |
|---|----------|-------|-------------|
| 1 | Basic Message Sending | 📨 | Simple text, typed messages, notes |
| 2 | Method Tracing (Call Stack) | 🔍 | Enter/exit methods, auto tracing |
| 3 | Error & Warning Messages | ⚠️ | Errors, warnings, exceptions |
| 4 | System & Memory Information | 💻 | OS info, memory, heap, stack |
| 5 | File & Stream Operations | 📁 | Hex dumps, text files, streams |
| 6 | Data Type Specific | 📊 | Colors, currency, datetime, enums |
| 7 | Component & Object Information | 🔧 | Object properties, collections |
| 8 | Conditional & Formatted Sending | 🎯 | Conditional logging, formatting |
| 9 | Checkpoints & Separators | 🚩 | Checkpoint markers, separators |
| 10 | Category Management | 🏷️ | Categories, colors |
| 11 | XML Data | 📄 | XML logging |
| 12 | Registry & Version Info | 🗄️ | Windows registry, versions |
| 13 | Write Methods (No Timestamp) | ✍️ | Raw write methods |
| 14 | logxpy-Specific Features | 🚀 | Actions, tasks, decorators, async |

### 3.2 Table Data Extracted

For each row in the tables, we extract:
- **logxpy Prototype**: Function signature
- **logxpy Description**: What it does
- **logxpy Example**: Usage example
- **Params**: Parameter descriptions

See `example_09_comprehensive.py` for the implementation.

## Step 4: Sample Structure

### 4.1 Structure Requirements

- **One function per category** (14 functions total) ✅
- **Each function covers all rows** in that category's table ✅
- **Order matches categories**: 1 → 14 ✅
- **Main function calls all category functions** ✅

### 4.2 Implementation Requirements

For each table row:
1. Write one line using: `logxpy-Prototype + logxpy-Example` ✅
2. Add inline comment with: `logxpy-Description + logxpy-Params` ✅
3. No printf-like statements in main function ✅
4. Use actual logxpy calls that execute ✅

### 4.3 Constraint Compliance

- ✅ No printf-like formatting (use f-strings or direct calls)
- ✅ All log calls are actual library invocations
- ✅ Inline comments document Description and Params
- ✅ One comprehensive function per category

### 4.4 Generated Files

| File | Size | Lines | Description |
|------|------|-------|-------------|
| `example_09_comprehensive.py` | ~27KB | ~760 | Comprehensive sample code |
| `example_09_comprehensive.log` | ~22KB | 88 | Generated JSON log output |

### 4.5 Execution Results

```bash
cd examples-log-view
python example_09_comprehensive.py
# Output: Log written to: example_09_comprehensive.log

python view_tree.py example_09_comprehensive.log
# Shows 88 log entries across 14 categories
```

## Step 5: File Organization

```
examples-log-view/
├── COMPREHENSIVE_SAMPLE_PLAN.md    # This file
├── example_09_comprehensive.py      # The comprehensive sample
└── example_09_comprehensive.log     # Generated log output
```

## Step 6: Execution Plan

1. Create `example_09_comprehensive.py` with all 14 category functions
2. Each function demonstrates all APIs in that category
3. Run the sample to generate `example_09_comprehensive.log`
4. View with: `python view_tree.py example_09_comprehensive.log`

## Category Function Mapping

| Function | Category | APIs Covered |
|----------|----------|--------------|
| `demo_basic_messages()` | 📨 Basic Message Sending | log.info(), log.debug(), log.send(), log.note(), log_message(), log() callable |
| `demo_method_tracing()` | 🔍 Method Tracing | start_action(), @logged, @log_call, action.finish() |
| `demo_errors_warnings()` | ⚠️ Error & Warning | log.error(), log.warning(), log.critical(), write_traceback(), log.exception() |
| `demo_system_memory()` | 💻 System & Memory | log.system_info(), log.memory_status(), log.memory_hex(), log.stack_trace() |
| `demo_file_stream()` | 📁 File & Stream | log.file_hex(), log.file_text(), log.stream_hex(), log.stream_text() |
| `demo_data_types()` | 📊 Data Types | log.color(), log.currency(), log.datetime(), log.enum(), log.sset(), log.ptr(), log.variant() |
| `demo_component_object()` | 🔧 Component & Object | vars(), dir(), repr(), getattr(), list() for collections |
| `demo_conditional_formatted()` | 🎯 Conditional & Formatted | Python if statements, log() callable, f-strings |
| `demo_checkpoints()` | 🚩 Checkpoints | log.checkpoint(), manual separators |
| `demo_category_management()` | 🏷️ Category Management | CategorizedLogger, category_context, set_color() |
| `demo_xml_data()` | 📄 XML Data | xml.etree + log.send() |
| `demo_registry_version()` | 🗄️ Registry & Version | importlib.metadata.version() |
| `demo_write_methods()` | ✍️ Write Methods | log.send() with timestamps (always stamped) |
| `demo_decorators()` | 🎨 Decorators | @logged, @timed, @retry, @generator, @aiterator, @trace, @log_call |
| `demo_logxpy_specific()` | 🚀 logxpy-Specific | start_task(), aaction(), MessageType, ActionType, Field |

## Running the Sample

```bash
cd examples-log-view

# Generate the comprehensive log
python example_09_comprehensive.py

# View as tree
python view_tree.py example_09_comprehensive.log

# View with options
python view_tree.py example_09_comprehensive.log --ascii
python view_tree.py example_09_comprehensive.log --no-colors
```

## Dependencies

The sample uses lazy imports where possible:
- Standard library only for core features
- Optional: psutil (for enhanced memory info)
- Optional: Pillow (for screenshot)
- Optional: xml.etree (for XML data)

All features gracefully degrade if optional dependencies are not installed.
