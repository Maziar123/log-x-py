"""Pattern extraction and grok-like parsing for Eliot logs."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from re import Pattern
from typing import Any


@dataclass
class PatternMatch:
    """Result of a pattern match."""

    field: str
    pattern_name: str
    value: Any
    matched_text: str


# Common grok-like patterns
COMMON_PATTERNS: dict[str, str] = {
    "WORD": r"\b\w+\b",
    "NUMBER": r"-?\d+(?:\.\d+)?",
    "INT": r"-?\d+",
    "FLOAT": r"-?\d+\.\d+",
    "IP": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
    "IPV6": r"[0-9a-fA-F:]+",
    "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "URL": r"https?://[^\s]+",
    "UUID": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
    "PATH": r"(?:/[^/\s]+)+",
    "HOSTNAME": r"[a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+",
    "TIMESTAMP": r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?",
    "DATE": r"\d{4}-\d{2}-\d{2}",
    "TIME": r"\d{2}:\d{2}:\d{2}",
    "HEX": r"0[xX][0-9a-fA-F]+",
    "MD5": r"[a-fA-F0-9]{32}",
    "SHA1": r"[a-fA-F0-9]{40}",
    "SHA256": r"[a-fA-F0-9]{64}",
    "JSON": r"\{[^{}]*\}",
    "QUERY_STRING": r"\?[^\s]*",
    "HTTP_METHOD": r"GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|TRACE",
    "HTTP_STATUS": r"\d{3}",
    "USER_AGENT": r"Mozilla/[\d.]+ \([^)]+\).*",
}


def compile_pattern(pattern: str) -> Pattern[str]:
    """
    Compile a grok-like pattern with named groups.
    
    Args:
        pattern: Pattern string with %{PATTERN:name} syntax
        
    Returns:
        Compiled regex pattern
        
    Example:
        >>> pattern = compile_pattern("%{IP:client} - %{WORD:method}")
    """
    # Replace %{PATTERN:name} with named groups
    result = pattern

    # Find all %{PATTERN:name} occurrences
    for match in re.finditer(r"%\{(\w+):(\w+)(?::(\w+))?\}", pattern):
        full_match = match.group(0)
        pattern_name = match.group(1)
        field_name = match.group(2)

        # Get regex for pattern
        if pattern_name in COMMON_PATTERNS:
            regex = COMMON_PATTERNS[pattern_name]
        else:
            # Assume it's a literal regex
            regex = pattern_name

        # Replace with named group
        replacement = f"(?P<{field_name}>{regex})"
        result = result.replace(full_match, replacement, 1)

    return re.compile(result)


class PatternExtractor:
    """Extract patterns from log fields."""

    def __init__(self):
        self.patterns: dict[str, Pattern[str]] = {}
        self.custom_patterns: dict[str, str] = {}

    def add_pattern(self, name: str, regex: str) -> None:
        """
        Add a custom pattern.
        
        Args:
            name: Pattern name
            regex: Regular expression
        """
        self.custom_patterns[name] = regex
        COMMON_PATTERNS[name] = regex

    def extract(
        self,
        text: str,
        pattern: str | Pattern[str],
    ) -> dict[str, Any] | None:
        """
        Extract fields from text using pattern.
        
        Args:
            text: Text to parse
            pattern: Pattern string or compiled regex
            
        Returns:
            Dictionary of extracted fields or None
            
        Example:
            >>> extractor = PatternExtractor()
            >>> extractor.extract("192.168.1.1 GET", "%{IP:client} %{WORD:method}")
            {'client': '192.168.1.1', 'method': 'GET'}
        """
        if isinstance(pattern, str):
            if pattern not in self.patterns:
                self.patterns[pattern] = compile_pattern(pattern)
            compiled = self.patterns[pattern]
        else:
            compiled = pattern

        match = compiled.search(text)
        if match:
            return match.groupdict()
        return None

    def extract_from_task(
        self,
        task: dict[str, Any],
        field: str,
        pattern: str,
    ) -> dict[str, Any] | None:
        """
        Extract pattern from a specific task field.
        
        Args:
            task: Task dictionary
            field: Field name to extract from
            pattern: Extraction pattern
            
        Returns:
            Dictionary of extracted fields or None
        """
        value = task.get(field)
        if not isinstance(value, str):
            return None

        return self.extract(value, pattern)


def extract_urls(text: str) -> list[str]:
    """Extract all URLs from text."""
    pattern = re.compile(COMMON_PATTERNS["URL"])
    return pattern.findall(text)


def extract_ips(text: str) -> list[str]:
    """Extract all IP addresses from text."""
    pattern = re.compile(COMMON_PATTERNS["IP"])
    return pattern.findall(text)


def extract_emails(text: str) -> list[str]:
    """Extract all email addresses from text."""
    pattern = re.compile(COMMON_PATTERNS["EMAIL"])
    return pattern.findall(text)


def extract_uuids(text: str) -> list[str]:
    """Extract all UUIDs from text."""
    pattern = re.compile(COMMON_PATTERNS["UUID"])
    return pattern.findall(text)


def create_extraction_pipeline(
    *extractors: Callable[[dict], dict],
) -> Callable[[dict], dict]:
    """
    Create a pipeline of extractors.
    
    Args:
        *extractors: Extraction functions
        
    Returns:
        Combined extraction function
        
    Example:
        >>> pipeline = create_extraction_pipeline(
        ...     lambda t: {"urls": extract_urls(t.get("message", ""))},
        ...     lambda t: {"ips": extract_ips(t.get("message", ""))},
        ... )
    """
    def pipeline(task: dict) -> dict:
        result = dict(task)
        for extractor in extractors:
            extracted = extractor(result)
            if extracted:
                result.update(extracted)
        return result

    return pipeline


class LogClassifier:
    """Classify logs based on patterns."""

    def __init__(self):
        self.categories: dict[str, Pattern[str]] = {}

    def add_category(self, name: str, pattern: str) -> None:
        """
        Add a category with matching pattern.
        
        Args:
            name: Category name
            pattern: Regex pattern to match
        """
        self.categories[name] = re.compile(pattern)

    def classify(self, text: str) -> list[str]:
        """
        Classify text into categories.
        
        Args:
            text: Text to classify
            
        Returns:
            List of matching category names
        """
        matches = []
        for name, pattern in self.categories.items():
            if pattern.search(text):
                matches.append(name)
        return matches

    def classify_task(self, task: dict[str, Any]) -> list[str]:
        """
        Classify a task based on its action_type and message.
        
        Args:
            task: Task dictionary
            
        Returns:
            List of matching category names
        """
        text = " ".join(str(v) for v in task.values() if isinstance(v, str))
        return self.classify(text)


def create_common_classifier() -> LogClassifier:
    """Create a classifier with common log categories."""
    classifier = LogClassifier()

    # HTTP-related
    classifier.add_category("http_request", r"http.*request|GET|POST|PUT|DELETE")
    classifier.add_category("http_error", r"http.*error|5\d{2}|4\d{2}")

    # Database
    classifier.add_category("database", r"database|db|query|sql|select|insert|update|delete")
    classifier.add_category("db_slow", r"slow.*query|query.*slow|timeout")

    # Authentication
    classifier.add_category("auth", r"auth|login|logout|session|token|password")
    classifier.add_category("auth_failure", r"auth.*fail|login.*fail|unauthorized|forbidden")

    # System
    classifier.add_category("system", r"system|process|thread|memory|cpu")
    classifier.add_category("error", r"error|exception|traceback|fail")
    classifier.add_category("warning", r"warn|warning|deprecated")

    # Network
    classifier.add_category("network", r"network|connection|socket|tcp|udp")
    classifier.add_category("network_error", r"connection.*refused|timeout|unreachable")

    return classifier


__all__ = [
    "COMMON_PATTERNS",
    "LogClassifier",
    "PatternExtractor",
    "PatternMatch",
    "compile_pattern",
    "create_common_classifier",
    "create_extraction_pipeline",
    "extract_emails",
    "extract_ips",
    "extract_urls",
    "extract_uuids",
]
