# LogXPy Examples

This directory contains example projects demonstrating various LogXPy features.

## Examples Overview

| Example | Directory | Description |
|---------|-----------|-------------|
| **Basic Examples** | `complete-example-01/` | 7 examples from basic logging to deep nesting |
| **Minimal Demo** | `compact-color-demo/` | **Ultra-compact** demo with symlink (105 lines total) |
| **Color Features** | `comp-with-parser/` | Comprehensive example with color rendering |

## 📁 Directories

### compact-color-demo/

**Two ultra-compact demos** demonstrating different approaches:

#### Option A: `compact_color_demo.py` - Deep Tree + @logged + stack_trace()
```bash
cd compact-color-demo
./run_compact.sh
```

**Key concept:** 
- **ONE yellow block** (Application Start)
- **ONE cyan block** (Critical Section)
- **@logged decorator** - 3 decorated functions
- **log.stack_trace()** - Error handling
- **4-level deep nesting** - functions inside functions

```
🟡 [1] ═══════════════  ← YELLOW BLOCK
   [2] app:main → started
    ├── [23] decorator:demo → started
   [24]   Testing @logged decorator
    ├── [25] __main__.process_item → started  ← @logged
    ├── [28] __main__.validate_email → started  ← @logged  
    ├── [30] __main__.calculate_total → started  ← @logged
🟦 [35] ═══════════════  ← CYAN BLOCK
    ...
    ├── [60] error:test → started
   [66]   Stack Trace                   ← stack_trace()
```

| File | Lines | Purpose |
|------|-------|---------|
| `compact_color_demo.py` | ~120 | Deep nesting + @logged + stack_trace() |
| `compact_parser.py` | ~75 | Show function tree with depth |
| `run_compact.sh` | ~40 | Run pipeline |

**Output:** 74 entries, 4-level deep tree, decorators, stack trace

#### Option B: `minimal_color_demo.py` - Color API Features  
Symlink to `complete-example-01/minimal_color_demo.py`:
- Shows color API methods (`set_foreground`, `set_background`, `colored`)
- Linear flow with colors at specific message points
- Demonstrates 7 feature categories separately

**Why use this folder?** Choose the demo style:
- **compact_color_demo.py** = Deep tree + @logged decorator + stack_trace()
- **minimal_color_demo.py** = Color API showcase (linear flow)

### complete-example-01/

Seven progressive examples demonstrating core logging features:

- **example_01_basic.py** - Basic logging concepts
- **example_02_actions.py** - Nested actions
- **example_03_errors.py** - Error handling
- **example_04_api_server.py** - HTTP simulation
- **example_05_data_pipeline.py** - ETL pipeline
- **example_06_deep_nesting.py** - 7-level nesting
- **example_07_all_data_types.py** - All data types

View with `view_tree.py` for colored tree visualization.

### comp-with-parser/

Comprehensive example with **foreground/background color support**:

- **example_09_comprehensive.py** - Full color API demo
- **run_and_analyze.sh** - Complete pipeline script
- **parse_comprehensive.py** - Log parser with validation
- **view_tree_colored.py** - Tree viewer with line numbers & colors
- **view_log_colored.py** - Log viewer showing color hints
- **view_line_colored.py** - Single line viewer with custom colors

## 🎨 Color API

```python
from logxpy import log

# Method 1: Context colors
log.set_foreground("cyan")
log.info("Cyan text")
log.reset_foreground()

# Method 2: Combined
log.set_foreground("white").set_background("red")
log.error("White on red")
log.reset_foreground().reset_background()

# Method 3: One-shot
def demo_multiline_block_highlight():
    # Save current colors
    saved_fg = log._foreground_color
    saved_bg = log._background_color
    
    # Apply highlight colors
    log.set_foreground("black").set_background("yellow")
    log.info("╔═══════════════════════════════════════╗\n"
             "║  ⚠️  IMPORTANT WARNING BLOCK         ║\n"
             "╚═══════════════════════════════════════╝")
    
    # Restore original colors
    log._foreground_color = saved_fg
    log._background_color = saved_bg
```

## 🚀 Quick Start

```bash
# Basic examples
cd complete-example-01
python example_01_basic.py
python view_tree.py example_01_basic.log

# Color features
cd comp-with-parser
./run_and_analyze.sh
```
