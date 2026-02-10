# more-itertools `10.8.0` — Complete Reference

> 160+ functions extending itertools · The standard "itertools recipes" library
> `pip install more-itertools` · Python ≥3.9 · ~3.8k ★ · 200M+ monthly downloads
> Pure Python · No dependencies · Feb 2026

---

## Grouping

Split iterables into groups, chunks, and batches.

```
chunked(iterable, n, strict=False) → list of lists
    Break into lists of length n. Last chunk may be shorter.
    chunked('ABCDEFG', 3)               → [['A','B','C'],['D','E','F'],['G']]
    strict=True: raise if final chunk is shorter.

ichunked(iterable, n) → iterator of iterators
    Lazy chunked. Each sub-iterator must be consumed before the next.

batched(iterable, n, *, strict=False) → iterator of tuples
    Like chunked but yields tuples. Matches itertools.batched (3.12+).
    batched('ABCDEFG', 3)               → ('A','B','C'), ('D','E','F'), ('G',)

sliced(seq, n, strict=False) → iterator of slices
    Yield n-length slices of a SEQUENCE (not iterator). Uses indexing.
    sliced([1,2,3,4,5], 2)              → [1,2], [3,4], [5]

chunked_even(iterable, n)
    Break into lists of APPROXIMATELY length n, distributing evenly.
    chunked_even(range(10), 3)           → [[0,1,2,3],[4,5,6],[7,8,9]]

constrained_batches(iterable, max_size, max_count=None, get_len=len, strict=False)
    Batch items with a combined size limit. Useful for API rate limits.
    constrained_batches(['ab','cde','f','ghij'], max_size=5)
    → ['ab','cde'], ['f'], ['ghij']     (each batch ≤ 5 chars total)

distribute(n, iterable) → list of iterators
    Distribute items round-robin among n sub-iterators.
    distribute(3, range(7))              → [0,3,6], [1,4], [2,5]

divide(n, iterable) → list of iterators
    Divide into n contiguous parts.
    divide(3, range(7))                  → [0,1,2], [3,4], [5,6]

grouper(iterable, n, incomplete='fill', fillvalue=None)
    Fixed-size groups. incomplete: 'fill'|'strict'|'ignore'.
    grouper('ABCDEFG', 3, fillvalue='x') → ('A','B','C'), ('D','E','F'), ('G','x','x')
    grouper('ABCDEFG', 3, incomplete='ignore') → ('A','B','C'), ('D','E','F')

groupby_transform(iterable, keyfunc=None, valuefunc=None, reducefunc=None)
    Extended groupby: transform values and/or reduce each group.
    groupby_transform('aAbBcC', str.lower, str.upper, list)
    → ('a',['A','A']), ('b',['B','B']), ('c',['C','C'])

split_at(iterable, pred, maxsplit=-1, keep_separator=False) → lists
    Split at items matching pred.
    split_at([1,2,0,3,4,0,5], lambda x: x==0) → [[1,2],[3,4],[5]]
    keep_separator=True: include separator in output.

split_before(iterable, pred, maxsplit=-1) → lists
    Split just before items matching pred.
    split_before('OneTwo', str.isupper)  → [['O','n','e'],['T','w','o']]

split_after(iterable, pred, maxsplit=-1) → lists
    Split just after items matching pred.

split_when(iterable, pred, maxsplit=-1) → lists
    Split when pred(prev, current) is True.
    split_when([1,2,3,1,2], lambda a,b: b<a) → [[1,2,3],[1,2]]

split_into(iterable, sizes) → lists
    Split into pieces of specified sizes.
    split_into(range(9), [2,3,4])        → [[0,1],[2,3,4],[5,6,7,8]]

class bucket(iterable, key, validator=None)
    Lazy group-by: access groups on demand without materializing all.
    b = bucket('abcABC', str.lower)
    list(b['a'])                         → ['a', 'A']
    Available keys discovered lazily.

unzip(iterable)
    Inverse of zip.
    unzip([(1,'a'),(2,'b'),(3,'c')])     → (1,2,3), ('a','b','c')

map_reduce(iterable, keyfunc, valuefunc=None, reducefunc=None) → dict
    Single-pass group + transform + reduce.
    map_reduce([1,2,3,4], lambda x: x%2, lambda x: x*10)
    → {1: [10, 30], 0: [20, 40]}

join_mappings(**field_to_map) → dict of dicts
    Join mappings on common keys (like SQL inner join).
    join_mappings(name={1:'a',2:'b'}, age={1:30,2:25})
    → {1: {'name':'a','age':30}, 2: {'name':'b','age':25}}
```

---

## Lookahead & Inspection

Peek, count, check properties of iterables without consuming them.

```
spy(iterable, n=1) → (list, iterator)
    Peek at first n items without consuming the iterator.
    head, it = spy(range(100), 3)
    head → [0,1,2]; it still yields 0,1,2,3,...

class peekable(iterable)
    Wrapper allowing lookahead and prepend.
    p = peekable([1,2,3])
    p.peek()                   → 1 (doesn't consume)
    p.peek(default='end')      → 'end' when exhausted
    p[0], p[1]                 → lookahead by index
    p[:3]                      → lookahead slice
    p.prepend(0)               → push items back
    next(p)                    → 0 (prepended)

class seekable(iterable, maxlen=None)
    Wrapper allowing seeking backward and forward.
    s = seekable(gen())
    next(s); next(s); next(s)
    s.seek(0)                  → rewind to beginning
    s.seek(1)                  → go to position 1
    s.peek()                   → peek without consuming
    s.elements()               → cached elements so far
    maxlen: limit cache size.

class countable(iterable)
    Wrapper that counts items consumed.
    c = countable(range(10))
    next(c); next(c)
    c.items_seen               → 2

ilen(iterable) → int
    Count items by consuming the iterable.
    ilen(x for x in range(1000) if x%2)  → 500

is_sorted(iterable, key=None, reverse=False, strict=False) → bool
    Check if sorted without materializing.
    is_sorted([1, 2, 2, 3])             → True
    is_sorted([1, 2, 2, 3], strict=True)→ False

all_equal(iterable, key=None) → bool
    True if all items are equal.
    all_equal([1, 1, 1])                 → True

all_unique(iterable, key=None) → bool
    True if no duplicates.

exactly_n(iterable, n, predicate=bool) → bool
    True if exactly n items satisfy predicate.

iequals(*iterables) → bool
    True if all iterables yield equal sequences (lazy).
```

---

## Selecting

Choose, filter, and extract specific elements.

```
first(iterable, default=_missing) → item
    first([0, None, 'a'])                → 0
    first([], default='x')               → 'x'
    Raises ValueError if empty and no default.

last(iterable, default=_missing) → item
    last([1, 2, 3])                      → 3

one(iterable, too_short=None, too_long=None) → item
    Assert exactly one item and return it. Raises on 0 or 2+.

only(iterable, default=None, too_long=None) → item
    Like one() but returns default for empty. Raises on 2+.

strictly_n(iterable, n, too_short=None, too_long=None) → list
    Assert exactly n items and return them.

nth(iterable, n, default=None) → item
    Return nth item (0-indexed). Consumes up to n.

nth_or_last(iterable, n, default=_missing) → item
    Return nth item, or last if fewer than n+1.

take(n, iterable) → list
    First n items as a list.

tail(n, iterable) → iterator
    Last n items (uses deque for O(n) memory).

unique_everseen(iterable, key=None) → iterator
    Yield unique items preserving order. O(n) memory.
    unique_everseen('AABABC')            → A, B, C

unique_justseen(iterable, key=None) → iterator
    Yield unique items, deduplicating only consecutive runs.
    unique_justseen('AABABC')            → A, B, A, B, C

unique_in_window(iterable, n, key=None) → iterator
    Yield items unique within a sliding window of n.

unique(iterable, key=None, reverse=False) → iterator
    Yield unique items in sorted order.

duplicates_everseen(iterable, key=None) → iterator
    Yield items seen more than once (after first occurrence).

duplicates_justseen(iterable, key=None) → iterator
    Yield consecutive duplicates.

classify_unique(iterable, key=None) → (item, is_first_seen, is_new_consec_run)
    Classify each element's uniqueness status.

strip(iterable, pred) → iterator
    Strip items matching pred from both ends.
lstrip(iterable, pred) → iterator
    Strip from the beginning.
rstrip(iterable, pred) → iterator
    Strip from the end.

filter_except(validator, iterable, *exceptions) → iterator
    Yield items for which validator doesn't raise listed exceptions.

filter_map(func, iterable) → iterator
    Apply func; yield result only if not None.
    filter_map(lambda x: x*2 if x>0 else None, [-1,2,-3,4]) → 4, 8

map_except(function, iterable, *exceptions) → iterator
    Apply function; skip items that raise listed exceptions.

map_if(iterable, pred, func, func_else=None) → iterator
    Conditional map.
    map_if([1,-2,3,-4], lambda x: x>0, lambda x: x*10, lambda x: 0)
    → 10, 0, 30, 0

before_and_after(predicate, it) → (before_iter, after_iter)
    Split at first False predicate. Both iterators share the source.

takewhile_inclusive(predicate, iterable) → iterator
    Like takewhile but includes the first failing element.

locate(iterable, pred=bool, window_size=None) → iterator of indices
    Yield indices where pred is True.
    locate([0, 1, 0, 1, 1], pred=bool)  → 1, 3, 4

rlocate(iterable, pred=bool, window_size=None) → iterator
    Like locate but from the right.

extract(iterable, indices) → iterator
    Yield items at the specified indices (sorted).
    extract('abcde', [0, 2, 4])          → 'a', 'c', 'e'

first_true(iterable, default=None, pred=None) → item
    Return first truthy item (or matching pred).
```

---

## Windowing

Sliding windows and overlapping views.

```
windowed(seq, n, fillvalue=None, step=1) → iterator of tuples
    Sliding window with configurable step.
    windowed([1,2,3,4,5], 3)             → (1,2,3),(2,3,4),(3,4,5)
    windowed([1,2,3,4,5], 3, step=2)     → (1,2,3),(3,4,5)
    windowed([1,2,3], 4, fillvalue=0)    → (1,2,3,0)

windowed_complete(iterable, n)
    Yield (beginning, middle, end) tuples. Middle is n-wide window.
    windowed_complete([1,2,3,4,5], 3)
    → ((),       (1,2,3), (4,5))
    → ((1,),     (2,3,4), (5,))
    → ((1,2),    (3,4,5), ())

sliding_window(iterable, n) → iterator of tuples
    Simpler sliding window (no fill, no step).

pairwise(iterable) → iterator of 2-tuples
    pairwise([1,2,3,4])                  → (1,2),(2,3),(3,4)

triplewise(iterable) → iterator of 3-tuples
    triplewise([1,2,3,4,5])              → (1,2,3),(2,3,4),(3,4,5)

stagger(iterable, offsets=(-1,0,1), longest=False, fillvalue=None)
    Yield tuples of items at specified offsets relative to each position.
    stagger([1,2,3,4], offsets=(0,1,2))  → (1,2,3),(2,3,4)

substrings(iterable) → iterator
    All contiguous substrings (subsequences).
    substrings('abc')                    → 'a','b','c','ab','bc','abc'

substrings_indexes(seq, reverse=False)
    Yield (substring, start, stop) for all substrings.

subslices(iterable)
    All contiguous non-empty subslices.
```

---

## Augmenting

Add elements, side effects, and metadata to iterables.

```
count_cycle(iterable, n=None)
    Cycle through items up to n times, yielding (count, item).
    count_cycle('AB', 3)                 → (0,'A'),(0,'B'),(1,'A'),(1,'B'),(2,'A'),(2,'B')

intersperse(e, iterable, n=1) → iterator
    Insert e every n items.
    intersperse('|', [1,2,3])            → 1, '|', 2, '|', 3
    intersperse('|', [1,2,3,4,5], n=2)   → 1, 2, '|', 3, 4, '|', 5

padded(iterable, fillvalue=None, n=None, next_multiple=False)
    Pad iterable with fillvalue to length n.
    padded([1,2], fillvalue=0, n=5)      → 1, 2, 0, 0, 0
    next_multiple=True: pad to next multiple of n.

pad_none(iterable) / padnone(iterable)
    Yield items, then None forever.

repeat_each(iterable, n=2)
    Repeat each element n times.
    repeat_each('AB', 3)                 → 'A','A','A','B','B','B'

repeat_last(iterable, default=None)
    After exhaustion, keep yielding the last item forever.

ncycles(iterable, n) → iterator
    Repeat the entire iterable n times.

adjacent(predicate, iterable, distance=1) → (bool, item)
    Mark items that are adjacent to items matching predicate.
    adjacent(lambda x: x==3, [1,2,3,4,5])
    → (F,1),(T,2),(T,3),(T,4),(F,5)

mark_ends(iterable) → (is_first, is_last, item)
    mark_ends('ABC')                     → (T,F,'A'),(F,F,'B'),(F,T,'C')

side_effect(func, iterable, chunk_size=None, before=None, after=None)
    Call func on each item (or chunk) as a side effect while iterating.
    before/after: callables run at start/end.

tabulate(function, start=0)
    Yield func(0), func(1), func(2), ...

consume(iterator, n=None)
    Advance iterator by n steps (or exhaust it if n is None).

prepend(value, iterator) → iterator
    Yield value first, then items from iterator.

value_chain(*args)
    Yield from each arg; if arg is iterable, yield from it, else yield it.
    value_chain(1, [2,3], 4)             → 1, 2, 3, 4
```

---

## Combining

Merge, interleave, zip, and combine multiple iterables.

```
collapse(iterable, base_type=None, levels=None) → iterator
    Deep flatten. Levels controls depth (None=unlimited).
    collapse([[1,[2]],[[3],4]])          → 1, 2, 3, 4
    collapse([[1,[2]]], levels=1)        → 1, [2]

flatten(listOfLists) → iterator
    Single-level flatten (alias for chain.from_iterable).

interleave(*iterables)
    Round-robin, stopping at shortest.
    interleave([1,2,3], [4,5])           → 1, 4, 2, 5

interleave_longest(*iterables)
    Round-robin, continuing to longest.
    interleave_longest([1,2,3], [4,5])   → 1, 4, 2, 5, 3

interleave_evenly(iterables, lengths=None)
    Interleave so elements from each iterable are evenly distributed.

interleave_randomly(*iterables)
    Randomly select which iterable to yield from next.

roundrobin(*iterables)
    Classic round-robin interleave.

sort_together(iterables, key_list=(0,), key=None, reverse=False, strict=False)
    Sort multiple iterables together by one or more key iterables.
    sort_together([[3,1,2], ['c','a','b']]) → ([1,2,3], ['a','b','c'])

zip_equal(*iterables)
    Like zip but raises UnequalIterablesError if lengths differ.

zip_offset(*iterables, offsets, longest=False, fillvalue=None)
    Zip with offsets applied to each iterable.

zip_broadcast(*objects, scalar_types=(str, bytes), strict=False)
    Zip that broadcasts scalars to match iterable length.
    zip_broadcast([1,2,3], 'x')          → (1,'x'), (2,'x'), (3,'x')

partial_product(*iterables)
    Like product but changing one element at a time.

outer_product(func, xs, ys, *args, **kwargs)
    Apply func(x, y) for all x in xs, y in ys.

dotproduct(vec1, vec2) → number
convolve(signal, kernel) → iterator
matmul(m1, m2) → matrix
transpose(it) → iterator of tuples
reshape(matrix, shape) → iterator
```

---

## Math & Statistics

Primes, factoring, polynomials, numeric ranges, descriptive stats.

```
# ── Aggregation ──
minmax(iterable_or_value, *others, key=None, default=_missing)
    Return (min, max) in a single pass.
    minmax([3,1,4,1,5])                  → (1, 5)

quantify(iterable, pred=bool) → int
    Count truthy items.
    quantify([True, False, True])        → 2

sum_of_squares(it) → number

running_median(iterable, *, maxlen=None) → iterator
    Cumulative or sliding-window median.

# ── Number Theory ──
factor(n) → iterator
    Prime factors of n.
    list(factor(360))                    → [2, 2, 2, 3, 3, 5]

sieve(n) → iterator
    Primes less than n (Sieve of Eratosthenes).
    list(sieve(20))                      → [2, 3, 5, 7, 11, 13, 17, 19]

is_prime(n) → bool

nth_prime(n, *, approximate=False) → int
    nth_prime(0) → 2, nth_prime(3) → 7

totient(n) → int
    Euler's totient: count of integers up to n coprime with n.

multinomial(*counts) → int
    Number of distinct arrangements of a multiset.

# ── Polynomials ──
polynomial_from_roots(roots) → list of coefficients
polynomial_eval(coefficients, x) → number
polynomial_derivative(coefficients) → list

# ── Fourier ──
dft(xarr) → list of complex
idft(Xarr) → list of complex

# ── Numeric Range ──
class numeric_range(*args)
    Like range() but for float, Decimal, Fraction, datetime, etc.
    numeric_range(0.0, 1.0, 0.3)         → 0.0, 0.3, 0.6, 0.9
    numeric_range(Decimal('0'), Decimal('1'), Decimal('0.25'))
    Supports len(), indexing, slicing, reversed, contains.
```

---

## Combinatorics

Permutations, combinations, partitions, powerset, derangements.

```
distinct_permutations(iterable, r=None)
    Yield permutations without duplicates (even with repeated elements).
    distinct_permutations([1,1,2])       → (1,1,2),(1,2,1),(2,1,1)

distinct_combinations(iterable, r)
    Combinations without duplicates.

derangements(iterable, r=None)
    Permutations where no element is in its original position.

circular_shifts(iterable, steps=1)
    circular_shifts([1,2,3,4])           → (1,2,3,4),(2,3,4,1),(3,4,1,2),(4,1,2,3)

partitions(iterable)
    All order-preserving partitions.
    partitions([1,2,3])                  → [[1,2,3]], [[1],[2,3]], [[1,2],[3]], [[1],[2],[3]]

set_partitions(iterable, k=None, min_size=None, max_size=None)
    Set partitions into k parts (unordered).

powerset(iterable)
    All subsets.
    powerset([1,2,3])                    → (),{1},{2},{3},{1,2},{1,3},{2,3},{1,2,3}

powerset_of_sets(iterable)
    All subsets as frozensets.

gray_product(*iterables)
    Product in Gray code order (adjacent tuples differ by one element).

# ── Index-based access to combinatorial objects ──
product_index(element, *args) → int
nth_product(index, *args) → tuple
random_product(*args, repeat=1) → tuple

combination_index(element, iterable) → int
combination_with_replacement_index(element, iterable) → int
nth_combination(iterable, r, index) → tuple
nth_combination_with_replacement(iterable, r, index) → tuple
random_combination(iterable, r) → tuple
random_combination_with_replacement(iterable, r) → tuple

permutation_index(element, iterable) → int
nth_permutation(iterable, r, index) → tuple
random_permutation(iterable, r=None) → tuple
```

---

## Utilities & Wrappers

General-purpose helpers and iterator wrappers.

```
always_iterable(obj, base_type=(str, bytes))
    Ensure obj is iterable. Strings/bytes stay as-is.
    always_iterable(42)                  → iter([42])
    always_iterable([1,2])               → iter([1,2])
    always_iterable('hi')               → iter(['hi'])  # string not split

always_reversible(iterable)
    reversed() for any iterable (caches if needed).

consumer(func)
    Decorator that auto-advances a generator-based "reverse iterator"
    (PEP 342 send-style coroutine).

with_iter(context_manager)
    Use a context manager as an iterator; closes on exhaustion.

iter_except(func, exception, first=None)
    Repeatedly call func() until exception is raised.
    iter_except(d.popitem, KeyError)     → yields all items from dict

iter_suppress(iterable, *exceptions)
    Yield items, silently stopping if an exception is raised.

class callback_iter(func, callback_kwd='callback', wait_seconds=0.1)
    Convert a callback-based function into an iterator.

class time_limited(limit_seconds, iterable)
    Yield items until time limit exceeded.
    .timed_out                           → True if time ran out

class islice_extended(iterable, *args)
    islice that supports negative indices.
    islice_extended('ABCDEFG', -3, None) → 'E', 'F', 'G'

class run_length
    Run-length encoding/decoding.
    run_length.encode('aabbccc')         → ('a',2),('b',2),('c',3)
    run_length.decode([('a',2),('b',3)]) → 'a','a','b','b','b'

class SequenceView(target)
    Read-only view of a sequence. Reflects changes to the original.

class numeric_range(*args)
    (See Math section above.)

consecutive_groups(iterable, ordering=None) → groups
    Group consecutive numbers.
    consecutive_groups([1,2,3,5,6,8])    → [1,2,3],[5,6],[8]

sample(iterable, k, weights=None, *, counts=None, strict=False) → list
    Reservoir sampling: random sample without replacement from an iterable
    of unknown length.

repeatfunc(func, times=None, *args)
    Call func(*args) repeatedly.
    repeatfunc(random.random, 5)         → 5 random floats

iterate(func, start)
    start, func(start), func(func(start)), ...
    take(5, iterate(lambda x: x*2, 1))  → [1, 2, 4, 8, 16]

difference(iterable, func=sub, *, initial=None)
    Inverse of accumulate.
    difference(accumulate([1,2,3]))      → 1, 2, 3

make_decorator(wrapping_func, result_index=0)
    Turn a wrapping function into a decorator.

replace(iterable, pred, substitutes, count=None, window_size=1)
    Replace items matching pred with substitutes.

loops(n) → iterable
    Efficient loop counter (faster than range for pure iteration).
    for _ in loops(1000000): pass

raise_(exception, *args)
    Raise an exception as an expression (useful in lambdas).

longest_common_prefix(iterables)
    Yield elements of the longest common prefix.

argmin(iterable, *, key=None) → int
argmax(iterable, *, key=None) → int
    Index of minimum/maximum value.

doublestarmap(func, iterable)
    Like starmap but unpacks dicts: func(**item).
```

---

## Recipes Quick Reference

```python
from more_itertools import (
    chunked, batched, flatten, collapse, first, last, one, only,
    unique_everseen, peekable, seekable, windowed, pairwise,
    interleave_longest, roundrobin, partition, bucket,
    split_at, split_before, split_after, split_when,
    spy, ilen, is_sorted, all_equal, all_unique,
    minmax, quantify, numeric_range, powerset,
    distinct_permutations, always_iterable, time_limited,
    mark_ends, side_effect, consecutive_groups, sample,
    run_length, locate, extract, map_reduce,
    constrained_batches, sort_together, zip_equal,
)

# ── Batch API calls ──
for batch in constrained_batches(records, max_size=1_000_000, get_len=len):
    api.send(batch)

# ── Peek at stream ──
head, stream = spy(event_stream, 5)
if is_valid_header(head):
    process(stream)

# ── Safe single-item extraction ──
config = one(configs, too_short=ValueError("No config found"))

# ── Time-limited processing ──
for item in time_limited(30, huge_generator):
    process(item)
if time_limited.timed_out:
    log.warn("Processing timed out")

# ── Partition into success/failure ──
falsy, truthy = partition(lambda r: r.ok, responses)
# ⚠ NOTE: returns (falsy, truthy) — opposite of boltons!

# ── Run-length encoding ──
list(run_length.encode('aaabbbcccc'))    → [('a',3),('b',3),('c',4)]

# ── Find consecutive groups ──
list(consecutive_groups([1,2,3,10,11,20]))
→ [[1,2,3], [10,11], [20]]

# ── Reservoir sampling from unknown-length stream ──
sampled = sample(log_lines_generator(), k=1000)

# ── Sliding window analysis ──
for w in windowed(prices, 7):
    moving_avg = sum(w) / 7

# ── Multi-key sort ──
names, ages, scores = sort_together([names, ages, scores], key_list=(2,), reverse=True)

# ── Lazy group-by ──
b = bucket(log_entries, key=lambda e: e['level'])
for error in b['ERROR']:
    alert(error)

# ── Powerset search ──
for subset in powerset(features):
    evaluate_model(subset)
```

---

## more-itertools vs boltons.iterutils

| Task | more-itertools | boltons |
|---|---|---|
| Chunk | `chunked` | `chunked` |
| Window | `windowed(step=)` | `windowed(fill=)` |
| Pairwise | `pairwise` | `pairwise(end=)` |
| Flatten | `flatten` (1 level), `collapse` (deep) | `flatten` (1 level) |
| Unique | `unique_everseen` | `unique` |
| Partition | `partition` → **(falsy, truthy)** | `partition` → **(truthy, falsy)** ⚠ |
| Group by | `bucket` (lazy) | `bucketize` (eager dict) |
| Peek | `peekable`, `spy` | — |
| Seekable | `seekable` | — |
| Time-limited | `time_limited` | — |
| Combinatorics | ✅ 20+ functions | — |
| Primes/math | ✅ factor, sieve, etc. | — |
| Nested remap | — | ✅ `remap` (killer feature) |
| Backoff | — | ✅ `backoff` |
| Int ranges | — | ✅ parse/format_int_list |
| Run-length | `run_length` | — |
| Reservoir sample | `sample` | — |
