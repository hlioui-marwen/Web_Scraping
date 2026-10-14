import sqlite3
import requests
import selectorlib
import smtplib, ssl
import os
import time

"INSERT INTO events VALUES ('Tigers', 'Tiger City', '2088.10.14')"
"SELECT * FROM events WHERE date='2088.10.16'"
"DELETE FROM events WHERE band='Tigers'"

connection = sqlite3.connect("data.db", timeout=30)


url = "https://programmer100.pythonanywhere.com/tours/"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def scrape(url):
    """Scrape the page source from the url"""
    response = requests.get(url, headers=HEADERS)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yml")
    value = extractor.extract(source)["tours"]
    return value


def send_email(message):
    host = "smtp.gmail.com"
    port = 465

    username = "marwen@gmail.com"
    password = "password"

    receiver = "marwen@gmail.com"
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)

    print("email was sent")


def store(extracted):
    row = extracted.split(",")
    row = [item.strip() for item in row]
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events VALUES (?, ?, ?)", row)
    connection.commit()

def read(extracted):
    row = extracted.split(",")
    row = [item.strip() for item in row]
    band, city, date = row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events")
    rowss = cursor.fetchall()
    print(rowss)
    cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))
    rows = cursor.fetchall()
    print(rows)
    return rows

if __name__ == "__main__":
    while True:
        scraped = scrape(url)
        extracted = extract(scraped)
        print(extracted)
        if extracted != "No upcoming tours":
            row = read(extracted)
            if not row:
                store(extracted)
                send_email(message="Hey, new event was found")
        time.sleep(2)
