"""Tests for logxpy/src/category.py -- Category management."""
from __future__ import annotations
from logxpy.src.category import (
    category_context, get_current_category,
    CategorizedLogger, CategoryManager, Category,
    get_category,
)

class TestCategoryContext:
    def test_yields_category(self):
        """category_context yields the category name."""
        with category_context("test") as cat:
            assert cat == "test"

    def test_restores_on_exit(self):
        with category_context("test"):
            pass
        # After exit, should be restored to previous

    def test_nested_yields(self):
        """Nested category_context yields correct names."""
        with category_context("outer") as outer:
            assert outer == "outer"
            with category_context("inner") as inner:
                assert inner == "inner"

    def test_set_category_returns_categorized_logger(self):
        """Module-level set_category returns CategorizedLogger (via CategoryManager)."""
        from logxpy.src.category import set_category
        result = set_category("test")
        assert isinstance(result, CategorizedLogger)
        assert get_category() == "test"

class TestCategorizedLogger:
    def test_info_returns_self(self, captured_messages):
        cl = CategorizedLogger("test")
        result = cl.info("hello")
        assert result is cl

    def test_includes_category(self, captured_messages):
        cl = CategorizedLogger("db")
        cl.info("query")
        assert any(m.get("_category") == "db" for m in captured_messages)

    def test_child_subcategory(self):
        cl = CategorizedLogger("db")
        child = cl.child("query")
        assert child.category == "db:query"

    def test_call_delegates_to_info(self, captured_messages):
        cl = CategorizedLogger("test")
        result = cl("hello")
        assert result is cl
        assert len(captured_messages) >= 1

    def test_level_methods_return_self(self, captured_messages):
        cl = CategorizedLogger("test")
        assert cl.debug("d") is cl
        assert cl.success("s") is cl
        assert cl.warning("w") is cl
        assert cl.error("e") is cl
        assert cl.critical("c") is cl

    def test_color_methods_return_self(self):
        cl = CategorizedLogger("test")
        assert cl.set_color("red") is cl
        assert cl.set_back_color("yellow") is cl
        assert cl.set_fore_color("blue") is cl
        assert cl.set_font_color("green") is cl

class TestCategoryManager:
    def test_call_creates_logger(self):
        cm = CategoryManager()
        result = cm("test")
        assert isinstance(result, CategorizedLogger)

    def test_current_property(self):
        cm = CategoryManager()
        cm("test")
        assert cm.current == "test"

    def test_default_without_set(self):
        cm = CategoryManager()
        result = cm()
        assert isinstance(result, CategorizedLogger)
