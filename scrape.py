import pymongo
import requests as re
import time
from bs4 import BeautifulSoup
import config

client = pymongo.MongoClient("mongodb://"+config.writer_user+":"+config.writer_pw+"@localhost:27017/sse-data")
db = client["sse-data"]

# Scraping the live demand and generation of the Orkney ANM
demand_col = db["demand"]
demand_scrape = re.get("https://www.ssen.co.uk/Sse_Components/Views/Controls/FormControls/Handlers/ActiveNetworkManagementHandler.ashx?action=graph&contentId=14973").json()
demand = dict()
demand["timestamp"] = time.time()
demand["data"] = demand_scrape["data"]["datasets"]
demand_id = demand_col.insert_one(demand)

# Scraping the live status of the Orkney ANM
status_col = db["ANM_status"]
page = re.get("https://www.ssen.co.uk/ANMGeneration/").text
soup = BeautifulSoup(page, 'html.parser')
table = soup.find('table', attrs={'class':'table'})
rows = table.find_all('tr')[2:]

def parse_symbol(td):
	classes = td.span["class"]
	if "glyphicon-ok-sign" in classes:
		return "GREEN"
	if "glyphicon-warning-sign" in classes:
		return "YELLOW"
	if "glyphicon-remove-sign" in classes:
		return "RED"

status = dict()
status["timestamp"] = time.time()
for row in rows:
	label = row.find('td', attrs={'class':'ZoneData-ZoneLabel'}).contents[0].strip()
	status[label] = dict()
	status[label]["label"] = label
	symbols = row.find_all('td', attrs={'class':'ZoneData-NoText'})
	status[label]["ANM_Operation"] = parse_symbol(symbols[0])
	status[label]["SHEPD_Equipment"] = parse_symbol(symbols[1])
	status[label]["Generator_Site_Issues"] = parse_symbol(symbols[2])

status_id = status_col.insert_one(status)
