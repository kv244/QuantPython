import yahoo_fin.stock_info as si
# https://algotrading101.com/learn/yahoo-finance-api-guide/
# import pandas as pd
# import numpy as np
import datetime as dt
import psycopg2

date_back_average = 20
dates_back_check = [30, 60, 90] # P1

# get date window for averages P2
date_from = dt.date.today() - dt.timedelta(date_back_average)
d1 = date_from.strftime("%d/%m/%Y")
date_to = dt.date.today() - dt.timedelta(1)
d2 = date_to.strftime("%d/%m/%Y")
print(f"Running for date range {d1} to {d2}")

# instruments
ticker_list = ["MSFT", "GOF", "PKO", "PCN", "UTG", "UTF", "CSCO", "VZ", "OKE", "FB", "PATH", "OLED",
               "MAIN", "ARCC", "HTGC", "RFI", "IVV", "VUG", "AGG", "NVDA"]
# TODO pull from IBRK

# database
try:
    ps_connection = psycopg2.connect(user="postgres",
                                     password="Singapore2021",
                                     host="127.0.0.1",
                                     port="5432",
                                     database="HFT")
    ps_connection.autocommit = True
    cursor = ps_connection.cursor()
    cursor.execute("TRUNCATE TABLE public.\"Collection\";")
    # TODO handle duplicate insert graciously no stop

    historical_datas = {}
    signal_s = ""
    for ticker in ticker_list:
        historical_datas[ticker] = si.get_data(ticker, start_date=d1)  # smth wrong, end_date = d1)
        # print(historical_datas[ticker])
        my_data = historical_datas[ticker][['open', 'close']]
        # my_data.index pandas.core.indexes.datetimes.DatetimeIndex'
        print(my_data) # it is a dictionary of data frames
        # print(f"{ticker} data")
        # print(my_data.describe())
        signal_n = my_data.mean(axis=0)  # this is a series
        current = si.get_live_price(ticker)
        print(f"{ticker}: Signal {signal_n}  vs current price {current}")
        # print(signal[1]) # close

        if current > signal_n[1]:
            signal_s = "BUY"
        else:
            signal_s = "SELL"

        cursor.execute("CALL public.insert_collection(%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                   (1, # instrument ref this is a tuple btw
                    date_from.strftime("%m/%d/%Y"), # date signal from
                    dt.date.today().strftime("%m/%d/%Y"), # date updated
                    dt.datetime.now().strftime("%H:%M:%S"), # time updated
                    ticker,
                    signal_s,
                    signal_n[0], #open
                    signal_n[1], # close
                    current)) #signal num

    # compare to previous
    for date_back in dates_back_check:
        date_check = dt.date.today() - dt.timedelta(date_back)
        print(date_check)
        # date_check = dt.date(2021, 12, 11) # override until data

        for ticker in ticker_list:
            cursor.execute("call public.determine_performance(%s, %s, %s); fetch all in cur;",
                           (ticker, date_check.strftime("%m/%d/%Y"), ''))
            result = cursor.fetchall()

            if not result:
                print(f"\tNo previous data for {ticker} on {date_check}")
            else:
                # TODO calculate success
                # TODO store success somewhere?
                for row in result:
                    print(f"\t{ticker} Value then: {row[0]} signal: {row[1]}")
                    print(f"\tValue now: {si.get_live_price(ticker)}")

except (Exception, psycopg2.DatabaseError) as error:
    print("PostgreSQL error: ", error)

ps_connection.close()

# additionals:
# fb_earnings_hist = si.get_earnings_history("fb")
# fb_earnings = si.get_earnings("fb")
# print(fb_earnings)

# df = pd.DataFrame(np.random.randn(5, 4),
#                  index = ['a', 'b', 'c', 'd', 'e'],
#                  columns = ['A', 'B', 'C', 'D'])
# print(df)

# print(historical_datas)  # it is a dictionary of data frames

