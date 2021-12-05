from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

base_url = "https://coinmarketcap.com"
crypto_category_extension = "/cryptocurrency-category/"
view_extension = "/view/"


def html(url):
    req = Request(url=url, headers={"user-agent": "my-app/0.0.1"})
    response = urlopen(req)
    html_response = BeautifulSoup(response, features="html.parser")
    return html_response


def table_body(html_data):
    return html_data.find("tbody")


def table_row(table):
    return table.findAll("tr")


def normalize_string(string):
    normalized_string = string.lower().replace(" ", "-")
    normalized_string = normalized_string.replace("&", "")
    normalized_string = normalized_string.replace("/", "-")
    normalized_string = normalized_string.replace("---", "-")
    normalized_string = normalized_string.replace("--", "-")
    normalized_string = normalized_string.replace(".", "-")

    return normalized_string


table_row_list = table_row(table_body(html(base_url + crypto_category_extension)))

industries = []
avg_price_change = []
gainers = []
market_cap = []
dominance = []
volume = []

for tr in table_row_list:
    td = tr.findAll("td")
    industries.append(td[1].text)
    avg_price_change.append(td[2].text)
    gainers.append(td[3].findAll("div")[2].text + "," + td[3].findAll("div")[3].text)
    market_cap.append(td[4].text)
    dominance.append(td[5].text)
    volume.append(td[6].text)

for industry in industries:

    industry_link = normalize_string(industry)
    if industry == "NFTs & Collectibles":
        industry_link = "collectibles-nfts"
    if industry == "Electric Global Portfolio":
        industry_link = "electric-capital-portfolio"
    if industry == "Lending / Borrowing":
        industry_link = "lending-borowing"
    if industry == "BSC Ecosystem":
        industry_link = "binance-smart-chain"
    try:
        trl = table_row(table_body(html(base_url+view_extension+industry_link)))
        for t in trl:
            tds = t.findAll("td")
            if len(tds) == 5:
                continue
            else:
                project_name = tds[2].text
                current_price = tds[3].text
                change_24h = tds[4].text
                change_7d = tds[5].text
                market_cap = tds[6].text
                volume_24h = tds[7].text

    except Exception as e:
        print(f"Exception occurred with link {industry_link}: {e}")
    print("******************************")

