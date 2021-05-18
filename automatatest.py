import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertTrue(5 == 5)


if __name__ == '__main__':
    unittest.main()
