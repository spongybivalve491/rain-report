import random
import requests
import yagmail
import datetime
import os
import dotenv
import pytz

dotenv.load_dotenv()

LONGITUDE = os.getenv("LONGITUDE")
LATITUDE = os.getenv("LATITUDE")
MY_GMAIL_USER = os.getenv("MY_GMAIL_USER")
MY_GMAIL_PASS = os.getenv("MY_GMAIL_PASS")
EMAIL_SEND_TO = os.getenv("EMAIL_SEND_TO")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

# define the hours you care about the weather in 24h hour format
begin_time = 6
end_time = 21

# https://gist.github.com/mjrulesamrat/0c1f7de951d3c508fb3a20b4b0b33a98
timezone = "America/Los_Angeles"

# search query for random images
unsplash_query = ["wild bird", "wild animal", "endangered species", "wild fish", "ocean", "train", "boat", "storm",
                  "crab", "nature", "storm", "mountain", "fire", "camping", "wildlife", "coast guard", "navy", "flower",
                  "tree", "forest", "flower", "tornado", "military", "police", "whale", "pinniped", "bird"]

# fetch a portrait orientation photo
unsplash_optimized_for_mobile = True

# only send email on rainy forcast
rain_only_notification = True

weather_api = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude=" + \
              f"{LONGITUDE}&hourly=precipitation&timezone=America%2FLos_Angeles&forecast_days=1"
unsplash_api = "https://api.unsplash.com/photos/random/"

response_weather = requests.get(weather_api)
weather_data = response_weather.json()

date_str = weather_data["hourly"]["time"][0]

def format_date():
    formatted_date = "{d:%A}, {d:%B} {d.day}, {d.year}".format(d=datetime.datetime.now(pytz.timezone(timezone)))
    return formatted_date

def current_time():
    formatted_time = datetime.datetime.now(pytz.timezone(timezone)).strftime("%I:%M %p")
    formatted_time = formatted_time.lstrip("0")
    return formatted_time


readable_date = format_date()
rainfall_info = ""

for hour in range(begin_time, end_time):
    precipitation = weather_data["hourly"]["precipitation"][hour]
    time_label = "AM" if hour < 12 else "PM"
    hour_label = hour if hour <= 12 else hour - 12
    if hour_label == 0:
        hour_label = 12
    if precipitation > 0:
        rainfall_info += f"During {hour_label}{time_label}, there will be {precipitation} mm of rain.\n"

data_content = str(rainfall_info)

if not rainfall_info and not rain_only_notification:
    data_content = "Clear skies today (I think) :)"

unsplash_chosen_query = random.choice(unsplash_query)

unsplash_parameters = {
    "query": unsplash_chosen_query,
    "client_id": UNSPLASH_ACCESS_KEY,
    "count": 1
}

if unsplash_optimized_for_mobile:
    unsplash_parameters["orientation"] = "portrait"

unsplash_response = requests.get(url=unsplash_api, params=unsplash_parameters)
unsplash_data = unsplash_response.json()
unsplash_img_url = unsplash_data[0]["urls"]["raw"]
unsplash_author = unsplash_data[0]["user"]["username"]
unsplash_author_portfolio = unsplash_data[0]["user"]["portfolio_url"]

if unsplash_author_portfolio is None:
    unsplash_author_portfolio = unsplash_data[0]["links"]["html"]


contents = (
    f"Hiya, buddy!<br><br>{data_content} <br><br> ---------------------------------------------------------------"
    f"<br><br>Here's an image! This came from the query \"{unsplash_chosen_query}\".<br><br>"
    f"<img src='{unsplash_img_url}' height='600'><br><br>"
    f"Author: <b>{unsplash_author}</b>, <a href={unsplash_author_portfolio}>{unsplash_author_portfolio}</a>"
)

yag = yagmail.SMTP(MY_GMAIL_USER, MY_GMAIL_PASS)
if rainfall_info and rain_only_notification:
    yag.send(to=EMAIL_SEND_TO, subject='(RAIN TODAY) Rain report for '+ readable_date + ' (' + current_time() + ")",
            contents=contents)
if not rain_only_notification:
    yag.send(to=EMAIL_SEND_TO, subject='Rain report for ' + readable_date + ' (' + current_time() + ")",
             contents=contents)