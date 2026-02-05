"""Tests for eliot._fmt."""
from unittest import TestCase
from logxpy._fmt import format_value, DFFormatter, TensorFormatter

class MockDF:
    shape = (10, 2)
    columns = ["a", "b"]
    dtypes = {"a": "int", "b": "float"}
    def head(self, n): return self
    def to_dict(self, orient): return [{"a": 1, "b": 1.1}]

class MockTensor:
    shape = (2, 2)
    dtype = "float32"
    device = "cpu"
    def min(self): return 0.0
    def max(self): return 1.0
    def mean(self): return 0.5

class FormatTests(TestCase):
    def test_truncate(self):
        """Values are truncated."""
        long_str = "x" * 1000
        res = format_value(long_str, max_len=10)
        self.assertEqual(len(res), 13) # 10 + "..."
        
    def test_df_formatter(self):
        """DataFrames are formatted."""
        # Mocking get_module is hard without dependency injection, 
        # so we'll test the formatter directly assuming support check passed
        fmt = DFFormatter()
        res = fmt.format(MockDF())
        self.assertEqual(res["_type"], "DataFrame")
        self.assertEqual(res["shape"], [10, 2])

    def test_tensor_formatter(self):
        """Tensors are formatted."""
        fmt = TensorFormatter()
        self.assertTrue(fmt.supports(MockTensor()))
        res = fmt.format(MockTensor())
        self.assertEqual(res["_type"], "MockTensor")
        self.assertEqual(res["dtype"], "float32")
