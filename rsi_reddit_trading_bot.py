import pandas as pd
import praw
import config

from textblob import TextBlob
from binance.client import Client
from binance.enums import *
from ta.momentum import RSIIndicator


client = Client(config.BINANCE_FIRST_API, config.BINANCE_FIRST_SECRET)
info = client.get_account()
print(info)

reddit = praw.Reddit(
    client_id=config.REDDIT_ID,
    client_secret=config.REDDIT_SECRET,
    passwod=config.REDDIT_PASS,
    user_agent="USERAGENT",
    username=config.REDDIT_USER
)

sentiment_list = []
dogePrices = []
needed_sentiments = 300
TRADE_SYMBOL = "DOGEGBP"
TRADE_QUANTITY = 0.001
in_position = False
UPPER_BAND = 70
LOWER_BAND = 30


def average(lst):
    if len(lst) == 0:
        return len(lst)
    else:
        return sum(sentiment_list[-needed_sentiments:]) / needed_sentiments


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("Sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print(f"An exception has occurred: {e}")
        return False
    return True


for comment in reddit.subreddit("dogecoin").stream.comments():
    redditComment = comment.body
    blob = TextBlob(redditComment)
    sent = blob.sentiment
    if sent.polarity != 0.0:
        sentiment_list.append(sent.polarity)
        #print(len(sentiment_list))

        candles = client.get_historical_klines(TRADE_SYMBOL, Client.KLINE_INTERVAL_5MINUTE, "5 Minutes ago UTC")
        print("CANDLES", candles)
        if len(dogePrices) == 0:
            dogePrices.append(float(candles[-1][1]))
        elif dogePrices[-1] != float(candles[-1][1]):
            dogePrices.append(float(candles[-1][1]))

        print("******* Length of Prices list is: " + str(len(dogePrices)))
        rsi = RSIIndicator(pd.Series(dogePrices))
        print(rsi.rsi())
        df = rsi.rsi()
        df.iloc[-1]

        if df.iloc[-1] < LOWER_BAND and len(sentiment_list) > needed_sentiments and round(average(sentiment_list)) > 0.5:
            print("********BUY")
            if in_position:
                print("****** BUY ORDER BUT WE OWN ******")
            else:
                print("****** BUY ORDER ******")
                # order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                # if order_succeeded:
                #     in_position = True

        elif df.iloc[-1] > UPPER_BAND and len(sentiment_list) > needed_sentiments and round(average(sentiment_list)) > 0.5:
            print("********SELL*********")
            if in_position:
                print("Hello")
                # order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                # if order_succeeded:
                #     in_position = False
                # else:
                #     print("********SELL ORDER BUT WE DO NOT OWN")

