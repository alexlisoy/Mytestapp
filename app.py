from flask import Flask, render_template
from scraper import check_and_alert
import threading
import time

app = Flask(__name__)
current_data = {
    "price": None,
    "news": [],
    "status": "Starting...",
    "last_updated": "",
    "sources": {}
}

def run_scraper():
    def job():
        price, news, status, sources = check_and_alert()
        if price:
            current_data.update({
                "price": price,
                "news": news,
                "status": status,
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "sources": sources
            })
    job()
    while True:
        time.sleep(3600)
        job()

@app.route("/")
def dashboard():
    return render_template("dashboard.html", data=current_data)

if __name__ == "__main__":
    threading.Thread(target=run_scraper, daemon=True).start()
    app.run(debug=True, host="0.0.0.0")