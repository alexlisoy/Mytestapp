import requests
import smtplib
from email.mime.text import MIMEText
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import *

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

def send_email(msg):
    try:
        email = MIMEText(msg)
        email["Subject"] = "Oil Price Alert"
        email["From"] = EMAIL_USER
        email["To"] = EMAIL_TO
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(email)
    except Exception as e:
        print("Email failed:", e)

def log_to_google_sheets(price, status, timestamp):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CRED_JSON, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
        sheet.append_row([timestamp, price, status])
    except Exception as e:
        print("Sheets error:", e)