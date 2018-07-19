import lib.exchange.exchange as exchange

class TradeAlgorithms():
    def __init__(self):
        # exchange object
        self.bitmex = exchange.Exchange('bitmex')

        self.contracts_held = 0 # this needs to be pulled from bitmex, or calculated
        self.margin_balance = self.bitmex.get_margin_balanace()
        self.index_price = 0
        self.market_price = 0

    # This method will calculate the prices for orders
    # and returns a list of those prices
    def generate_price_list(self, price, interval, offset, n_orders):
        adjusted_price = price + offset
        result_list = []

        result_list.append(adjusted_price)

        for num in range(n_orders):
            adjusted_price += interval
            result_list.append(adjusted_price)

        return result_list

    # Calculates a delta value using the values passed
    def calculate_delta(self, pending_balance, capital_balance):
        return 1 + (pending_balance / capital_balance)

    def calculate_profit(self,first_price, offset, amount_borrowed, margin_balance):
        amount_owned = margin_balance + (amount_borrowed * offset) / first_price

        return amount_owned - amount_borrowed

    def calculate_contract_qty_max(self, price_list, available_balance, n_orders):
        return (price_list[-1] * available_balance) / n_orders

    def calculate_contract_qty_min(self, price_list, available_balance, n_orders):
        return (price_list[1] * available_balance) / n_orders

    def calculate_loss(self, order_list, offset, amount_borrowed, target_contract_qty):
        amount_owed = 0

        for price, idx in enumerate(order_list):
            if idx is 0:
                amount_owed -= amount_borrowed - (target_contract_qty / price)
            else:
                amount_owed -= target_contract_qty / price

        loss = self.calculate_profit(order_list[0], offset, amount_borrowed, margin_balance) - amount_owed

        return loss

    def binary_search_inflection(self, margin_balance, pending_balance, price_diff, last_price):
        return (pending_balance * price_diff) / last_price + margin_balance

    def calculate_future_delta(self, order_size, contract_qty, margin_balance, index_price, last_price, list_of_prices):
        first_order = list[1]
        last_order = list[-1]

        pass # need to complete

    # A simple binary search algorithm
    def binary_search(self, target_list, item):
        first_index = 0
        last_index = len(target_list) - 1
        found = False

        while first_index <= last_index and not found:
            midpoint = (first_index + last_index) // 2

            if target_list[midpoint] == item:
                found = True
            else:
                if item < target_list[midpoint]:
                    last_index = midpoint - 1
                else:
                    first_index = midpoint + 1

        return found

    # Method to generate a list of numbers between a
    # certain bounds.
    def generate_list(self, start, end):
        return [x for x in range(start, end+1)]

    # Test all deltas
    def test_deltas(self, list, pending_balance, capital_balance):
        try:
            for item in list:
                self.calculate_delta(pending_balance, capital_balance)
        except:
            raise Exception('Balance will go negative.')

    # def search_y(self, ):

    def binary_search_y_helper_btc(self, start_y, end_y, delta_n, contracts_held, margin_balance, index_price, last_price,
                                   b_offset, b_interval, n_orders):

        # Base Case, if y values right next to each other
        if (abs(start_y - end_y) == 1):
            # logger.info("Base Case Hit")
            # logger.info("Start: " + str(start_y) + " End: " + str(end_y))
            start_delta = self.calculate_delta(margin_balance, contracts_held) #get_delta_from_y_btc(start_y, contracts_held, margin_balance, index_price, last_price,
                                              # b_offset, b_interval, n_orders)
            end_delta = self.calculate_delta(margin_balance, contracts_held) #get_delta_from_y_btc(end_y, contracts_held, margin_balance, index_price, last_price, b_offset,
                                             #b_interval, n_orders)

            start_diff = abs(start_delta - delta_n)
            end_diff = abs(end_delta - delta_n)

            if (start_diff >= end_diff):
                # logger.info("end used" + str(end_y))
                return end_y

            # logger.info("start used")
            return start_y

        # Halves
        else:
            # logger.info("Else statement")
            flr_mid = (start_y + end_y) // 2

            start_delta = get_delta_from_y_btc(start_y, contracts_held, margin_balance, index_price, last_price,
                                               b_offset, b_interval, n_orders)
            mid_delta = get_delta_from_y_btc(flr_mid, contracts_held, margin_balance, index_price, last_price, b_offset,
                                             b_interval, n_orders)
            end_delta = get_delta_from_y_btc(end_y, contracts_held, margin_balance, index_price, last_price, b_offset,
                                             b_interval, n_orders)

            # logger.info(start_y, flr_mid, end_y)

            if (start_delta <= delta_n <= mid_delta) or (start_delta >= delta_n >= mid_delta):
                return binary_search_y_helper_btc(start_y, flr_mid, delta_n, contracts_held, margin_balance,
                                                  index_price, last_price, b_offset, b_interval, n_orders)
            elif (mid_delta <= delta_n <= end_delta) or (mid_delta >= delta_n >= end_delta):
                return binary_search_y_helper_btc(flr_mid, end_y, delta_n, contracts_held, margin_balance, index_price,
                                                  last_price, b_offset, b_interval, n_orders)
            else:
                logger.info("Delta_n: " + str(delta_n))
                logger.info("Start delta: " + str(start_delta))
                logger.info("Mid delta: " + str(mid_delta))
                logger.info("End delta: " + str(end_delta))
                raise Exception()
                logger.info("Delta we're aiming for will generate negative margin balance.")

    # Wrapping Binary Search Function
    # Find closest delta value and return corresponding y value
    def binary_search_y_btc(self, operation, delta_n, contracts_held, margin_balance, index_price, last_price, b_offset,
                            b_interval, n_orders):

        start_y = None
        end_y = None

        if (operation == 'buy'):  # bounds = 1 to 100000
            start_y = 1
            end_y = 100000
        elif (operation == 'sell'):  # bounds = -100000 to -1
            start_y = -100000
            end_y = -1
        else:
            ValueError("Invalid Operation")

        # ==================================================================================
        # Removes any invalid y values returning negative p_n value/margin balance
        # ==================================================================================
        inflection_y = find_inflection_y_btc(contracts_held, margin_balance, index_price, last_price, b_offset,
                                             b_interval, n_orders)  # Y-Value where p_n goes pos <-> neg

        # logger.info("Inflection_y: " + str(inflection_y))

        if inflection_y < start_y or inflection_y > end_y:  # If inflection not within range
            try:  # test a value in range to determine if all give positive p_n values or negative
                get_delta_from_y_btc(start_y, contracts_held, margin_balance, index_price, last_price, b_offset,
                                     b_interval, n_orders)  # no variable set
            except:  # All values in range are bad
                raise Exception('Balance will go negative')

        elif start_y <= inflection_y <= end_y:
            left_used = 1
            try:
                # logger.info("Inside range")
                get_delta_from_y_btc(inflection_y - 1, contracts_held, margin_balance, index_price, last_price,
                                     b_offset, b_interval, n_orders)
            except:
                print('Right will be used')
                left_used = 0  # right will automatically be used

            if (left_used):  # left side used, move back end point
                end_y = inflection_y - 1
            elif (not left_used):  # right side used, move forward start point
                start_y = inflection_y + 1
                # logger.info("start: " + str(start_y) + " end: " + str(end_y))

        # logger.info("end_y: " + str(end_y))
        # logger.info("start_y: " + str(start_y))
        return binary_search_y_helper_btc(start_y, end_y, delta_n, contracts_held, margin_balance, index_price,
                                          last_price, b_offset, b_interval, n_orders)

    # order_type = value is either 'Limit' or 'StopLimit' (for determining what the order type is)
    # base_currency = curency that is being held (numerator)
    # quote_currency = currency that is putting a price to the base currency (denominator)
    # amount_borrowed = the amount that is owed(-) or lent(+) (quote_currency)
    # evaluation_price = evaluate the starting price
    # evaluation_price_delta = (pending_balance + capital_balance) / capital_balance
    # capital_balance = how much coin is available for withdraw
    # n_orders = number of orders in the array that is being evaluated
    # price_interval = the distance between each order in the array
    def all_currency_y_search(self, pending_balance,
                                    order_type,
                                    operation,
                                    base_currency,
                                    quote_currency,
                                    amount_borrowed,
                                    capital_balance,
                                    evaluation_price,
                                    evaluation_price_delta,
                                    price_interval,
                                    n_orders,
                                    price_list):
        # sort prices lowest to highest
        price_list.sort()

        self.lowest_priced_order = price_list[0]  # first element in list (lowest price)
        self.highest_priced_order = price_list[-1]  # last element in list (highest price)

        if base_currency is 'XBTUSD' or base_currency is 'XBTU17':
            return self.binary_search(
                pending_balance,
                order_type,
                operation,
                amount_borrowed,
                base_currency,
                capital_balance,
                evaluation_price,
                evaluation_price_delta,
                price_interval,
                n_orders,
                price_list
            )
        else:
            return self.binary_search(
                pending_balance,
                order_type,
                operation,
                amount_borrowed,
                base_currency,
                capital_balance,
                evaluation_price,
                evaluation_price_delta,
                price_interval,
                n_orders,
                price_list
            )

    # def binary_search(self, pending_balance,
    #                         order_type,
    #                         operation,
    #                         amount_borrowed,
    #                         base_currency,
    #                         capital_balance,
    #                         start_price,
    #                         evaluation_price,
    #                         evaluation_price_delta,
    #                         start_price_offset,
    #                         price_interval,
    #                         n_orders,
    #                         price_list):
    #
    #     start_y = None
    #     end_y = None
    #
    #     if (operation == 'buy'):  # bounds = 1 to 100000
    #         start_y = 1
    #         end_y = 100000
    #     elif (operation == 'sell'):  # bounds = -100000 to -1
    #         start_y = -100000
    #         end_y = -1
    #     else:
    #         ValueError("Invalid Operation")

    def generate_order_qty(self, capital_balance):
        pass


if __name__ == '__main__':
    trade = TradeAlgorithms()

    x = [x for x in range(100)]

    print(trade.binary_search(x, 50))