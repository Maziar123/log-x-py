# boltons `25.0.0` — Complete Reference

> 250+ pure-Python utilities — no dependencies · Battle-tested · ~6.6k ★
> `pip install boltons` · Python ≥3.7 · by Kurt Rose & Mahmoud Hashemi
> 26 modules · 87 types · 171 functions · Feb 2026

---

**logxpy Integration**: See [boltons-in-logxpy.md](boltons-in-logxpy.md) for how logxpy uses boltons with Python 3.12+ features.

---

## `cacheutils` — Caches and caching

LRU/LRI caches, cached decorators, cachedproperty.

```
class LRU(max_size=128, values=None, on_miss=None)
    Least Recently Used cache. Dict subtype that evicts the least-recently
    accessed entry when max_size is exceeded.
    .get(key, default=None)       .pop(key, default=None)
    .setdefault(key, default)     .clear()
    .copy()                       .soft_clear()  → clear but keep max_size
    on_miss(key) callback fires on cache miss, return value is stored.

class LRI(max_size=128, values=None, on_miss=None)
    Least Recently Inserted cache. Same API as LRU but evicts based on
    insertion order, not access order. Faster than LRU for write-heavy loads.

class ThresholdCounter(threshold=0.001)
    Bounded dict-like mapping from keys to counts. Automatically prunes
    entries below the threshold fraction of total. Useful for streaming
    frequency estimation (heavy hitters / lossy counting).
    .add(key)                     .elements()
    .most_common(n=None)          .get_count(key)
    .get_total()                  .get_threshold()

class MinIDMap()
    Assigns weakref-able objects the smallest available unique integer ID.
    Auto-reclaims IDs when objects are garbage collected.
    .get(obj)  → int             .drop(obj)
    .iteritems()                 len(m)

@cached(cache, scoped=True, typed=False, key=None)
    Cache any function. Accepts any dict-like as cache (LRU, LRI, plain dict).
    scoped=True: include function identity in cache key (safe for reuse).
    typed=True: separate cache entries for int(1) vs float(1.0).
    key=callable: custom cache key function(args, kwargs) → hashable.

@cachedmethod(cache, scoped=True, typed=False, key=None)
    Like @cached but for methods. The cache object is per-method, not
    per-instance; use a lambda or Factory for per-instance caching.

class cachedproperty(func)
    Like @property but computed only once, then stored on the instance.
    No __set__ or __delete__. Thread-safe for frozen computation.

make_cache_key(args, kwargs, typed=False)
    Build a generic hashable key from positional and keyword arguments.

make_sentinel(name='_MISSING', var_name=None)
    Create a unique sentinel object. Useful for distinguishing "not provided"
    from None. The sentinel has a clean repr and is falsy by default.
    _MISSING = make_sentinel('_MISSING')
```

### Recipes

```python
from boltons.cacheutils import LRU, cached, cachedproperty

# Basic LRU cache
cache = LRU(max_size=1000)
@cached(cache)
def fetch_user(uid):
    return db.query(uid)

# cachedproperty — compute once
class Config:
    @cachedproperty
    def settings(self):
        return load_settings()   # called once per instance

# Auto-loading cache with on_miss
users = LRU(max_size=500, on_miss=lambda uid: db.get_user(uid))
user = users[42]               # fetches from db on first access

# Streaming frequency estimation
from boltons.cacheutils import ThresholdCounter
tc = ThresholdCounter(threshold=0.01)
for word in huge_stream:
    tc.add(word)
tc.most_common(10)             # top 10 by approximate frequency
```

---

## `debugutils` — Debugging utilities

Drop into pdb on exceptions or signals, trace object interactions.

```
pdb_on_exception(limit=100)
    Install sys.excepthook that drops into pdb instead of exiting.
    limit controls traceback depth.

pdb_on_signal(signalnum=None)
    Install a signal handler (default SIGINT) that drops into pdb.
    Useful for debugging hung processes: send the signal, get a debugger.

wrap_trace(obj, hook=trace_print_hook, which=None, events=None, label=None)
    Wrap an object to monitor all interactions. Every method call, attribute
    access, or item access is reported via the hook function.
    which: iterable of attr names to trace (None = all).
    events: set of event types ('get', 'set', 'del', 'call').
    Returns a proxy object.

trace_print_hook(event, label, obj, attr_name, args=(), kwargs={}, result=_UNSET)
    Default hook for wrap_trace. Prints each interaction to stderr.
```

### Recipes

```python
from boltons.debugutils import pdb_on_exception, wrap_trace

# Drop into debugger on any unhandled exception
pdb_on_exception()

# Trace all interactions with an object
traced_db = wrap_trace(db_connection, label='DB')
traced_db.execute("SELECT 1")
# prints: DB.execute('SELECT 1') → <result>
```

---

## `dictutils` — Mapping types (OMD)

OrderedMultiDict, OneToOne, ManyToMany, FrozenDict, subdict.

```
class OrderedMultiDict(*a, **kw)            — aliased as OMD, MultiDict
    A dict subtype that retains insertion order and supports multiple values
    per key. Core structure for HTTP headers, query strings, form data.

    Standard dict API plus:
    .add(key, value)              → append without overwriting
    .addlist(key, valuelist)      → append multiple values
    .getlist(key, default=_MISSING) → list of all values for key
    .setlist(key, valuelist)      → replace all values for key
    .popall(key, default=_MISSING)→ pop all values for key
    .poplast(key=_MISSING, default=_MISSING) → pop last-inserted (key,value)
    .keys(multi=False)            → multi=True yields repeated keys
    .values(multi=False)          → multi=True yields all values
    .items(multi=False)           → multi=True yields all (key, value)
    .inverted()                   → OMD with keys↔values swapped
    .counts()                     → dict of key → count of values
    .todict()                     → plain dict (last value wins)
    .sorted()                     → new OMD sorted by key
    .copy()                       → shallow copy
    len(omd)                      → number of unique keys

class FastIterOrderedMultiDict(*a, **kw)
    OrderedMultiDict backed by a skip list. O(1) iteration over all (k,v)
    pairs. Faster iteration, same API as OMD.

class OneToOne(*a, **kw)
    Bijective dict: every key maps to exactly one value and vice versa.
    Setting a duplicate value raises ValueError.
    .inv                          → the inverse mapping (also a OneToOne)

class ManyToMany(items=None)
    Dict-like representing a many-to-many relationship.
    m2m = ManyToMany({1: {'a','b'}, 2: {'b','c'}})
    m2m[1]                        → {'a', 'b'}
    m2m.inv['b']                  → {1, 2}
    .add(key, value)              .remove(key, value)
    .get(key, default=frozenset())
    .inv                          → inverse ManyToMany
    .keys() .values() .items()

class FrozenDict(...)
    Immutable, hashable dict. Can be used as dict key or set member.
    Raises TypeError on mutation attempts. Built from any mapping.

subdict(d, keep=None, drop=None)
    Compute a "subdictionary". Keep only keys in keep, or drop keys in drop.
    subdict({'a':1,'b':2,'c':3}, keep=['a','b']) → {'a':1, 'b':2}
    subdict({'a':1,'b':2,'c':3}, drop=['c'])     → {'a':1, 'b':2}
```

### Recipes

```python
from boltons.dictutils import OrderedMultiDict, OneToOne, FrozenDict, subdict

# HTTP headers with multiple values
headers = OrderedMultiDict()
headers.add('Set-Cookie', 'a=1')
headers.add('Set-Cookie', 'b=2')
headers.getlist('Set-Cookie')        → ['a=1', 'b=2']

# Bidirectional mapping
codes = OneToOne({'us': 'United States', 'gb': 'United Kingdom'})
codes.inv['United States']           → 'us'

# Hashable dict (for sets, dict keys)
cfg = FrozenDict(host='localhost', port=8080)
cache = {cfg: result}

# Selective dict
subdict(request.args, keep=['page', 'limit'])
```

---

## `ecoutils` — Ecosystem analytics

Collect runtime environment info (Python version, OS, CPU, packages).

```
get_profile(**kwargs) → dict
    Collect comprehensive environment profile: Python version, platform,
    hostname, CPU architecture, user, installed packages, filesystem info.

get_profile_json(indent=False) → str
    Same as get_profile() but returns JSON string.

get_python_info() → dict
    Python-specific info: version, compiler, build, implementation.
```

### Recipes

```python
from boltons.ecoutils import get_profile
profile = get_profile()
# {'python': {'version': '3.12.1', ...}, 'platform': {...}, ...}
# Useful for bug reports, logging environment state, CI diagnostics
```

---

## `fileutils` — Filesystem helpers

Atomic file writes, directory creation, file finding, permissions, rotation.

```
atomic_save(dest_path, **kwargs)
    Context manager for atomic file writes. Writes to a temp file, then
    renames on success. On failure, the temp file is cleaned up.
    kwargs: text_mode=False, overwrite=True, part_file=None, rm_part_on_exc=True

class AtomicSaver(dest_path, **kwargs)
    Class form of atomic_save. Same kwargs.
    with AtomicSaver('/etc/config') as f:
        f.write(data)

mkdir_p(path)
    Create directory and all parents (like mkdir -p). No error if exists.

iter_find_files(directory, patterns, ignored=None, include_dirs=False, max_depth=None)
    Recursively find files matching glob patterns.
    patterns: string or list of glob patterns ('*.py', '*.txt')
    ignored: patterns to skip
    max_depth: limit recursion depth
    Returns generator of file paths.

copy_tree(src, dst, symlinks=False, ignore=None)     — alias: copytree
    Recursive directory copy (like shutil.copytree but works).

class FilePerms(user='', group='', other='')
    Parse, represent, and manipulate POSIX file permissions.
    FilePerms.from_int(0o755)     → FilePerms(user='rwx', group='rx', other='rx')
    FilePerms.from_path('/etc/passwd')
    fp.to_int()                   → 0o755

atomic_rename(src, dst, overwrite=False)
    Atomically rename src to dst. Cross-platform.

replace(src, dst)
    Like os.replace (Python 3.3+). Atomic rename that overwrites dst.

rotate_file(filename, *, keep=5)
    Rotate file.ext → file.1.ext → file.2.ext → ... up to keep copies.

class DummyFile(path, mode='r', buffering=None)
    A no-op file-like object. Useful for silencing output.

set_cloexec(fd)
    Set close-on-exec flag on a file descriptor.
```

### Recipes

```python
from boltons.fileutils import atomic_save, mkdir_p, iter_find_files, FilePerms

# Atomic config write — never corrupted
with atomic_save('/etc/app/config.json') as f:
    f.write(json.dumps(config))

# Find all Python files
for path in iter_find_files('/src', '*.py', ignored=['__pycache__']):
    process(path)

# Ensure directory exists
mkdir_p('/var/log/myapp')

# File permissions
fp = FilePerms.from_int(0o644)
fp.user   → 'rw'
fp.other  → 'r'
```

---

## `formatutils` — `str.format()` toolbox

Parse, inspect, and manipulate format strings.

```
get_format_args(fstr) → (positional_args, keyword_args)
    Introspect a format string to discover referenced arguments.
    get_format_args('{0} {name}')  → ([0], ['name'])

tokenize_format_str(fstr, resolve_pos=True) → list
    Split format string into alternating literal strings and
    BaseFormatField objects.

split_format_str(fstr) → list
    Basic splitting of format string into literal and field parts.

infer_positional_format_args(fstr)
    Convert anonymous positional args {} to explicit {0}, {1}, etc.

construct_format_field_str(fname, fspec, conv) → str
    Reconstruct a format field string from parsed components.

class BaseFormatField(fname, fspec='', conv=None)
    Represents a single {field:spec!conv} reference.
    .base_name    .subpath    .is_positional
    .set_name()   .set_conv() .set_spec()

class DeferredValue(func, cache_value=True)
    Wraps a callable for lazy evaluation inside format strings.
    Computes only when __format__ is called.
    '{stats}'.format(stats=DeferredValue(compute_stats))
```

### Recipes

```python
from boltons.formatutils import get_format_args, DeferredValue

# Discover what a template needs
pos, kw = get_format_args('Hello {name}, you have {count} items')
# pos=[], kw=['name', 'count']

# Lazy evaluation in format strings
import time
msg = 'Time: {now}'.format(now=DeferredValue(lambda: time.time()))
```

---

## `funcutils` — `functools` fixes

Better wraps, FunctionBuilder, partial that works with methods.

```
wraps(func, injected=None, expected=None, **kw)
    Decorator factory. Like functools.wraps but copies the full signature,
    not just __name__ and __doc__. The wrapped function introspects correctly.
    injected: args to remove from signature (already provided).
    expected: args to add to signature.

update_wrapper(wrapper, func, injected=None, expected=None, build_from=None, **kw)
    Function form of wraps. Same parameters.

class FunctionBuilder(name, **kw)
    Programmatically create functions with arbitrary signatures.
    fb = FunctionBuilder('my_func', args=['x', 'y'], body='return x + y')
    func = fb.get_func()
    .args  .kwargs  .body  .doc  .annotations
    .add_arg(name, default=_UNSET)
    .remove_arg(name)
    .get_func(execdict=None, add_source=True, with_dict=True)
    .get_defaults_dict()
    FunctionBuilder.from_func(existing_func) → introspect existing

class InstancePartial(...)
    Like functools.partial but works correctly as an instance method.
    Normal partial breaks when accessed as a descriptor (method binding).
    InstancePartial binds self properly.

class CachedInstancePartial(...)
    Same as InstancePartial but caches the bound method for performance.

partial = CachedInstancePartial    — recommended default

copy_function(orig, copy_dict=True)
    Shallow copy a function (code, globals, defaults, closure, dict).

noop(*args, **kwargs)
    No-op function. Returns None. Useful as default callback.

partial_ordering(cls)
    Class decorator. Like functools.total_ordering but handles partial
    orderings (where not all elements are comparable).

format_invocation(name='', args=(), kwargs=None, **kw) → str
    Format a function call as a string for logging/debugging.
    format_invocation('foo', (1, 2), {'bar': 3}) → "foo(1, 2, bar=3)"

format_exp_repr(obj, pos_names, req_names=None, opt_names=None, opt_key=None)
    Render an expression-style repr: MyType(x=1, y=2).

dir_dict(obj, raise_exc=False) → dict
    Like dir() but returns {name: value} dict.

mro_items(type_obj)
    Iterate over all class variables in MRO order.

get_module_callables(mod, ignore=None) → (types_dict, funcs_dict)
    Introspect a module and return its types and functions.
```

### Recipes

```python
from boltons.funcutils import wraps, FunctionBuilder, InstancePartial, noop

# wraps that preserves signature
def decorator(func):
    @wraps(func)
    def wrapper(*a, **kw):
        print(f"calling {func.__name__}")
        return func(*a, **kw)
    return wrapper

# Build a function dynamically
fb = FunctionBuilder('adder', args=['x', 'y'], body='return x + y',
                     doc='Add two numbers')
adder = fb.get_func()
adder(3, 4)  → 7

# partial that works as method
class MyClass:
    process = InstancePartial(some_func, mode='fast')
```

---

## `gcutils` — Garbage collecting tools

Safely toggle GC, find all instances of a type.

```
class GCToggler(postcollect=False)
    Context manager to safely disable/re-enable the garbage collector.
    postcollect=True: run gc.collect() on exit.
    with GCToggler():
        # GC disabled here — bulk allocation without pauses
        data = [MyObj() for _ in range(1_000_000)]

get_all(type_obj, include_subtypes=True) → list
    Get ALL live instances of a given type. Walks gc.get_objects().
    Useful for debugging memory leaks.
    get_all(MyClass)              → [instance1, instance2, ...]
```

---

## `ioutils` — Input/output enhancements

Spooled IO, multi-file reader.

```
class SpooledBytesIO(max_size=5_000_000, dir=None)
    Bytes file-like that lives in memory until exceeding max_size,
    then transparently spills to a temp file on disk.
    Standard read/write/seek/tell API.

class SpooledStringIO(*args, **kwargs)
    Unicode version of SpooledBytesIO.

class SpooledIOBase(max_size=5_000_000, dir=None)
    Base class for the spooled types.

class MultiFileReader(*fileobjs)
    Concatenate multiple file objects into a single readable stream.
    Reads seamlessly across file boundaries.

is_text_fileobj(fileobj) → bool
    Check if a file object is in text mode.
```

### Recipes

```python
from boltons.ioutils import SpooledBytesIO

# Buffer in memory, spill to disk if huge
buf = SpooledBytesIO(max_size=10_000_000)  # 10MB threshold
for chunk in download_stream():
    buf.write(chunk)
buf.seek(0)
process(buf)
```

---

## `iterutils` — `itertools` improvements

The largest boltons module. Chunking, flattening, windowing, nesting, remap.

```
# ── Chunking & Windowing ──

chunked(src, size, count=None, **kw) → list of lists
    Break iterable into chunks. Returns a list.
    chunked(range(7), 3)                → [[0,1,2], [3,4,5], [6]]

chunked_iter(src, size, **kw) → generator of lists
    Lazy version of chunked.

windowed(src, size, fill=_UNSET) → list of tuples
    Sliding window. fill pads the last window if too short.
    windowed([1,2,3,4,5], 3)            → [(1,2,3),(2,3,4),(3,4,5)]

windowed_iter(src, size, fill=_UNSET) → generator
    Lazy version of windowed.

pairwise(src, end=_UNSET) → list of tuples
    Shortcut for windowed(src, 2).
    pairwise([1,2,3])                   → [(1,2),(2,3)]

pairwise_iter(src, end=_UNSET) → generator
    Lazy version.

# ── Flattening ──

flatten(iterable) → list
    Collapse one level of nesting.
    flatten([[1,2],[3,[4,5]]])           → [1, 2, 3, [4, 5]]

flatten_iter(iterable) → generator
    Lazy version.

# ── Selection ──

first(iterable, default=None, key=None)
    Return first truthy element (or matching key).
    first([0, False, 3, 4])             → 3
    first([0, False], default='nope')   → 'nope'

one(src, default=None, key=None)
    Assert iterable has exactly one truthy item and return it.

unique(src, key=None) → list
    Unique values preserving insertion order.
    unique([3,1,2,1,3])                 → [3, 1, 2]

unique_iter(src, key=None) → generator
    Lazy version.

redundant(src, key=None, groups=False)
    Complement of unique: return only duplicated values.

same(iterable, ref=_UNSET) → bool
    True if all values are identical.
    same([1, 1, 1])                     → True

# ── Splitting ──

split(src, sep=None, maxsplit=None) → list of lists
    Split iterable on separator, like str.split for iterables.
    split([1,0,2,0,3], sep=0)           → [[1], [2], [3]]

split_iter(src, sep=None, maxsplit=None) → generator
    Lazy version.

partition(src, key=bool) → (truthy_list, falsy_list)
    Split into two lists based on predicate.
    ⚠ Returns (truthy, falsy) — opposite order from more-itertools!
    partition([1,2,3,4,5], lambda x: x>3) → ([4,5], [1,2,3])

bucketize(src, key=bool, value_transform=None, key_filter=None) → dict
    Group values by key function.
    bucketize(range(5), key=lambda x: x%2) → {0:[0,2,4], 1:[1,3]}

# ── Stripping ──

strip(iterable, strip_value=None)       → list — strip from both ends
lstrip(iterable, strip_value=None)      → list — strip from beginning
rstrip(iterable, strip_value=None)      → list — strip from end
strip_iter / lstrip_iter / rstrip_iter  → lazy generators

# ── Sorting ──

soft_sorted(iterable, first=None, last=None, key=None, reverse=False)
    Partial ordering: pin some items first/last, sort the rest.
    soft_sorted([3,1,4,1,5], first=[5], last=[1]) → [5, 3, 4, 1, 1]

untyped_sorted(iterable, key=None, reverse=False)
    Sort mixed types without TypeError (falls back to type name).

# ── Numeric ──

frange(stop, start=None, step=1.0) → list
    Float range. Returns a list.
    frange(0.0, 1.0, 0.3)              → [0.0, 0.3, 0.6, 0.9]

xfrange(stop, start=None, step=1.0) → generator
    Generator version of frange.

backoff(start, stop, count=None, factor=2.0, jitter=False) → list
    Geometric sequence for retry delays.
    backoff(1, 30, count=5)             → [1, 2, 4, 8, 16]

backoff_iter(start, stop, count=None, factor=2.0, jitter=False) → generator
    Lazy version. jitter=True adds random variation.

chunk_ranges(input_size, chunk_size, input_offset=0, overlap_size=0, align=False)
    Generate (start, end) ranges for chunked processing.

# ── Predicates ──

is_iterable(obj) → bool          — True for lists, etc. False for strings.
is_scalar(obj) → bool            — opposite of is_iterable
is_collection(obj) → bool        — same as is_iterable

# ── Nested Data: remap & research ──

remap(root, visit=default_visit, enter=default_enter, exit=default_exit,
      reraise=True, tag=None)
    ★ KILLER FEATURE. Recursively traverse and transform arbitrarily nested
    data (dicts, lists, tuples, sets). Callbacks control the walk:
      visit(path, key, value) → new value (or True to keep, False to drop)
      enter(path, key, value) → (new_parent, items_iter) or False to skip
      exit(path, key, old_parent, new_parent, new_items) → final value
    path is a tuple of keys leading to current location.

research(root, query=lambda p,k,v: False, reraise=False)
    Search nested data. Returns list of (path, key, value) where query
    returns True.
    research({'a': {'b': [1,2,3]}}, query=lambda p,k,v: v == 2)
    → [((('a',), 'b', 0), 0, 2)]   — found 2 at root.a.b[0]

get_path(root, path, default=_UNSET)
    Retrieve a value from nested data via a tuple path.
    get_path({'a': {'b': 42}}, ('a', 'b'))  → 42

default_visit(path, key, value)    — default callbacks for remap
default_enter(path, key, value)
default_exit(path, key, old_parent, new_parent, new_items)

# ── GUID Iterators ──

class GUIDerator(size=24)
    Iterator yielding globally-unique IDs (base64-encoded random + counter).

class SequentialGUIDerator(size=24)
    Same but sequential (monotonically increasing).

class PathAccessError(exc, seg, path)
    Exception for nested access failures. Amalgamation of KeyError,
    IndexError, and TypeError.
```

### Recipes

```python
from boltons.iterutils import remap, research, chunked, backoff, bucketize

# ── remap: clean None values from nested data ──
data = {'a': 1, 'b': None, 'c': {'d': None, 'e': 2}}
clean = remap(data, visit=lambda p, k, v: v is not None)
# → {'a': 1, 'c': {'e': 2}}

# ── remap: redact sensitive fields ──
remap(api_response, visit=lambda p, k, v: '***' if k in ('password','token') else v)

# ── research: find all emails in nested JSON ──
import re
research(big_json, query=lambda p, k, v: isinstance(v, str) and '@' in v)

# ── batch processing ──
for batch in chunked(million_rows, 1000):
    db.insert_many(batch)

# ── retry delays ──
for delay in backoff(0.5, 60, count=8, jitter=True):
    try: result = api_call(); break
    except: time.sleep(delay)

# ── group by arbitrary key ──
by_ext = bucketize(filenames, key=lambda f: f.rsplit('.', 1)[-1])
```

---

## `jsonutils` — JSON interactions

JSONL (JSON Lines) iterator with reverse-reading.

```
class JSONLIterator(file_obj, ignore_errors=False, reverse=False, rel_seek=None)
    Iterate over JSON-encoded objects in a JSONL file (one JSON per line).
    reverse=True: iterate from end of file (tail-like).
    ignore_errors: skip unparseable lines.
    .next()  .__iter__()  .__len__()

reverse_iter_lines(file_obj, blocksize=4096, preseek=True, encoding=None)
    Iterate over lines in a file in reverse order (last line first).
    Memory-efficient: reads in blocks from the end.
```

### Recipes

```python
from boltons.jsonutils import JSONLIterator

# Read JSONL log file
with open('events.jsonl') as f:
    for event in JSONLIterator(f):
        process(event)

# Read last N events efficiently
with open('events.jsonl') as f:
    for event in JSONLIterator(f, reverse=True):
        if enough: break
        process(event)
```

---

## `listutils` — `list` derivatives

High-performance list subtypes for large collections.

```
class BarrelList(iterable=None)              — alias: BList
    A list subtype backed by many smaller lists ("barrels"). Provides
    better performance for very large lists by avoiding the O(n) cost
    of insert/delete in the middle. Standard list API.
    Automatic barrel splitting when sublists grow too large.

class SplayList(iterable=())
    Self-adjusting list: recently accessed elements migrate toward the
    front. Good for workloads with temporal locality.
    Standard list API. Splay on __getitem__ and __contains__.
```

---

## `mathutils` — Mathematical functions

Clamping, flexible floor/ceil, bit strings.

```
clamp(x, lower=-inf, upper=inf)
    Limit value to range.
    clamp(15, 0, 10)                    → 10
    clamp(-5, 0, 10)                    → 0

ceil(x, options=None)
    If options given, return smallest option ≥ x.
    ceil(3.2)                           → 4
    ceil(3.2, options=[1, 5, 10])       → 5

floor(x, options=None)
    If options given, return largest option ≤ x.
    floor(3.8, options=[1, 5, 10])      → 1

class Bits(val=0, len_=None)
    Immutable bit-string. Supports indexing, slicing, bitwise ops.
    Bits(0b1010, 4)
    .to_int()  .to_bytes()  len(b)
    b[0]  b[1:3]  b & other  b | other  b ^ other  ~b
```

---

## `mboxutils` — Unix mailbox utilities

```
class mbox_readonlydir(path, factory=None, create=True, maxmem=1048576)
    A read-only mailbox.mbox subclass suitable for use with mboxs stored
    in directories. Uses memory-mapped IO for efficiency.
```

---

## `namedutils` — Lightweight containers

Named variants of tuple and list.

```
namedtuple(typename, field_names, verbose=False, rename=False)
    Identical to collections.namedtuple. Re-exported for convenience.

namedlist(typename, field_names, verbose=False, rename=False)
    Like namedtuple but MUTABLE. Returns a new list subclass with named
    fields. Supports assignment: nl.x = 5.
```

### Recipes

```python
from boltons.namedutils import namedlist

Point = namedlist('Point', ['x', 'y'])
p = Point(3, 4)
p.x = 10                               # mutable!
p[0]                                    → 10
```

---

## `pathutils` — Filesystem fun

Augment, expand, and shrink filesystem paths.

```
augpath(path, suffix='', prefix='', ext=None, base=None, dpath=None, multidot=False)
    Modify components of a path string without parsing manually.
    augpath('/data/file.txt', ext='.csv')   → '/data/file.csv'
    augpath('/data/file.txt', prefix='new_') → '/data/new_file.txt'
    augpath('/data/file.txt', suffix='_v2')  → '/data/file_v2.txt'
    augpath('/data/file.txt', dpath='/out')   → '/out/file.txt'

expandpath(path)
    Shell-like expansion of ~ and $ENV_VAR in paths.
    expandpath('~/data/$PROJECT')       → '/home/user/data/myproject'

shrinkuser(path, home='~')
    Inverse of os.path.expanduser.
    shrinkuser('/home/user/data')       → '~/data'
```

---

## `queueutils` — Priority queues

Multiple priority queue implementations.

```
class PriorityQueue(**kw)
    A priority queue based on a sorted list. O(log n) insert, O(1) peek/pop.
    Best for small queues or when iteration order matters.

class HeapPriorityQueue(**kw)
    A priority queue using heapq. O(log n) insert/pop. Best general choice.

class SortedPriorityQueue(**kw)
    Priority queue using a sorted BarrelList. Good for large queues with
    many priority levels.

class BasePriorityQueue(**kw)
    Abstract base class. All priority queues share this API:
    .add(item, priority=None)     → add item
    .pop(default=_MISSING)        → remove and return lowest-priority item
    .peek(default=_MISSING)       → peek at next item
    .remove(item)                 → remove specific item
    .clear()                      len(pq)
    .__iter__()                   → iterate in priority order
```

### Recipes

```python
from boltons.queueutils import HeapPriorityQueue

pq = HeapPriorityQueue()
pq.add('low-task', priority=10)
pq.add('high-task', priority=1)
pq.add('mid-task', priority=5)
pq.pop()                                → 'high-task'
```

---

## `setutils` — `IndexedSet` type

Ordered set with O(1) positional access.

```
class IndexedSet(other=None)
    A set that maintains insertion order and supports positional indexing.
    Combines the features of a list and a set.

    Set API: .add() .discard() .remove() .pop() & | - ^ operators
    List API: s[0] s[-1] s[1:3] .index(val)
    Extras:
    .pop(index=-1)                → pop by position (default: last)
    .clear()                      len(s)
    .__contains__                 → O(1)
    .__getitem__                  → O(1)
    .index(val)                   → O(1) (unlike list)

complement(wrapped)
    Given a set, return a complement set that contains "everything else".
    Useful for exclusion logic.
```

### Recipes

```python
from boltons.setutils import IndexedSet

s = IndexedSet([3, 1, 4, 1, 5, 9])    # → IndexedSet([3, 1, 4, 5, 9])
s[0]                                    → 3
s[-1]                                   → 9
s.add(2)                                # appended
4 in s                                  → True  (O(1))
s | {10, 20}                            → IndexedSet([3,1,4,5,9,2,10,20])
```

---

## `socketutils` — `socket` wrappers

Buffered sockets and netstring protocol.

```
class BufferedSocket(sock, timeout=_UNSET, maxsize=32768, recvsize=_UNSET)
    Wraps a socket with buffered recv operations.
    .recv_until(delimiter, timeout=_UNSET, maxsize=_UNSET)
        → receive until delimiter found. Raises MessageTooLong if exceeded.
    .recv_size(size, timeout=_UNSET)
        → receive exactly size bytes.
    .recv(size)  .send(data)  .sendall(data)
    .peek(size)               → peek without consuming
    .flush()                  .close()
    .settimeout(timeout)      .getrecvbuffer()

class NetstringSocket(sock, timeout=10, maxsize=32768)
    Reads and writes using the netstring protocol (length-prefixed).
    .read_ns() → bytes         .write_ns(data)
    Safe framing for binary protocols.

# Exceptions
class Error(socket.error)              — base
class Timeout(socket.timeout)          — recv timeout
class ConnectionClosed                 — unexpected close
class MessageTooLong(bytes_read, delimiter)
class NetstringProtocolError           — base for netstring errors
class NetstringInvalidSize(msg)
class NetstringMessageTooLong(size, maxsize)
```

---

## `statsutils` — Statistics fundamentals

Pure-Python descriptive statistics with no dependencies.

```
class Stats(data, default=0.0, use_copy=True, is_sorted=False)
    All-in-one statistics object. Accepts any numeric iterable.
    .mean()          .median()         .mode()
    .std_dev()       .variance()       .median_abs_dev()
    .iqr()           .trimean()
    .skewness()      .kurtosis()       .pearson_type()
    .rel_std_dev()                     — coefficient of variation
    .get_quantile(q)                   — arbitrary quantile (0-1)
    .get_zscore(value)                 — z-score of a value
    .get_histogram_counts(bins=None, bin_digits=1)
    .format_histogram(bins=None, **kw) → ASCII histogram string
    .describe(quantiles=None, format=None) → summary dict

# Standalone functions (same as Stats methods)
mean(data, default=0.0)
median(data, default=0.0)
variance(data, default=0.0)
std_dev(data, default=0.0)
median_abs_dev(data, default=0.0)
iqr(data, default=0.0)
trimean(data, default=0.0)
skewness(data, default=0.0)
kurtosis(data, default=0.0)
pearson_type(data, default=0.0)
rel_std_dev(data, default=0.0)

describe(data, quantiles=None, format=None) → dict
    Quick summary: count, mean, std_dev, min, max, quartiles.

format_histogram_counts(bin_counts, width=None, format_bin=None)
    Format pre-computed histogram counts as ASCII art.
```

### Recipes

```python
from boltons.statsutils import Stats

s = Stats([1, 2, 3, 4, 5, 5, 6, 7, 8, 100])
s.mean()        → 14.1
s.median()      → 5.0
s.std_dev()     → 29.15...
s.iqr()         → 4.0
s.trimean()     → 4.75
print(s.format_histogram())   # ASCII histogram
```

---

## `strutils` — Text manipulation

Slugify, case conversion, byte formatting, HTML stripping, integer ranges, pluralization.

```
# ── Case Conversion ──
camel2under(camel_string)                → 'CamelCase' → 'camel_case'
under2camel(under_string)                → 'under_score' → 'UnderScore'
slugify(text, delim='_', lower=True, ascii=False) → URL/filename safe string
    slugify('Hello, World!!')            → 'hello_world'

# ── Encoding & Bytes ──
asciify(text, ignore=False) → bytes
    Convert Unicode to closest ASCII approximation (é→e, ñ→n).
bytes2human(nbytes, ndigits=0) → str
    bytes2human(1234567)                 → '1 MB'
    bytes2human(1234567, ndigits=2)      → '1.18 MB'
gzip_bytes(bytestring, level=6) → bytes
gunzip_bytes(bytestring) → bytes
is_ascii(text) → bool
is_uuid(obj, version=4) → bool

# ── HTML ──
html2text(html) → str
    Strip all HTML tags, decode entities.

strip_ansi(text) → str
    Remove ANSI escape codes from text.

# ── Integer Ranges ──
parse_int_list(range_string, delim=',', range_delim='-') → list
    parse_int_list('1,3,5-8,10')         → [1, 3, 5, 6, 7, 8, 10]

format_int_list(int_list, delim=',', range_delim='-', delim_space=False) → str
    format_int_list([1,3,5,6,7,8,10])    → '1,3,5-8,10'

int_ranges_from_int_list(range_string) → tuple of tuples
    int_ranges_from_int_list('1,3,5-8')  → ((1,1),(3,3),(5,8))

complement_int_list(range_string, range_start=0, range_end=None)
    Complement of an integer range string.

# ── Pluralization ──
pluralize(word) → str
    pluralize('mouse')                   → 'mice'
    pluralize('child')                   → 'children'
singularize(word) → str
    singularize('mice')                  → 'mouse'
cardinalize(unit_noun, count) → str
    cardinalize('mouse', 3)              → 'mice'
    cardinalize('mouse', 1)              → 'mouse'
ordinalize(number, ext_only=False) → str
    ordinalize(3)                        → '3rd'
    ordinalize(11)                       → '11th'
unit_len(sized_iterable, unit_noun='item') → str
    unit_len([1,2,3], 'file')            → '3 files'

# ── Text Processing ──
a10n(string) → str
    Abbreviation like i18n: a10n('internationalization') → 'i18n'
indent(text, margin, newline='\n', key=bool)
    Add margin to each line.
unwrap_text(text, ending='\n\n')
    Rejoin wrapped text into paragraphs.
iter_splitlines(text) → generator
    Like str.splitlines() but lazy.
split_punct_ws(text) → list
    Split on both punctuation and whitespace.
    split_punct_ws('hello, world!')      → ['hello', 'world']
find_hashtags(string) → list
    find_hashtags('hello #world #python') → ['world', 'python']

# ── Shell ──
args2cmd(args, sep=' ') → str              — alias: args2sh
escape_shell_args(args, sep=' ', style=None) → str

# ── Misc ──
class MultiReplace(sub_map, **kwargs)
    Multiple find/replace in a single pass. Efficient for many substitutions.
multi_replace(text, sub_map, **kwargs) → str
    Shortcut for MultiReplace.

removeprefix(text, prefix) → str          — backport of str.removeprefix

class HTMLTextExtractor()                  — used internally by html2text
class DeaccenterDict()                     — caching dict for asciify
```

### Recipes

```python
from boltons.strutils import (slugify, bytes2human, parse_int_list,
                               format_int_list, html2text, pluralize)

slugify('Héllo, Wörld!', ascii=True)     → 'hello_world'
bytes2human(1_500_000_000, 2)            → '1.40 GB'
parse_int_list('1-5,10,20-22')           → [1,2,3,4,5,10,20,21,22]
format_int_list([1,2,3,5,6,7,10])        → '1-3,5-7,10'
html2text('<p>Hello <b>World</b></p>')   → 'Hello World'
pluralize('octopus')                     → 'octopuses'
```

---

## `tableutils` — 2D data structure

Lightweight table for tabular data with multiple input formats.

```
class Table(data=None, headers=_MISSING, metadata=None)
    A simple, extensible 2D data structure. Accepts:
    - List of dicts
    - List of lists/tuples
    - List of namedtuples
    - List of objects (reads attributes)

    .headers          → list of column names
    .rows             → list of row data
    .to_html()        → HTML table string
    .to_text()        → plain text table
    .to_csv()         → CSV string
    .__len__()        → row count

# Input type registry
class InputType(*a, **kw)              — base
class DictInputType(*a, **kw)          — from list of dicts
class ListInputType(*a, **kw)          — from list of lists
class TupleInputType(*a, **kw)         — from list of tuples
class NamedTupleInputType(*a, **kw)    — from list of namedtuples
class ObjectInputType(*a, **kw)        — from list of objects

class UnsupportedData(...)             — raised for unrecognized input
```

---

## `tbutils` — Tracebacks and call stacks

Rich traceback/exception objects for programmatic inspection and formatting.

```
class TracebackInfo(frames)
    Basic traceback representation.
    .frames           → list of Callpoint objects
    .to_dict()        .to_text()     .to_string()
    TracebackInfo.from_current()     → from current stack
    TracebackInfo.from_traceback(tb) → from sys.exc_info()[2]

class ContextualTracebackInfo(frames)
    TracebackInfo with local variable context in each frame.

class ExceptionInfo(exc_type, exc_msg, tb_info)
    Full exception info: type, message, traceback.
    .to_dict()        .to_string()
    ExceptionInfo.from_current()     → from sys.exc_info()

class ContextualExceptionInfo(exc_type, exc_msg, tb_info)
    ExceptionInfo with local variables captured.

class Callpoint(module_name, module_path, func_name, lineno, lasti, line=None)
    A single frame in a traceback.
    .to_dict()        .to_string()

class ContextualCallpoint(*a, **kw)
    Callpoint with .local_reprs dict of local variable representations.

class ParsedException(exc_type_name, exc_msg, frames=None)    — alias: ParsedTB
    Parse a traceback string back into a structured object.
    ParsedException.from_string(tb_text)

fix_print_exception()
    Replace sys.excepthook with boltons' version (better formatting).

print_exception(etype, value, tb, limit=None, file=None)
format_exception_only(etype, value) → list
```

### Recipes

```python
from boltons.tbutils import ExceptionInfo, ContextualExceptionInfo

try:
    1 / 0
except:
    ei = ContextualExceptionInfo.from_current()
    print(ei.to_string())   # includes local variables!
    log_dict = ei.to_dict() # structured for JSON logging
```

---

## `timeutils` — `datetime` additions

ISO parsing, timedelta parsing, relative time, daterange.

```
isoparse(iso_str) → datetime
    Parse ISO 8601 date/time strings (the subset Python emits).
    isoparse('2026-02-08T14:30:00')     → datetime(2026, 2, 8, 14, 30)

parse_timedelta(text) → timedelta                   — alias: parse_td
    Parse human-readable durations.
    parse_timedelta('1h 30m')            → timedelta(hours=1, minutes=30)
    parse_timedelta('2 days 5 hours')    → timedelta(days=2, hours=5)
    parse_timedelta('500ms')             → timedelta(milliseconds=500)

relative_time(d, other=None, ndigits=0) → str
    Human-readable relative time.
    relative_time(then)                  → '2 hours ago'
    relative_time(then, now)             → '3 days from now'

decimal_relative_time(d, other=None, ndigits=0, cardinalize=True) → tuple
    Returns (value, unit_string) tuple.
    decimal_relative_time(then)          → (2.5, 'hours')

daterange(start, stop, step=1, inclusive=False) → generator
    Like range() for dates.
    daterange(date(2026,1,1), date(2026,1,5))
    → date(2026,1,1), date(2026,1,2), date(2026,1,3), date(2026,1,4)
    step can be int (days) or timedelta.

dt_to_timestamp(dt) → float
    Convert datetime to UNIX timestamp (works on Python 2+3).

strpdate(string, format) → date
    Like strptime but returns date, not datetime.

total_seconds(td) → float
    Backport of timedelta.total_seconds().

# Timezone types
class ConstantTZInfo(name='ConstantTZ', offset=timedelta(0))
    Fixed-offset timezone.
class LocalTZInfo()
    Represents the local timezone using time module data.
class USTimeZone(hours, reprname, stdname, dstname)
    US timezone with DST support.
```

### Recipes

```python
from boltons.timeutils import isoparse, parse_timedelta, relative_time, daterange

dt = isoparse('2026-02-08T14:30:00')
td = parse_timedelta('2d 5h 30m')
print(relative_time(dt))               # "3 hours ago"

from datetime import date
for d in daterange(date(2026, 1, 1), date(2026, 2, 1)):
    print(d)                            # every day in January
```

---

## `typeutils` — Type handling

Classproperty, subclass discovery, safe issubclass.

```
class classproperty(fn)
    Like @property but for the class itself (not instances).
    class MyClass:
        @classproperty
        def table_name(cls):
            return cls.__name__.lower()
    MyClass.table_name              → 'myclass'

get_all_subclasses(cls) → list
    Recursively find all subclasses of a class.
    get_all_subclasses(Exception)   → [ValueError, TypeError, ...]

issubclass(subclass, baseclass) → bool
    Safe issubclass that doesn't raise TypeError for non-classes.
    issubclass(42, int)             → False (builtin raises TypeError)

make_sentinel(name='_MISSING', var_name=None)
    (Same as in cacheutils — re-exported here.)
```

---

## `urlutils` — Structured URL

Full URL type with component access, query manipulation, link extraction.

```
class URL(url='')
    Structured URL object. Parse, modify, and rebuild URLs cleanly.
    URL('https://user:pass@host:443/path?q=1#frag')

    Properties (get/set):
    .scheme  .username  .password  .host  .port  .path
    .query_params        → QueryParamDict (OrderedMultiDict subtype)
    .fragment            .netloc
    .authority           — user:pass@host:port
    .is_absolute         .to_text()  str(url)

    Methods:
    .navigate(url)       → resolve relative URL against this base
    .normalize()         → canonical form
    .to_text()           → string

class QueryParamDict(*a, **kw)
    OrderedMultiDict specialized for URL query parameters.
    Handles ?key=val1&key=val2 correctly.

class URLParseError(...)
    Raised on invalid URL parsing.

# Functions
find_all_links(text, with_text=False, default_scheme='https', schemes=())
    Heuristic extraction of URLs from plain text.
    find_all_links('Visit https://x.com or y.com')
    → ['https://x.com', 'https://y.com']

parse_url(url_text) → dict
    Low-level URL parsing into component dict.

parse_host(host) → dict
    Parse host portion into family, address, port.

parse_qsl(qs, keep_blank_values=True, encoding='utf8') → list
    Parse query string into (key, value) pairs.

# Quoting
quote_path_part(text, full_quote=True)
quote_query_part(text, full_quote=True)
quote_fragment_part(text, full_quote=True)
quote_userinfo_part(text, full_quote=True)
unquote(string, encoding='utf-8', errors='replace')

resolve_path_parts(path_parts)
    Normalize . and .. in path segments.

register_scheme(text, uses_netloc=None, default_port=None)
    Register a custom URL scheme for correct parsing.
```

### Recipes

```python
from boltons.urlutils import URL, find_all_links

# Parse and modify
u = URL('https://api.example.com/v2/users?page=1&limit=50')
u.host                               → 'api.example.com'
u.path                               → '/v2/users'
u.query_params['page']               → '1'
u.query_params['page'] = '2'
u.path = '/v3/users'
str(u)                               → 'https://api.example.com/v3/users?page=2&limit=50'

# Extract links from text
links = find_all_links(email_body)

# Resolve relative URL
base = URL('https://example.com/docs/guide/')
abs_url = base.navigate('../api/ref')
str(abs_url)                         → 'https://example.com/docs/api/ref'
```
