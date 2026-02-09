"""Sqid (Sequential Quick ID) parser for hierarchical task IDs.

Sqid format: PID_PREFIX.COUNTER[.CHILD_INDEX...]

Examples:
- "Xa.1"      - Root level, 1st action
- "Xa.1.1"    - Child of Xa.1, 1st sub-action
- "Xa.1.2.3"  - 3 levels deep

This replaces UUID4 for process-isolated task tracking.
89% smaller than UUID4 (4-12 chars vs 36).

Python 3.12+ features used:
- Type aliases (PEP 695): `type Name = ...`
- StrEnum (PEP 663): Type-safe enums
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

# ============================================================================
# Type Aliases (PEP 695 - Python 3.12+)
# ============================================================================

type SqidString = str


# ============================================================================
# LogFormat Enum
# ============================================================================

class LogFormat(StrEnum):
    """Log format type detection."""
    COMPACT = "compact"    # New compact field names (ts, tid, lvl, mt, at, st, dur, msg)
    LEGACY = "legacy"      # Legacy Eliot field names (timestamp, task_uuid, etc.)
    AUTO = "auto"          # Auto-detect from content
    UNKNOWN = "unknown"


# ============================================================================
# SqidInfo Dataclass
# ============================================================================

@dataclass(frozen=True, slots=True)
class SqidInfo:
    """Parsed information from a Sqid task ID."""

    sqid: str              # Original Sqid string
    pid_prefix: str        # 2-character PID prefix (base62)
    counter: int           # Entry counter (base62, sequential)
    depth: int             # Nesting depth (number of levels)
    child_indices: tuple[int, ...]  # Child indices for nested actions
    is_root: bool          # True if no child indices (e.g., "Xa.1")
    parent: str | None     # Parent Sqid (None if root)


# ============================================================================
# SqidParser
# ============================================================================

class SqidParser:
    """Parse hierarchical Sqid task IDs.

    Uses boltons-style iteration patterns for clean traversal.
    """

    # Base62 alphabet for encoding/decoding
    _ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    _BASE = 62

    @classmethod
    def parse(cls, sqid: str) -> SqidInfo:
        """Parse a Sqid into its components.

        Args:
            sqid: Sqid string like "Xa.1" or "Xa.1.2.3"

        Returns:
            SqidInfo with parsed components

        Raises:
            ValueError: If sqid format is invalid
        """
        if not sqid or "." not in sqid:
            raise ValueError(f"Invalid Sqid format: {sqid!r}")

        parts = sqid.split(".")
        if len(parts) < 2:
            raise ValueError(f"Invalid Sqid format (too few parts): {sqid!r}")

        # First part is PID_PREFIX.COUNTER combined
        prefix_counter = parts[0]
        if len(prefix_counter) < 2:
            raise ValueError(f"Invalid PID prefix/counter: {prefix_counter!r}")

        # Extract PID prefix (first 2 chars)
        pid_prefix = prefix_counter[:2]

        # Parse counter (remaining chars)
        counter_str = prefix_counter[2:]
        if counter_str:
            counter = cls._decode_base62(counter_str)
        else:
            # No explicit counter in prefix part, check first child index
            counter = int(parts[1]) if len(parts) > 1 else 1

        # Child indices are parts[1:] (excluding prefix/counter)
        child_indices: tuple[int, ...] = ()
        if len(parts) > 1:
            # All parts after the first are child indices
            try:
                child_indices = tuple(int(p) for p in parts[1:])
            except ValueError as e:
                raise ValueError(f"Invalid child indices in Sqid: {sqid!r}") from e

        depth = len(parts) - 1  # Number of levels minus prefix

        return SqidInfo(
            sqid=sqid,
            pid_prefix=pid_prefix,
            counter=counter,
            depth=depth,
            child_indices=child_indices,
            is_root=(depth == 0 or (depth == 1 and len(child_indices) == 1)),
            parent=cls.parent(sqid),
        )

    @classmethod
    def parent(cls, sqid: str) -> str | None:
        """Get the parent Sqid.

        Args:
            sqid: Sqid string like "Xa.1.2.3"

        Returns:
            Parent Sqid like "Xa.1.2", or None if root
        """
        if "." not in sqid:
            return None

        parts = sqid.split(".")
        if len(parts) <= 1:
            return None

        if len(parts) == 2:
            # "Xa.1" -> "Xa" (but this is likely invalid, return None)
            return None

        # Remove the last child index
        return ".".join(parts[:-1])

    @classmethod
    def depth(cls, sqid: str) -> int:
        """Get the nesting depth of a Sqid.

        Args:
            sqid: Sqid string

        Returns:
            Depth level (1 for root like "Xa.1", 2 for "Xa.1.1", etc.)
        """
        if "." not in sqid:
            return 0
        return len(sqid.split(".")) - 1

    @classmethod
    def is_child_of(cls, parent: str, child: str) -> bool:
        """Check if child Sqid is a descendant of parent.

        Args:
            parent: Parent Sqid
            child: Child Sqid to check

        Returns:
            True if child is a descendant of parent
        """
        if not child.startswith(parent):
            return False

        # Ensure we match at boundary
        if len(child) > len(parent):
            next_char = child[len(parent)]
            return next_char == "."

        return False  # Same Sqid is not a child

    @classmethod
    def is_sibling_of(cls, sqid1: str, sqid2: str) -> bool:
        """Check if two Sqids are siblings (same parent, different position).

        Args:
            sqid1: First Sqid
            sqid2: Second Sqid

        Returns:
            True if they share the same parent
        """
        parent1 = cls.parent(sqid1)
        parent2 = cls.parent(sqid2)
        return parent1 is not None and parent1 == parent2

    @classmethod
    def root(cls, sqid: str) -> str:
        """Get the root Sqid (top-level task).

        Args:
            sqid: Any Sqid in the hierarchy

        Returns:
            Root Sqid like "Xa.1"
        """
        parts = sqid.split(".")
        if len(parts) >= 2:
            return f"{parts[0]}.{parts[1]}"
        return sqid

    @classmethod
    def children(cls, sqid: str) -> list[str]:
        """Generate possible child Sqids (1-9 for common cases).

        Args:
            sqid: Parent Sqid

        Returns:
            List of possible child Sqids ["Xa.1.1", "Xa.1.2", ...]
        """
        return [f"{sqid}.{i}" for i in range(1, 10)]

    @classmethod
    def _decode_base62(cls, s: str) -> int:
        """Decode a base62 string to integer.

        Args:
            s: Base62 encoded string

        Returns:
            Decoded integer
        """
        result = 0
        for char in s:
            result = result * cls._BASE + cls._ALPHABET.index(char)
        return result

    @classmethod
    def _encode_base62(cls, n: int) -> str:
        """Encode an integer to base62 string.

        Args:
            n: Integer to encode

        Returns:
            Base62 encoded string
        """
        if n == 0:
            return cls._ALPHABET[0]

        result = []
        while n > 0:
            n, remainder = divmod(n, cls._BASE)
            result.append(cls._ALPHABET[remainder])
        return "".join(reversed(result))


# ============================================================================
# Convenience Functions
# ============================================================================

def parse_sqid(sqid: str) -> SqidInfo:
    """Parse a Sqid into components.

    Convenience function for SqidParser.parse().

    Args:
        sqid: Sqid string

    Returns:
        SqidInfo with parsed components
    """
    return SqidParser.parse(sqid)


def sqid_parent(sqid: str) -> str | None:
    """Get parent Sqid.

    Convenience function for SqidParser.parent().

    Args:
        sqid: Sqid string

    Returns:
        Parent Sqid or None
    """
    return SqidParser.parent(sqid)


def sqid_depth(sqid: str) -> int:
    """Get Sqid depth.

    Convenience function for SqidParser.depth().

    Args:
        sqid: Sqid string

    Returns:
        Nesting depth
    """
    return SqidParser.depth(sqid)


def sqid_root(sqid: str) -> str:
    """Get root Sqid.

    Convenience function for SqidParser.root().

    Args:
        sqid: Sqid string

    Returns:
        Root Sqid
    """
    return SqidParser.root(sqid)
