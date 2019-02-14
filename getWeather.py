import pymongo
import requests as re
import config

# Connect to db
client = pymongo.MongoClient("mongodb://"+config.writer_user+":"+config.writer_pw+"@localhost:27017/sse-data")
db = client["sse-data"]

# Scraping the live demand and generation of the Orkney ANM
weather_col = db["weather"]
weather_scrape = re.get("http://api.openweathermap.org/data/2.5/weather?lat=59.1885692&lon=-2.8229873&APPID="+config.API_KEY).json()
weather_id = weather_col.insert_one(weather_scrape)
