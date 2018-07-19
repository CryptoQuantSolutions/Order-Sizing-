import unittest
import lib.utils.automation_equations as automation_equations

class AutomationEquationsTest(unittest.TestCase):

    def test_binary_search_sell(self):
        btc_amount = 1
        # ans = automation_equations.binary_search_y_btc('sell', -2, 4000, (1*10^8), 4100, 4000, 100, 200, 4)
        #                               operation, symbol, delta_n, contract qty, margin balance (btc_balance * 10^8), last price, offset, interval, price of btc index
        ans = automation_equations.all_currency_y_search('sell', 'XBTUSD', -3, 4000, (btc_amount), 4100, 100, 200, 4, 4000)

        print('Result: ')
        print(ans)

    # def test_buy_bin_search(self):
    #     # ans = automation_equations.binary_search_y_btc('sell', -2, 4000, (1*10^8), 4100, 4000, 100, 200, 4)
    #     #                               operation, symbol, delta_n, contract qty, margin balance (btc_balance * 10^8), last price, offset, interval, price of btc index
    #     ans = automation_equations.all_currency_y_search('buy', 'XBTUSD', 3, 4000, (1*10^8), 4100, 100, 200, 4, 4000)
    #
    #     print('Result: ')
    #     print(ans)

