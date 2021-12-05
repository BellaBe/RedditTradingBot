import praw
import config

from textblob import TextBlob
from binance.client import Client
from binance.enums import *


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
needed_sentiments = 300
TRADE_SYMBOL = "BTCUSDT"
TRADE_QUANTITY = 0.001
in_position = False


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
        print(f"An exception has occured: {e}")
        return False
    return True


for comment in reddit.subreddit("bitcoin+cryptocurrency+ripple+stellar").stream.comments():
    redditComment = comment.body
    blob = TextBlob(redditComment)
    sent = blob.sentiment
    #print(f"**********Sentiment is: {str(sent.polarity)}")

    if sent.polarity != 0.0:
        sentiment_list.append(sent.polarity)
        print(len(sentiment_list))
        if len(sentiment_list) > needed_sentiments and round(average(sentiment_list)) > 0.5:
            print("********BUY")
            if in_position:
                print("****** BUY ORDER BUT WE OWN ******")
            else:
                print("****** BUY ORDER ******")
                order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_succeeded:
                    in_position = True
        elif len(sentiment_list) > needed_sentiments and round(average(sentiment_list)) < -0.5:
            print("********SELL*********")
            if in_position:
                order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_succeeded:
                    in_position = False
                else:
                    print("********SELL ORDER BUT WE DO NOT OWN")







# for comment in reddit.subreddit("redditdev").comments(limit=25):
#     print(comment.author)
#     print(comment.body)

# for submission in reddit.subreddit("bitcoin").hot(limit=25):
#     print(submission.title)

# for comment in reddit.subreddit("bitcoin").stream.comments():
#     print(comment.body)

