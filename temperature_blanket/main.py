import datetime
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from seleniumbase import Driver

load_dotenv()
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = os.environ.get("SMTP_PORT", 587)
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
HEADLESS = os.environ.get("SELENIUM_HEADLESS", "false") == "true"
TIME_REGEX = r"(\d+:\d+ [ap]m).*"


def send_email(recipient: str, subject: str, body: str):
    message = MIMEMultipart()
    message["From"] = SMTP_USERNAME
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, recipient, message.as_string())


def convert_to_minutes_since_midnight(time_str):
    if not isinstance(time_str, str):
        return float("-inf")
    dummy_date = datetime.datetime.strptime("2000-01-01 " + time_str, "%Y-%m-%d %I:%M %p")
    return dummy_date.hour * 60 + dummy_date.minute


if __name__ == "__main__":
    date = datetime.date.today() - datetime.timedelta(1)
    temperatures_url = f"https://www.timeanddate.com/weather/@4367175/historic?hd={date.strftime('%Y%m%d')}"
    sunrise_url = f"https://www.timeanddate.com/sun/@z-us-20850?month={date.month}"
    driver = Driver(uc=True, incognito=True, headless=HEADLESS)

    try:
        driver.get(temperatures_url)
        dfs = pd.read_html(StringIO(driver.page_source))
        if len(dfs) != 2:
            raise ValueError("Could not find 24 hour table.")
        df = dfs[1]

        times = (
            df[("Unnamed: 0_level_0", "Time")].str.extract(TIME_REGEX).iloc[:, 0].map(convert_to_minutes_since_midnight)
        )
        temps = df[("Conditions", "Temp")][:-1].map(lambda x: int(x[:-3]))

        driver.get("https://www.timeanddate.com/sun/@z-us-20850")
        dfs = pd.read_html(StringIO(driver.page_source))
        if len(dfs) != 2:
            raise ValueError("Could not find sunrise/sunset table.")

        df = dfs[1]
        sunrise = df[("Sunrise/Sunset", "Sunrise", "Sunrise")][date.day - 1]
        sunset = df[("Sunrise/Sunset", "Sunset", "Sunset")][date.day - 1]
        sunrise_time = convert_to_minutes_since_midnight(re.match(TIME_REGEX, sunrise).group(1))
        sunset_time = convert_to_minutes_since_midnight(re.match(TIME_REGEX, sunset).group(1))

        day_temps = temps[(sunrise_time <= times) & (times <= sunset_time)]
        avg_day_temp = round(day_temps.mean())

        print(f"{avg_day_temp=}")
        send_email("your.email@example.com", f"{date.strftime('%B %-d')}:  {avg_day_temp}°F", "")
    finally:
        driver.quit()
