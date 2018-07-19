#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 12:27:09 2017

@author: Crypto Quant Solutions
"""
import logging
# import lib.exchange.bitmex.bitmex as bitmex
#
# exchange_mgr = bitmex.BitMEX()
logger = logging.getLogger(__name__)

symbol = "XBTUSD"
#
# contracts_held = exchange_mgr.get_position_contractQty(symbol) # number of contracts held
# margin_balance = exchange_mgr.get_margin_balance()/100000000 # bitcoins owned in margin balance
# index_price = exchange_mgr.get_indexPrice(symbol) # price of bitcoin index .BXBT
# last_price = exchange_mgr.get_lastPrice(symbol) # last price

def interval_price_list(start_price, interval, n_orders): #default iterations/len is 20
    price_list = []
    current_price = start_price
    for interval_price in range(n_orders):
        price_list.append(current_price)
        current_price = current_price + interval
    return price_list

# ======================
# FUNCTIONS FOR BITCOIN
# ======================

def sum_last_price_btc(list_b): #sum for all items in list_b except last item
    
    running_sum = 0
    for b_item in list_b[0:-1]: #all items except last item in list, b_item is ith item in b up to i-1
        running_sum += ((list_b[-1] - b_item) / (list_b[-1]))
        # 0 + (8600 - 8200) / 8600
        # 21.5 + (8600 - 8400) / 8600
    return running_sum

def get_delta_from_y_btc(y_value, contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders):
    
    b1 = last_price + b_offset          # Give me after adjusting for the offset(first order in the array)
    price_list_b = interval_price_list(b1, b_interval, n_orders)       # Creates price list based on first price and intervals for orders to be placed
    a_n = index_price + b_offset + (n_orders * b_interval)       # Calculate the last price in the price array( I.E. price_list_b[-1])
    
    term1 = ((contracts_held * (last_price - price_list_b[-1])) / price_list_b[-1]) # Converting current position to bitcoin price format
    term2 = -y_value * sum_last_price_btc(price_list_b) # ?
    term3 =  margin_balance * (index_price - a_n) # price index - last price in list multiplied by margin balance
    loss = term1 +  term2 + term3
    #logger.info('loss: ' + str(loss))
    #logger.info('a_n: ' + str (a_n))
    p_n = margin_balance - (loss/a_n)

    delta_n = ((margin_balance * index_price) + (n_orders * y_value) + contracts_held - loss) / ((a_n * margin_balance) - loss) # delta at end of orders in b_list array
    
    #logger.info("\ny: " + str(y_value))
    #logger.info('delta: ' + str(delta_n))
    #logger.info('loss: ' + str(loss))
    #logger.info('a_n: ' + str (a_n))
    #logger.info(str(term1) + " : " + str(term2) + " : " + str(term3))
    #logger.info("p_n: " + str(p_n))
    
    if p_n <= 0:
        raise Exception("Value of p_n is negative.")
    else:
        return delta_n


# # This area is to hack together the delta function
# def get_delta_from_y_btc(last):
#
#
#
#
def find_inflection_y_btc(contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders):
    b1 = last_price + b_offset # Determines the first price (last price + offset)
    price_list_b = interval_price_list(b1, b_interval, n_orders) # Generated price list
    a_n = index_price + b_offset + (n_orders * b_interval) # calculates last element in the array - > price_list_b[-1]

    term1 = ((contracts_held * (last_price - price_list_b[-1])) / price_list_b[-1]) # Converting current position to bitcoin price format
    term2 = -(a_n * margin_balance) # last price in list multiplied by the margin balance all multiplied by -1 for negative value
    term3 = (margin_balance * (index_price - a_n)) # last price multiplied by (index price minus last price in list)

    numerator = term1 + term2 + term3
    denominator = sum_last_price_btc(price_list_b)
    
    try:
        inflection = numerator / denominator
        return inflection
    except:
        raise Exception("Inflection is undefined/invalid - possibly divided by zero.")
        
        
def binary_search_y_helper_btc(start_y, end_y, delta_n, contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders):

    # Base Case, if y values right next to each other
    if (abs(start_y - end_y) == 1):
        #logger.info("Base Case Hit")
        #logger.info("Start: " + str(start_y) + " End: " + str(end_y))
        start_delta = get_delta_from_y_btc(start_y, contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders)
        end_delta = get_delta_from_y_btc(end_y, contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders)

        start_diff = abs(start_delta - delta_n)
        end_diff = abs(end_delta - delta_n)
        
        if (start_diff >= end_diff):
            #logger.info("end used" + str(end_y))
            return end_y
        
        #logger.info("start used")
        return start_y
    
    # Halves 
    else:
        #logger.info("Else statement")
        flr_mid = (start_y + end_y) // 2
        
        start_delta = get_delta_from_y_btc(start_y, contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders)
        mid_delta = get_delta_from_y_btc(flr_mid, contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders)
        end_delta = get_delta_from_y_btc(end_y, contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders)

        #logger.info(start_y, flr_mid, end_y)

        if (start_delta <= delta_n <= mid_delta) or (start_delta >= delta_n >= mid_delta):
            return binary_search_y_helper_btc(start_y, flr_mid, delta_n, contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders)
        elif (mid_delta <= delta_n <= end_delta) or (mid_delta >= delta_n >= end_delta):
            return binary_search_y_helper_btc(flr_mid, end_y, delta_n, contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders)
        else:
            logger.info("Delta_n: " + str(delta_n))
            logger.info("Start delta: " + str(start_delta))
            logger.info("Mid delta: " + str(mid_delta))
            logger.info("End delta: " + str(end_delta))
            raise Exception()
            logger.info("Delta we're aiming for will generate negative margin balance.")

# Wrapping Binary Search Function
# Find closest delta value and return corresponding y value
def binary_search_y_btc(operation, delta_n, contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders):    
    
    start_y = None
    end_y = None
    
    if (operation == 'buy'): # bounds = 1 to 100000 
        start_y = 1
        end_y = 100000
    elif (operation == 'sell'): # bounds = -100000 to -1
        start_y = -100000
        end_y = -1
    else:
        ValueError("Invalid Operation")

    # ==================================================================================
    # Removes any invalid y values returning negative p_n value/margin balance
    # ==================================================================================
    inflection_y = find_inflection_y_btc(contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders) # Y-Value where p_n goes pos <-> neg
    
    #logger.info("Inflection_y: " + str(inflection_y))
    
    if inflection_y < start_y or inflection_y > end_y: # If inflection not within range
        try: # test a value in range to determine if all give positive p_n values or negative
            get_delta_from_y_btc(start_y, contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders) #no variable set
        except: # All values in range are bad
            raise Exception('Balance will go negative')
 
    elif start_y <= inflection_y <= end_y:
        left_used = 1
        try:
            #logger.info("Inside range")
            get_delta_from_y_btc(inflection_y - 1, contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders)
        except:
            print('Right will be used')
            left_used = 0 #right will automatically be used
            
        if (left_used): # left side used, move back end point
            end_y = inflection_y - 1
        elif (not left_used): #right side used, move forward start point
            start_y = inflection_y + 1  
        #logger.info("start: " + str(start_y) + " end: " + str(end_y))
        
    #logger.info("end_y: " + str(end_y))
    #logger.info("start_y: " + str(start_y))    
    return binary_search_y_helper_btc(start_y, end_y, delta_n, contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders)

    
# ===============================
# FUNCTIONS FOR OTHER CURRENCIES
# ===============================
    
def sum_last_price(list_b):
    
    running_sum = 0
    for b_item in list_b[0:-1]: #all items except last item in list, b_item is ith item in b up to i-1
        running_sum += (b_item - list_b[-1])
    return running_sum
    

def get_delta_from_y(y_value, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders = 20):
    
    b1 = last_price + b_offset
    price_list_b = interval_price_list(b1, b_interval, n_orders)
    
    term1 = contracts_held * (last_price - price_list_b[-1])
    term2 = y_value * sum_last_price(price_list_b)
    loss =  term1 + term2
    
    p_n = margin_balance - loss
    delta_n = (price_list_b[-1] * ((y_value * n_orders) + contracts_held)) / p_n
    
    #logger.info("\ny: " + str(y_value))
    #logger.info('delta: ' + str(delta_n))
    #logger.info('loss: ' + str(loss))
    #logger.info(str(term1) + " : " + str(term2))
    #logger.info("p_n: " + str(p_n))
    
    
    if (p_n <= 0): #negative account balance
        raise Exception("Value of p_n is negative.")
    else:
        return delta_n    

def find_inflection_y(contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders):
    
    b1 = last_price + b_offset
    price_list_b = interval_price_list(b1, b_interval, n_orders) 
    
    term1 = -contracts_held * (last_price - price_list_b[-1])
    term2 = margin_balance
    numerator = term1 + term2
    denominator = sum_last_price(price_list_b)
    
    try:
        inflection = numerator / denominator
        return inflection
    except:
        raise Exception("Inflection is undefined/invalid - possibly divided by zero.")
    
def binary_search_y_helper(start_y, end_y, delta_n, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders):

    # Base Case, if y values right next to each other
    if (abs(start_y - end_y) == 1):
        #logger.info("Base Case Hit")
        #logger.info("Start: " + str(start_y) + " End: " + str(end_y))
        start_delta = get_delta_from_y(start_y, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders)
        end_delta = get_delta_from_y(end_y, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders)

        start_diff = abs(start_delta - delta_n)
        end_diff = abs(end_delta - delta_n)
        
        if (start_diff >= end_diff):
            #logger.info("end used" + str(end_y))
            return end_y
        
        #logger.info("start used")
        return start_y
    
    # Halves 
    else:
        #logger.info("Else statement")
        flr_mid = (start_y + end_y) // 2
        
        start_delta = get_delta_from_y(start_y, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders)
        mid_delta = get_delta_from_y(flr_mid, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders)
        end_delta = get_delta_from_y(end_y, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders)
        #logger.info(start_y, flr_mid, end_y)
        #logger.info(start_delta, mid_delta, end_delta, delta_n)
        if (start_delta <= delta_n <= mid_delta) or (start_delta >= delta_n >= mid_delta):
            return binary_search_y_helper(start_y, flr_mid, delta_n, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders)
        elif (mid_delta <= delta_n <= end_delta) or (mid_delta >= delta_n >= end_delta):
            return binary_search_y_helper(flr_mid, end_y, delta_n, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders)
        else:
            logger.info("Delta_n: ", str(delta_n))
            logger.info("Start delta: " + str(start_delta))
            logger.info("End delta: " + str(end_delta))
            logger.info("Current delta not within start/end delta")
            raise Exception()
            logger.info("Delta we're aiming for will generate negative margin balance.")

# Wrapping Binary Search Function
# Find closest delta value and return corresponding y value
def binary_search_y(operation, delta_n, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders):    
    
    start_y = None
    end_y = None
    
    if (operation == 'buy'): # bounds = 1 to 100000 
        start_y = 1
        end_y = 100000
    elif (operation == 'sell'): # bounds = -100000 to -1
        start_y = -100000
        end_y = -1
    else:
        ValueError("Invalid Operation")

    # ==================================================================================
    # Removes any invalid y values returning negative p_n value/margin balance
    # ==================================================================================
    inflection_y = find_inflection_y(contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders) # Y-Value where p_n goes pos <-> neg
    
    if inflection_y < start_y or inflection_y > end_y: # If inflection not within range
        try: # test a value in range to determine if all give positive p_n values or negative
            get_delta_from_y(start_y, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders) #no variable set
        except: # All values in range are bad
            raise Exception('Balance will go negative')
 
    elif start_y <= inflection_y <= end_y:
        left_used = 1
        try:
            #logger.info("Inside range")
            get_delta_from_y(inflection_y - 1, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders)
        except:
            left_used = 0 #right will automatically be used
            
        if (left_used): # left side used, move back end point
            end_y = inflection_y - 1
        elif (not left_used): #right side used, move forward start point
            start_y = inflection_y + 1  
    logger.info("start: " + str(start_y) + " end: " + str(end_y))
        
    return binary_search_y_helper(start_y, end_y, delta_n, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders)

# NOTE: index_price argument moved to end of argument list 
def all_currency_y_search(operation, symbol, delta_n, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders, index_price = None):
    if symbol == "XBTUSD" or symbol == "XBTU17":
        qty = binary_search_y_btc(operation, delta_n, contracts_held, margin_balance, index_price, last_price, b_offset, b_interval, n_orders)

        # if operation is 'sell' and qty < 0:
        #     qty *= -1

        return qty
    else: # General BTC currency case
        qty = binary_search_y(operation, delta_n, contracts_held, margin_balance, last_price, b_offset, b_interval, n_orders)

        # if operation is 'sell' and qty < 0:
        #     qty *= -1

        return qty



