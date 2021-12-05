import csv

import requests
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import re

def get_index():
    cnn = "https://www.technoduet.com/a-comprehensive-list-of-blockchain-platforms/"
    req = Request(url=cnn, headers={"user-agent": "my-app/0.0.1"})
    response = urlopen(req)
    html = BeautifulSoup(response, features="html.parser")
    data = html.findAll(id=re.compile(r"[0-9]{1,2}-+"))
    link_list = []
    for d in data:
        p = d.findNext("p")
        p = p.findNext("p")
        #print(p.contents[-1])
        link = p.contents[-1].replace(": ", "")
        #print(link)
        if ":" in link:
            link = "didux.io"
        link_list.append(link)
        print(link)
    print(link_list)
    with open("blockchain_list.csv", "w", newline="\n") as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerow(link_list)



get_index()