# todo database iffy
# todo pull from IBRK
# todo how to use the view?

import yahoo_fin.stock_info as si
# https://algotrading101.com/learn/yahoo-finance-api-guide/
# import pandas as pd
# import numpy as np
import datetime as dt
import psycopg2
import os
import time
from client import IBClient


class QuantAuto:
    date_back_average = 20
    dates_back_check = [30, 60, 90]  # P1
    cmd_unix = 'echo Singapore2021! | sudo -S -u postgres /Library/PostgreSQL/14/bin/pg_ctl __OP__ -D /Library/PostgreSQL/14/data -s \n'
    ps_connection = None
    cursor = None
    ticker_list = None
    ticker_type = None

    def __init__(self):
        self.get_tickers('current')

    def get_tickers(self, which):
        if which not in {'current', 'wishlist'}:
            print('Unrecognized list.')
            exit(1)
        self.ticker_type = which
        self.ticker_list = ['RFI', 'MDT', 'UNP', 'OLED', 'MCHI', 'CSCO', 'VUG', 'OKE', 'IRM', 'MAIN', 'PDI', 'PATH',
                            'UTF', 'UTG', 'GOF', 'HTGC', 'EWS', 'PCN', 'ARCC', 'ASG', 'SNAP', 'EWA', 'IBM', 'DOCU',
                            'VZ', 'JNJ', 'IVV', 'AAPL', 'MSFT', 'FB']

    def get_tickers_ibrk(self, which = 'current'):
        # Create a new session of the IB Web API.
        # start /Users/razvanjulianpetrescu/Downloads/clientportal.gw/bin/run.sh root/conf.yam
        # authenticate using https://localhost:5000/
        # then run this
        print("Starting the gateway")
        exe_cmd = "cd /Users/razvanjulianpetrescu/Downloads/clientportal.gw; ./bin/run.sh root/conf.yam &"
        os.system(exe_cmd) # todo subprocess? this hangs
        time.sleep(5)
        print("Launching OAuth")
        exe_cmd = "open https://localhost:5000/"
        os.system(exe_cmd)
        time.sleep(30)
        
        ib_client = IBClient(
            username="zzkj98765",
            account="U3900095",
            is_server_running=True
        )

        # create a new session
        ib_client.create_session()

        # grab the account data.
        account_data = ib_client.portfolio_accounts()
        print(account_data)

        # grab account portfolios
        account_positions = ib_client.portfolio_account_positions(
            account_id="U3900095",
            page_id=0
        )
        print(account_positions)

    def db_op(self, op):
        if op not in {'start', 'stop'}:
            print('Db command error')
            exit(1)

        if op == 'stop':
            self.db_close()

        exe_cmd = self.cmd_unix.replace("__OP__", op)
        print(f"Executing database {op}...")
        os.system(exe_cmd)
        time.sleep(2)
        print("Exiting step.")

    def db_con(self):
        # database
        try:
            self.ps_connection = psycopg2.connect(user="postgres",
                                                  password="Singapore2021",
                                                  host="127.0.0.1",
                                                  port="5432",
                                                  database="HFT")
            self.ps_connection.autocommit = True
            self.cursor = self.ps_connection.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error connecting to database. Exiting.")
            exit(1)

    def db_close(self):
        try:
            self.ps_connection.close()
        except(Exception, psycopg2.DatabaseError) as error:
            print("Error disconnecting from database. Exiting.")
            exit(1)

    def execute_get(self):
        # get date window for averages P2
        date_from = dt.date.today() - dt.timedelta(self.date_back_average)
        d1 = date_from.strftime("%d/%m/%Y")
        date_to = dt.date.today() - dt.timedelta(1)
        d2 = date_to.strftime("%d/%m/%Y")
        print(f"Running for date range {d1} to {d2}")
        sz = len(self.ticker_list)
        print(f"{self.ticker_type} has {sz} items")

        self.db_con()
        print("Connected")

        historical_datas = {}
        signal_s = ""

        for ticker in self.ticker_list:
            try:
                historical_datas[ticker] = si.get_data(ticker, start_date=d1)  # smth wrong, end_date = d1)
                my_data = historical_datas[ticker][['open', 'close']]
                # my_data.index pandas.core.indexes.datetimes.DatetimeIndex'
                # print(my_data) # it is a dictionary of data frames
                # print(f"{ticker} data")
                # print(my_data.describe())
                signal_n = my_data.mean(axis=0)  # this is a series
                current = si.get_live_price(ticker)
                print(f"{ticker}: Signal {signal_n[1]}  vs current price {current}")

                if current > signal_n[1]:
                    signal_s = "BUY"
                else:
                    signal_s = "SELL"

                self.cursor.execute("CALL public.insert_collection(%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                                    (1,  # instrument ref this is a tuple btw
                                     date_from.strftime("%m/%d/%Y"),  # date signal from
                                     dt.date.today().strftime("%m/%d/%Y"),  # date updated
                                     dt.datetime.now().strftime("%H:%M:%S"),  # time updated
                                     ticker,
                                     signal_s,
                                     signal_n[0],  # open
                                     signal_n[1],  # close
                                     current))  # signal num

            except Exception as error:
                print("Error: ", error)
                continue

    def execute_check(self):
        for date_back in self.dates_back_check:
            date_check = dt.date.today() - dt.timedelta(date_back)
            print(date_check)

            for ticker in self.ticker_list:
                self.cursor.execute("call public.determine_performance(%s, %s, %s); fetch all in cur;",
                                    (ticker, date_check.strftime("%m/%d/%Y"), ''))
                result = self.cursor.fetchall()

                if not result:
                    print(f"\tNo previous data for {ticker} on {date_check}")
                else:
                    for row in result:
                        print(f"\t{ticker} Value then: {row[0]} signal: {row[1]}")
                        print(f"\tValue now: {si.get_live_price(ticker)}")


# additionals:
# fb_earnings_hist = si.get_earnings_history("fb")
# fb_earnings = si.get_earnings("fb")
# print(fb_earnings)

# print(historical_datas)  # it is a dictionary of data frames


qa = QuantAuto()
# qa.db_op("start")
# qa.execute_get()
# qa.execute_check()
# qa.db_op("stop")
qa.get_tickers_ibrk()
