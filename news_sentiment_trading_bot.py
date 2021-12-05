from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import pandas as pd
import tensorflow as tf
import numpy as np
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import alpaca_trade_api as tradeapi

import config

finviz_url = "https://finviz.com/quote.ashx?t="

ticker = "TSLA"
url = finviz_url + ticker

req = Request(url=url, headers={"user-agent": "my-app/0.0.1"})
response = urlopen(req)
html = BeautifulSoup(response, features="html.parser")
news_table = html.find(id="news-table")
data_rows = news_table.find_all("tr")
df = pd.DataFrame(columns=["News_Title", "Time"])
for i, data_row in enumerate(data_rows):
    a_text = data_row.a.text
    td_text = data_row.td.text
    df = df.append({"News_Title": a_text, "Time": td_text}, ignore_index=True)

with open("./tokenizer.pickle", "rb") as handle:
    tokenizer = pickle.load(handle)

model = tf.keras.models.load_model("./model1.h5")

oov_tok = "<OOV>"
trunc_type = "post"
padding_type = "post"
vocab_size = 1000
max_length = 142


def preprocess_text(text):
    sequences = tokenizer.texts_to_sequences(text)
    padded = pad_sequences(sequences, maxlen=max_length, padding=padding_type, truncating=trunc_type)
    return padded


prep = preprocess_text(df.News_Title)
prep = model.predict(prep)

df["sent"] = np.argmax(prep, axis=-1)

print(df.sent.value_counts())

ALPACA_ENDPOINT = "https://paper-api.alpaca.markets"

api = tradeapi.REST(config.ALPACA_PAPER_KEY, config.ALPACA_PAPER_SECRET, ALPACA_ENDPOINT)
account = api.get_account()
print(account)

mode_sentiment = df.sent.mode().iloc[0]
print(mode_sentiment)

if mode_sentiment == 1:
    print("Neutral sentiment, nothing to do!")
elif mode_sentiment == 0:
    api.submit_order(symbol=ticker, qty=1, side="sell", type="market", time_in_force="gtc")
    print("SELL")
elif mode_sentiment == 2:
    api.submit_order(symbol=ticker, qty=1, side="buy", type="market", time_in_force="gtc")
    print("BUY")
