#!/usr/bin/python

"""
%(scriptname)s [-h|--help] [api [api [...]]] [ticker [ticker [...]]]
    no args: show some information about default tickers (%(defaultargs)s)
    ticker(s): show some information about specified ticker(s)
    api name(s) and ticker(s): show the specified api(s) result for the ticker(s)
    yf and -h: show apis
    api name(s) and -h: show help for that api
    -h or --help: show usage
"""

from __future__ import print_function
from fundamental_gen import YahooFinancials as YF

if __name__ == '__main__':
    ticker = 'AAPL'
    yahoo_financials = YF(ticker)

    balance_sheet_data_qt = yahoo_financials.get_financial_stmts('quarterly', 'balance')
    print(balance_sheet_data_qt)

    income_statement_data_qt = yahoo_financials.get_financial_stmts('quarterly', 'income')
    print(income_statement_data_qt)

    all_statement_data_qt =  yahoo_financials.get_financial_stmts('quarterly', ['income', 'cash', 'balance'])
    print(all_statement_data_qt)

    apple_earnings_data = yahoo_financials.get_stock_earnings_data()
    print(apple_earnings_data)

    apple_net_income = yahoo_financials.get_net_income()
    print(apple_net_income)
