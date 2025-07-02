import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
from alerts import send_telegram, send_email, log_to_google_sheets

def price_from_oilprice():
    try:
        r = requests.get("https://oilprice.com/oil-price-charts")
        soup = BeautifulSoup(r.content, "html.parser")
        tag = soup.find("span", {"id": "op_live_price"})
        return float(tag.text.replace("$", "").strip())
    except: return None

def price_from_investing():
    try:
        r = requests.get("https://www.investing.com/commodities/crude-oil")
        soup = BeautifulSoup(r.content, "html.parser")
        tag = soup.select_one(".instrument-price_last__KQzyA")
        return float(tag.text.replace(",", ""))
    except: return None

def price_from_yahoo():
    try:
        r = requests.get("https://finance.yahoo.com/quote/CL=F")
        soup = Beautiful.BeautifulSoup(r.content, "html.parser")
        tag = soup.find("fin-streamer", {"data-symbol": "CL=F"})
        return float(tag.text.replace(",", ""))
    except: return None

def get_oil_prices():
    prices = {
        "OilPrice.com": price_from_oilprice(),
        "Investing.com": price_from_investing(),
        "Yahoo Finance": price_from_yahoo()
    }
    valid = [p for p in prices.values() if p is not None]
    avg = round(sum(valid) / len(valid), 2) if valid else None
    return avg, prices

def get_oil_news():
    try:
        url = "https://oilprice.com/"
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        articles = soup.select("div.categoryArticle__content > h4 > a")[:5]
        return [a.text.strip() for a in articles]
    except:
        return ["❌ Failed to fetch news."]

def log_price(price):
    conn = sqlite3.connect('price_log.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS prices (timestamp TEXT, price REAL)''')
    c.execute("INSERT INTO prices VALUES (?, ?)", (datetime.now().isoformat(), price))
    conn.commit()
    conn.close()

def get_last_price():
    conn = sqlite3.connect('price_log.db')
    c = conn.cursor()
    c.execute("SELECT price FROM prices ORDER BY ROWID DESC LIMIT 1 OFFSET 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def check_and_alert():
    avg_price, sources = get_oil_prices()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if avg_price is None:
        return None, None, "❌ Price fetch failed", sources

    last_price = get_last_price()
    log_price(avg_price)

    if last_price:
        if avg_price > last_price:
            status = "🟢 Price is UP"
        elif avg_price < last_price:
            status = "🔻 Price is DOWN"
        else:
            status = "⏸ No Change"
    else:
        status = "ℹ️ First price recorded"

    send_telegram(f"{status} — ${avg_price} at {timestamp}")
    send_email(f"{status} — ${avg_price} at {timestamp}")
    log_to_google_sheets(avg_price, status, timestamp)

    return avg_price, get_oil_news(), status, sources