# Example 06: Deep Nesting (7 Levels)

## Overview

This example demonstrates **deeply nested operations up to 7 levels** to showcase how logxpy and logxpy_cli_view handle complex hierarchical structures.

## Why This Example?

Most logging examples show 2-3 levels of nesting. This example pushes it to **7 levels** to demonstrate:
- How tree structure renders at deep levels
- Enter/exit tracking at each level
- Multiple nesting patterns (functional, class-based, recursive)
- Performance with deep hierarchies

## Three Patterns Demonstrated

### 1. Functional Nesting Pattern (7 Levels)

```
Level 1: Server Process
  └─ Level 2: HTTP Handler
      └─ Level 3: Request Validation
          └─ Level 4: Authentication
              └─ Level 5: Cache Check
                  └─ Level 6: Database Query
                      └─ Level 7: Deepest Operation
```

**Real-world scenario:** HTTP request goes through server → handler → validation → auth → cache → database → final operation

### 2. Class-Based Nesting Pattern (7 Levels)

```
Application
  └─ UserService
      └─ UserRepository
          └─ ConnectionPool
              └─ PostgresConnection
                  └─ QueryBuilder
                      └─ QueryExecutor
                          └─ ResultParser (Level 7)
```

**Real-world scenario:** Layered architecture with Application → Service → Repository → Data Access layers

### 3. Recursive Tree Processing (7 Levels)

```
Root Node
  ├─ Branch 1
  │   ├─ Leaf 1.1
  │   │   └─ Process Data
  │   │       └─ Validate
  │   │           └─ Transform
  │   │               └─ Output (Level 7)
  │   └─ Leaf 1.2
  └─ Branch 2
      └─ Leaf 2.1
```

**Real-world scenario:** Tree traversal with data processing at leaf nodes

## Log Output Structure

When viewed, each level shows proper indentation:

```
2026-02-05 13:00:10.051 | level_1:server [started]
  depth: 1
2026-02-05 13:00:10.051 | server:incoming_connection
  ip: 192.168.1.100
  port: 8080
  2026-02-05 13:00:10.092 | level_2:http_handler [started]
    depth: 2
  2026-02-05 13:00:10.092 | http:received
    method: POST
    2026-02-05 13:00:10.132 | level_3:validation [started]
      depth: 3
    2026-02-05 13:00:10.132 | validation:headers
      2026-02-05 13:00:10.172 | level_4:auth [started]
        depth: 4
      2026-02-05 13:00:10.172 | auth:validate_token
        2026-02-05 13:00:10.212 | level_5:cache [started]
          depth: 5
        2026-02-05 13:00:10.212 | cache:lookup
          2026-02-05 13:00:10.232 | level_6:database [started]
            depth: 6
          2026-02-05 13:00:10.232 | db:connect
            2026-02-05 13:00:10.282 | level_7:operation [started]
              depth: 7
            2026-02-05 13:00:10.282 | level_7:start
              info: Deepest level reached
            2026-02-05 13:00:10.303 | level_7:complete
            2026-02-05 13:00:10.303 | level_7:operation [succeeded]
          2026-02-05 13:00:10.303 | level_6:database [succeeded]
        2026-02-05 13:00:10.303 | level_5:cache [succeeded]
      2026-02-05 13:00:10.303 | level_4:auth [succeeded]
    2026-02-05 13:00:10.303 | level_3:validation [succeeded]
  2026-02-05 13:00:10.303 | level_2:http_handler [succeeded]
2026-02-05 13:00:10.303 | level_1:server [succeeded]
```

## Key Features

✅ **7 levels of nesting** - Maximum depth to test rendering  
✅ **Enter/Exit tracking** - Every level shows [started] and [succeeded]  
✅ **Proper indentation** - Visual tree structure with spaces  
✅ **Duration tracking** - Time spent at each level  
✅ **Multiple patterns** - Functional, OOP, and recursive examples  
✅ **102 log entries** - Comprehensive test case  

## Run the Example

```bash
cd /mnt/N1/MZ/AMZ/Projects/Prog/a_cross/log-x-py/examples/cli_view

# Run and view
./run_single.sh 6

# Or manually
python example_06_deep_nesting.py
python view_tree.py example_06_deep_nesting.log
```

## When to Use Deep Nesting

Use deep nesting patterns when you have:
- **Layered architectures** (Application → Service → Repository → DAO)
- **Middleware chains** (Request → Auth → Validation → Rate Limit → Handler)
- **Recursive algorithms** (Tree traversal, graph processing)
- **Complex workflows** (Order → Payment → Inventory → Shipping → Notification)
- **Nested transactions** (Business logic with multiple sub-operations)

## Performance Considerations

Even at 7 levels deep:
- ✅ Log generation is fast (< 1 second)
- ✅ Tree rendering is readable
- ✅ File size is reasonable (17K for 102 entries)
- ✅ Structure is clear and maintainable

## Comparison with Other Examples

| Example | Max Depth | Pattern | Log Entries |
|---------|-----------|---------|-------------|
| Example 01 | 1 | Flat messages | 6 |
| Example 02 | 3 | Nested actions | 15 |
| Example 03 | 2 | Error handling | 12 |
| Example 04 | 4 | API server | 40 |
| Example 05 | 3 | Data pipeline | 32 |
| **Example 06** | **7** | **Deep nesting** | **102** |

## Learn More

This example is perfect for understanding:
- How logxpy handles deep hierarchies
- How logxpy_cli_view renders complex trees
- Best practices for structured logging in layered systems
- Performance characteristics of nested actions

---

**File:** `example_06_deep_nesting.py`  
**Log:** `example_06_deep_nesting.log` (17K, 102 entries)  
**Depth:** 7 levels  
**Patterns:** 3 (Functional, Class-based, Recursive)
