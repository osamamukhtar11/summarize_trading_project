import filecmp
import unittest

from summarize_trading import *


class TestSummarizeTrading(unittest.TestCase):
    def test_short(self):
        self.assertEqual(get_trade_type(1), "SHORT")

    def test_long(self):
        self.assertEqual(get_trade_type(-1), "LONG")

    def test_summarize_trading(self):
        summarize_trading("test_opened_closed.csv")
        self.assertTrue(filecmp.cmp("output/expected_longs_output.csv", "output/longs_output.csv"), 'Output file does not match expected results')
        self.assertTrue(filecmp.cmp("output/expected_shorts_output.csv", "output/shorts_output.csv"), 'Output file does not match expected results')
        self.assertTrue(filecmp.cmp("output/expected_longs_and_shorts_output.csv", "output/longs_and_shorts_output.csv"), 'Output file does not match expected results')
        self.assertTrue(filecmp.cmp("output/expected_invalid.csv", "output/invalid.csv"), 'Invalid file does not match expected results')


if __name__ == '__main__':
    unittest.main()
