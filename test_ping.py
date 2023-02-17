import unittest
import ping

class TestLinkChecker(unittest.TestCase):

    def test_get_internal_links(self):
        result = get_internal_links(["http://localhost:8000"],[],{},"localhost")
        self.assertEqual(result, 15)
        self.assertEqual(get_internal_links(["http://localhost:8000"],[],{},"localhost"), 15)

if __name__ = '__main__':
    unittest.main()
