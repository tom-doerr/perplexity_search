import unittest

def add(a, b):
    """Adds two numbers."""
    return a + b

class TestAdd(unittest.TestCase):
    def test_add_positive_numbers(self):
        self.assertEqual(add(2, 3), 5)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-2, -3), -5)

    def test_add_positive_and_negative_numbers(self):
        self.assertEqual(add(2, -3), -1)

    def test_add_zero(self):
        self.assertEqual(add(0, 5), 5)

    def test_add_large_numbers(self):
        self.assertEqual(add(1000000, 2000000), 3000000)

    def test_add_with_floats(self):
        self.assertAlmostEqual(add(2.5, 3.5), 6.0)

if __name__ == '__main__':
    unittest.main()
