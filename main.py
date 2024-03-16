import requests
import yagmail
from datetime import datetime
from bs4 import BeautifulSoup
import secrets

# define the hours you care about the weather in 24h hour format
BEGIN_TIME = 6
END_TIME = 21

wildlife_website_url = "https://dailywildlifephoto.nathab.com/"
weather_api = f"https://api.open-meteo.com/v1/forecast?latitude={secrets.secrets.get('LATITUDE')}&longitude=" + \
              f"{secrets.secrets.get('LONGITUDE')}&hourly=precipitation&timezone=America%2FLos_Angeles&forecast_days=1"

response_wildlife = requests.get(wildlife_website_url)
soup = BeautifulSoup(response_wildlife.content, 'html.parser')

image_url = soup.find('img').get('src')
info_location = soup.find('h2', class_='what-and-where')
species = info_location.find_all('span')[0].text
location = info_location.find_all('span')[1].text

response_weather = requests.get(weather_api)
weather_data = response_weather.json()

date_str = weather_data["hourly"]["time"][0]

def format_date(date_str):
    # Parse the input date string
    date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')

    # Format the parsed date into "Month Day, Year" format
    formatted_date = date_obj.strftime('%B %d, %Y')

    return formatted_date

rainfall_info = ''
for hour in range(BEGIN_TIME, END_TIME):
    precipitation = weather_data["hourly"]["precipitation"][hour]
    time_label = 'AM' if hour < 12 else 'PM'
    hour_label = hour if hour <= 12 else hour - 12
    if hour_label == 0:
        hour_label = 12
    if precipitation > 0:
        rainfall_info += f"During {hour_label}{time_label}, there will be {precipitation} mm of rain.\n"

data_content = str([rainfall_info])

if not rainfall_info:
    data_content = "Clear skies today :)"

contents = (
    f"Good morning, buddy!<br><br>{data_content} <br><br> ---------------------------------------------------------------"
    f"<br><br> Here's NatHab's wildlife picture of the day! <br><br> <img src='{image_url}' height='500'> <br><br>"
    f"Species: <b>{species}</b> <br> Location: {location}"
)

readable_date = format_date(date_str)
yag = yagmail.SMTP(secrets.secrets.get("MY_GMAIL_USER"), secrets.secrets.get("MY_GMAIL_PASS"))

yag.send(to=secrets.secrets.get("EMAIL_SEND_TO"), subject='Rain report for '+ readable_date, contents=contents)
