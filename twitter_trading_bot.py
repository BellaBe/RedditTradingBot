import requests
import os
import json
from config import *
import preprocessor as p
from langdetect import detect
from csv import writer
import config

from binance.client import Client
from binance.enums import *

from ernie import SentenceClassifier
import numpy as np

client = Client(config.BINANCE_FIRST_API, config.BINANCE_FIRST_SECRET)

classifier = SentenceClassifier(model_path="./output")

in_position = False
TRADE_SYMBOL = "BTCUSDT"
TRADE_QUANTITY = 0.005

sentimentList = []
neededSentiments = 500


def average(lst):
    if len(lst) == 0:
        return len(lst)
    else:
        return sum(lst[-neededSentiments:]) / neededSentiments



def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("Sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print(e)
        return False
    return True


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def get_rules(headers, bearer_token):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(headers, bearer_token, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(headers, delete, bearer_token):
    # You can adjust the rules if needed
    sample_rules = [
        {"value": "#ripple", "tag": "XRP"},
        #{"value": "cat has:images -grumpy", "tag": "cat pictures"},
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream(headers, set, bearer_token):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", headers=headers, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:

            json_response = json.loads(response_line)
            tweet = json_response["data"]["text"]
            #print(tweet)
            tweet = p.clean(tweet)
            tweet = tweet.replace(":", "")
            try:
                if detect(tweet) == "en":
                    try:
                        classes = ["Bearish", "Neutral", "Bullish"]
                        probabilities = classifier.predict_one(tweet)
                        classes[np.argmax(probabilities)]
                        polarity = classes[np.argmax(probabilities)]
                        sentimentList.append(polarity)
                        print(polarity)
                        if len(sentimentList) > 50:
                            end_list = sentimentList[-50:]
                            print(f"*******TOTAL BULLISH: {str(end_list.count('Bullish'))}")
                            print(f"*******TOTAL BEARISH: {str(end_list.count('Bearish'))}")

                            if end_list.count('Bullish') > 50:
                                if in_position:
                                    print(f"******* BUY BUT WE OWN")
                                else:
                                    print(f"******* BUY")
                                    # order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                                    # if order_succeeded:
                                    #     in_position = True

                            elif end_list.count('Bearish') > 50:
                                if in_position:
                                    print("in bearish position")
                                    # order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                                    # if order_succeeded:
                                    #     in_position = False
                                else:
                                    print(f"******* SELL BUT WE DO NOT OWN")
                    except Exception as e:
                        print(f"An exception occurred in trying to place an order: {e}")
            except Exception as e:
                print(f"An exception occurred in trying to place an order: {e}")


def main():
    bearer_token = TWITTER_BEARER
    headers = create_headers(bearer_token)
    rules = get_rules(headers, bearer_token)
    delete = delete_all_rules(headers, bearer_token, rules)
    set = set_rules(headers, delete, bearer_token)
    get_stream(headers, set, bearer_token)


if __name__ == "__main__":
    main()