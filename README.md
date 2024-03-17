# Rain Report

Rain report sends you an email detailing the time and the amount of rain for specified hours during the day. Never be caught unprepared in the rain again!

You also get a random picture because why not?

![received remail](/docs/rain-report.png)

## Precipitation
Precipitation data comes curtosy of [open-meteo.com](open-meteo.com). No API key is required. Rain is reported in mm.

##### Lattitude and longitude
These values are needed to get data. Use a site like [https://www.gps-coordinates.net/](https://www.gps-coordinates.net/) to find them for your location. These files should be stored locally in a .env file or under Secrets -> Actions on GitHub for scheduled running of main.py.
##### Local variables
`start_time` and `end_time` are defined in main.py. Use integers between 0-24 to set the interval that weather data will be collected.

## Email
This uses the [yagmail](https://pypi.org/project/yagmail/) library to send emails from a **gmail** account.
`MY_GMAIL_USER`, `MY_GMAIL_PASS`, and `EMAIL_SEND_TO` must be defined in a .env file locally or in GitHub secrets.

Any email may be used to receive emails.

## Random Image
The random image is provided from a [unsplash](https://unsplash.com/) endpoint. `UNPLASH_ACCESS_KEY` must be defined in a .env file.
`unsplash_query` is defined in main.py. It is a list of queries that the random picture will be selected from. Add as many search terms as you would like and one will be randomly selected.

## Scheduling automatically with GitHub Actions
To send an email at a specific time, use cron scheduling with GitHub Actions ([video tutorial](https://youtu.be/PaGp7Vi5gfM?si=fmxEORInrCymZNDf)). I had to change `os.environ("KEY")` to `os.getenv("KEY")` with [python-dotenv](https://pypi.org/project/python-dotenv/).
