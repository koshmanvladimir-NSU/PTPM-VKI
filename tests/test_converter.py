import unittest

from src.converter import Converter


class TestConverter(unittest.TestCase):

    # x >= 100.7 -> 1000
    def test_upper_boundary_included(self):
        self.assertEqual(Converter.do(100.7), 1000)

    def test_above_upper_boundary(self):
        self.assertEqual(Converter.do(100.8), 1000)

    def test_large_positive(self):
        self.assertEqual(Converter.do(99999.9), 1000)

    # (0; 100.7) -> int(x)
    def test_just_below_upper_boundary(self):
        self.assertEqual(Converter.do(100.6), 100)

    def test_positive_middle(self):
        self.assertEqual(Converter.do(65.7), 65)

    def test_positive_integer_value(self):
        self.assertEqual(Converter.do(50.0), 50)

    def test_just_above_zero(self):
        self.assertEqual(Converter.do(0.1), 0)

    def test_one_point_zero(self):
        self.assertEqual(Converter.do(1.0), 1)

    # x == 0 -> ValueError
    def test_zero_raises(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    def test_negative_zero_raises(self):
        with self.assertRaises(ValueError):
            Converter.do(-0.0)

    # [-30.4; 0) -> int(x) - 5
    def test_just_below_zero(self):
        self.assertEqual(Converter.do(-0.1), -5)

    def test_minus_one(self):
        self.assertEqual(Converter.do(-1.0), -6)

    def test_negative_middle(self):
        self.assertEqual(Converter.do(-15.7), -20)

    def test_lower_boundary_included(self):
        self.assertEqual(Converter.do(-30.4), -35)

    def test_minus_thirty(self):
        self.assertEqual(Converter.do(-30.0), -35)

    # x <= -30.5 -> -2000
    def test_below_boundary(self):
        self.assertEqual(Converter.do(-30.5), -2000)

    def test_below_boundary_further(self):
        self.assertEqual(Converter.do(-30.6), -2000)

    def test_large_negative(self):
        self.assertEqual(Converter.do(-94.5), -2000)

    def test_return_type_is_int(self):
        for value in (150.0, 65.7, -0.1, -50.0):
            self.assertIsInstance(Converter.do(value), int)


if __name__ == "__main__":
    unittest.main()