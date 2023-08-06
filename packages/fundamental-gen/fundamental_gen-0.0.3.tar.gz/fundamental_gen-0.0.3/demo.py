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
# from yahoofinancials import YahooFinancials as YF

if __name__ == '__main__':
    ticker = 'AAPL'
    yahoo_financials = YF(ticker)
    ps = yahoo_financials.get_summary_data()
    a = 1
