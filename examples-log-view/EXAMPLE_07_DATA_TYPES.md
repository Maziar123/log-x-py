# Example 07: All Data Types & Objects Demo

## Overview

This comprehensive example demonstrates how the tree viewer displays **all different data types and object structures** used in real-world applications.

## What's Tested

### 1. Primitive Data Types ✅

- **Numbers**: integers, floats, negative, zero, large, scientific notation
- **Boolean**: `True`, `False`
- **Strings**: regular, empty, Unicode (世界 🌍), multiline
- **None**: `null_value=None`

### 2. Collection Types ✅

- **Lists**: empty, numbers, mixed types, nested, deeply nested
- **Dictionaries**: empty, simple, nested, complex hierarchies
- **Tuples**: empty, simple, nested, mixed
- **Sets**: numbers, strings

### 3. Complex Structures ✅

#### API Response Format
```json
{
  "status": "success",
  "data": {
    "users": [
      {"id": 1, "name": "Alice", "roles": ["admin", "user"]},
      {"id": 2, "name": "Bob", "roles": ["user"]}
    ],
    "pagination": {"page": 1, "total": 2}
  },
  "meta": {"request_id": "req-123-456"}
}
```

#### Configuration Format
```json
{
  "app": {"name": "MyApp", "version": "2.5.0"},
  "database": {
    "host": "db.example.com",
    "pool": {"min_size": 5, "max_size": 20}
  },
  "features": {"authentication": true, "analytics": true}
}
```

### 4. Special Values & Edge Cases ✅

- **Special Characters**: `!@#$%^&*()_+-=[]{}|;':",./<>?`
- **File Paths**: Unix (`/usr/local/bin/python`), Windows (`C:\Users\...`)
- **URLs**: `https://example.com/path?key=value&foo=bar`
- **Email**: `user@example.com`
- **Escape Sequences**: tabs, quotes, newlines
- **Very Long Strings**: 200+ characters
- **SQL Queries**: `SELECT * FROM users WHERE...`
- **JSON Strings**: Embedded JSON as string
- **Special Numbers**: infinity, NaN, very large/small, scientific notation
- **Empty Values**: empty string, empty list, empty dict, None, zero, False

### 5. Python Objects ✅

- **DateTime Objects**: datetime, date, time (as strings)
- **Path Objects**: file paths
- **UUID Objects**: unique identifiers
- **Decimal Objects**: precise numbers

### 6. Error Scenarios ✅

```python
{
  "error_type": "ValidationError",
  "error_message": "Invalid email format",
  "field": "email",
  "error_code": "VAL_001"
}
```

```python
{
  "error_type": "DatabaseError",
  "stacktrace": ["File: database.py, Line: 45", ...]
}
```

### 7. Performance Metrics ✅

```python
{
  "operation": "api_request",
  "duration_ms": 145.67,
  "memory_mb": 256.5,
  "db_queries": 3,
  "cache_hits": 15
}
```

### 8. Nested Actions (4 Levels) ✅

Demonstrates deep nesting with complex data at each level:
- Level 1: Simple key-value
- Level 2: Nested data
- Level 3: More nesting
- Level 4: Complex arrays and objects

## How to Run

### Basic View
```bash
python example_07_all_data_types.py
python view_tree.py example_07_all_data_types.log
```

### ASCII Mode (No Unicode/Emoji)
```bash
python view_tree.py example_07_all_data_types.log --ascii
```

### No Colors (Plain Text)
```bash
python view_tree.py example_07_all_data_types.log --no-colors
```

### No Emojis
```bash
python view_tree.py example_07_all_data_types.log --no-emojis
```

### Limit Depth
```bash
python view_tree.py example_07_all_data_types.log --depth-limit 2
```

## Output Features

The tree viewer automatically:

### 🎨 Color Codes Values
- **Numbers**: Cyan color
- **Booleans**: Magenta color  
- **Strings with "error"/"fail"**: Red color
- **Strings with "success"/"complete"**: Green color
- **Regular strings**: White color

### 😊 Shows Emoji Icons
- ⚡ Action/Generic
- 💾 Database operations
- 🔌 API/HTTP operations
- 🔐 Authentication
- 🔥 Errors

### 🌲 Tree Structure
- Unicode box-drawing characters: `├── └── │`
- Clear hierarchy visualization
- Task level display: `/1`, `/2/1`, `/3/2/1`

### ⏱️ Timestamps & Status
- Compact time format: `14:19:30`
- Status indicators: ▶️ started, ✔️ succeeded, ✖️ failed

## Log Statistics

- **Total Entries**: 42
- **File Size**: ~10KB
- **Actions**: 8 top-level actions
- **Max Nesting Depth**: 4 levels
- **Data Types Tested**: 15+ types

## Use Cases

This example is perfect for:

1. **Testing**: Verify your log viewer handles all data types
2. **Development**: See how different structures appear in logs
3. **Documentation**: Show examples of data type formatting
4. **Debugging**: Compare expected vs actual output
5. **Performance**: Test with complex nested structures

## Key Takeaways

### What Works Great ✅
- All primitive types display clearly
- Nested structures maintain readability
- Colors help distinguish value types
- Unicode and emoji enhance visual scanning
- Special characters are handled correctly

### Design Patterns
- Use meaningful key names for better readability
- Nest data logically (max 3-4 levels recommended)
- Include context (timestamps, IDs, status)
- Add metadata for troubleshooting

### Best Practices
- Keep individual values reasonable in size
- Use structured data over plain strings
- Include type hints in key names when helpful
- Add units to numeric values (ms, MB, %, etc.)

## Python 3.12+ Features Used

The viewer uses modern Python features:
- **Type aliases**: `type LogEntry = dict[str, Any]`
- **Pattern matching**: Smart value coloring with `match`/`case`
- **Walrus operator**: `if duration := entry.get("duration")`
- **Dataclasses**: Zero-overhead with `slots=True`
- **StrEnum**: Type-safe enums for colors/emojis
- **Frozen dataclasses**: Immutable configurations

## Next Steps

- Try creating your own data types
- Test edge cases specific to your domain
- Experiment with deep nesting (example_06)
- Compare with other log viewers
- Customize colors/emojis for your needs

---

**Created**: 2026-02-05  
**Python Version**: 3.12+  
**Dependencies**: None (zero external dependencies!)
