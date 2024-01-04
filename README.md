# Temperature Blanket

A selenium-based script for getting the average daily temperature from [timeanddate](https://www.timeanddate.com/).

# Usage

1. Install python 3.12 and `pip install poetry`
2. Run `poetry install`
3. Add environment variables or a .env file that define the following:

- `SMTP_SERVER` - The host of your SMTP server. Defaults to `smtp.gmail.com`.
- `SMTP_PORT` - The port of your SMTP server. Defaults to `587`.
- `SMTP_USERNAME` - The email of your SMTP username, also used as the sender's email address.
- `SMTP_PASSWORD` - The password of the SMTP account associated with the username. If using gmail, you will need to obtain an [app password](https://support.google.com/accounts/answer/185833?hl=en).
- `HEADLESS` - Set to `true` if you want to run selenium in headless mode. Defaults to `false`.

4. Run the script: `poetry run python -m temperature_blank.main --email your.email@example.com --temperatures_url https://www.timeanddate.com/weather/@4367175 --sunrise_url https://www.timeanddate.com/sun/@z-us-20850`

- You may also specify `--date` as a `YYYY-MM-DD` formatted string, or it will default to yesterday's date.
- Email is optional, if not provided, the output will only be shown in stdout.
