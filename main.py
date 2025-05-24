import random
import requests
import yagmail
import datetime
import os
import dotenv
import pytz
from datetime import datetime as dt

dotenv.load_dotenv()

# Environment variables
LONGITUDE = os.getenv("LONGITUDE")
LATITUDE = os.getenv("LATITUDE")
MY_GMAIL_USER = os.getenv("MY_GMAIL_USER")
MY_GMAIL_PASS = os.getenv("MY_GMAIL_PASS")
EMAIL_SEND_TO = os.getenv("EMAIL_SEND_TO")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

# Configuration
begin_time = 6
end_time = 21
timezone = "America/Los_Angeles"
unsplash_query = ["wild bird", "wild animal", "endangered species", "wild fish", "ocean", "train", "boat", "storm",
                  "crab", "nature", "storm", "mountain", "fire", "camping", "wildlife", "coast guard", "navy", "flower",
                  "tree", "forest", "flower", "tornado", "military", "police", "whale", "pinniped", "bird"]
unsplash_optimized_for_mobile = True
rain_only_notification = False

def get_mlb_matchup():
    """Find the highest priority MLB game happening today"""
    highlighted_teams = [
        "San Francisco Giants",
        "Los Angeles Dodgers",
        "Toronto Blue Jays",
        "Milwaukee Brewers"
    ]
    
    url = "https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        pst = pytz.timezone('America/Los_Angeles')
        matching_games = []
        
        for date in data.get('dates', []):
            for game in date.get('games', []):
                away_team = game['teams']['away']['team']['name']
                home_team = game['teams']['home']['team']['name']
                away_record = game['teams']['away']['leagueRecord']
                home_record = game['teams']['home']['leagueRecord']
                
                for priority, team in enumerate(highlighted_teams):
                    if team in [away_team, home_team]:
                        game_time_utc = dt.strptime(game['gameDate'], "%Y-%m-%dT%H:%M:%SZ")
                        game_time_pst = pytz.utc.localize(game_time_utc).astimezone(pst)
                        hour = game_time_pst.strftime("%I").lstrip("0")
                        minute = game_time_pst.strftime("%M")
                        ampm = game_time_pst.strftime("%p")
                        time_str = f"{hour}:{minute} {ampm}"
                        
                        # Always show home team first with win percentages
                        home_str = f"<b>{home_team}</b> [{home_record['pct']}]"
                        away_str = f"<b>{away_team}</b> [{away_record['pct']}]"
                        matchup_str = f"{home_str} vs {away_str} at {time_str}"
                        
                        matching_games.append((priority, matchup_str))
                        break
        
        if matching_games:
            matching_games.sort()
            return matching_games[0][1]
    
    return "No MLB games of interest today."

def get_weather_report():
    """Get today's weather forecast"""
    weather_api = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude=" + \
                  f"{LONGITUDE}&hourly=precipitation&timezone=America%2FLos_Angeles&forecast_days=1"
    response = requests.get(weather_api)
    weather_data = response.json()
    
    rainfall_info = ""
    for hour in range(begin_time, end_time):
        precipitation = weather_data["hourly"]["precipitation"][hour]
        time_label = "AM" if hour < 12 else "PM"
        hour_label = hour if hour <= 12 else hour - 12
        if hour_label == 0:
            hour_label = 12
        if precipitation > 0:
            rainfall_info += f"During {hour_label}{time_label}, there will be {precipitation} mm of rain.\n"
    
    return rainfall_info if rainfall_info else "Clear skies today :)"

def get_random_image():
    """Get a random image from Unsplash"""
    unsplash_chosen_query = random.choice(unsplash_query)
    unsplash_parameters = {
        "query": unsplash_chosen_query,
        "client_id": UNSPLASH_ACCESS_KEY,
        "count": 1
    }
    
    if unsplash_optimized_for_mobile:
        unsplash_parameters["orientation"] = "portrait"
    
    unsplash_response = requests.get(url="https://api.unsplash.com/photos/random/", params=unsplash_parameters)
    unsplash_data = unsplash_response.json()
    return {
        "url": unsplash_data[0]["urls"]["raw"],
        "author": unsplash_data[0]["user"]["username"],
        "portfolio": unsplash_data[0]["user"]["portfolio_url"] or unsplash_data[0]["links"]["html"],
        "query": unsplash_chosen_query
    }

def format_current_date():
    """Format current date nicely"""
    return "{d:%A}, {d:%B} {d.day}, {d.year}".format(d=datetime.datetime.now(pytz.timezone(timezone)))

def format_current_time():
    """Format current time nicely"""
    formatted_time = datetime.datetime.now(pytz.timezone(timezone)).strftime("%I:%M %p")
    return formatted_time.lstrip("0")

def send_email():
    """Send the combined email with weather and MLB info"""
    # Gather all data
    readable_date = format_current_date()
    current_time_str = format_current_time()
    weather_report = get_weather_report()
    mlb_matchup = get_mlb_matchup()
    image_data = get_random_image()
    
    # Prepare email content
    contents = (
        f"<h2>Weather Report</h2>"
        f"{weather_report}<br><br>"
        f"---------------------------------------------------------------<br>"
        f"<h2>MLB Game of Interest</h2>"
        f"{mlb_matchup}<br><br>"
        f"---------------------------------------------------------------<br><br><br>"
        f"Here's an image! This came from the query \"{image_data['query']}\".<br><br>"
        f"<img src='{image_data['url']}' height='600'><br><br>"
        f"Author: <b>{image_data['author']}</b>, <a href={image_data['portfolio']}>{image_data['portfolio']}</a>"
    )
    
    # Send email
    yag = yagmail.SMTP(MY_GMAIL_USER, MY_GMAIL_PASS)
    subject = f"Daily Report for {readable_date} ({current_time_str})"
    
    if rain_only_notification and "rain" in weather_report.lower():
        yag.send(to=EMAIL_SEND_TO, subject=f"(RAIN TODAY) {subject}", contents=contents)
    elif not rain_only_notification:
        yag.send(to=EMAIL_SEND_TO, subject=subject, contents=contents)

if __name__ == "__main__":
    send_email()