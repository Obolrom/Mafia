import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertTrue(5 == 5)

    def test_something2(self):
        self.assertTrue(6 == 6)

    def testStrings(self):
        self.assertFalse("good" == "bad")


if __name__ == '__main__':
    unittest.main()
