import unittest2

import lib.utils.trade_algorithms as trade

class TradeAlgorithmsTest(unittest2.TestCase):
    def setUp(self):
        self.test = trade.TradeAlgorithms()

    def test_generate_price_list(self):
        result = self.test.generate_price_list(400, 200, 50, 6)

        print(result)

        assert (result != None)

    def test_calculate_delta(self):
        result = self.test.calculate_delta(5 * 8000, 1 * 8000)

        print(result)

        assert (result != None)

    def test_binary_search(self):
        list = [x for x in range(50)]

        result = self.test.binary_search(list, 23)

        print(result)

        assert (result)

    def test_generate_list(self):
        list = self.test.generate_list(1, 100)

        print(list)
