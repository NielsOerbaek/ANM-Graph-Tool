import pymongo
import datetime
import numpy as np
import pandas as pd
import config

zone_names = ["Core Zone", "Zone 1", "Zone 1A", "Zone 2", "Zone 2A", "Zone 2B", "Zone 3", "Zone 4", "Zone 4A"]

client = pymongo.MongoClient("mongodb://"+config.reader_user+":"+config.reader_pw+"@"+config.SERVER+"/sse-data")
db = client["sse-data"]
status = db["ANM_status"]

def getDate(s): return datetime.datetime.fromtimestamp(int(s["timestamp"]))
def isCurtailed(z): return z["ANM_Operation"] == "YELLOW"
def isStopped(z): return z["ANM_Operation"] == "RED"

def getDataFrame(start=0, end=0):

    if end == 0: end = start+86400

    data_dict = dict()

    for s in status.find({"timestamp": {"$gt": start-1, "$lt": end}}):
        d = getDate(s).replace(microsecond=0,second=0)
        zs = dict()
        for z in zone_names:
            ss = int(isStopped(s[z]))
            cs = int(isCurtailed(s[z]) or ss)
            zs[z+": Curtailed"] = cs
            zs[z+": Full Stop"] = ss
        data_dict[d] = zs

    demand = db["demand"]

    for s in demand.find({"timestamp": {"$gt": start-1, "$lt": end}}):
        d = getDate(s).replace(microsecond=0,second=0)
        if d in data_dict.keys() and len(data_dict[d]) < 20:
            data_dict[d]["Demand"] = s["data"][0]["data"][0]
            data_dict[d]["Generation"] = s["data"][2]["data"][1]+s["data"][3]["data"][1]
            data_dict[d]["ANM Generation"] = s["data"][2]["data"][1]
            data_dict[d]["Non-ANM Generation"] = s["data"][3]["data"][1]

    df = pd.DataFrame.from_dict(data_dict, orient="index")

    #df = cleanData(df)

    return df


def getWeatherDataFrame(start=0, end=0):

    if end == 0: end = start+86400

    data = dict()

    weather = db["weather"]

    for w in weather.find({"dt": {"$gt": start-1, "$lt": end}}):
        # Make datetime object at round to nearest 10 minutes.
        time = datetime.datetime.fromtimestamp(w["dt"]).replace(microsecond=0,second=0)
        data[time] = w["wind"]

    df = pd.DataFrame.from_dict(data, orient="index")

    return df

def cleanData(df):
    dt = datetime.timedelta(hours=6)
    total_cleaned = 0
    for z in zone_names:
        z = [z+": Curtailed", z+": Full Stop"]
        b = df[z].sum().sum() / 2
        cleanCol(df,dt,z)
        r = b - df[z].sum().sum() / 2
        total_cleaned += r
        print("Cleaned from",z,":",r/6,"hours")
    print("Total Cleaned:",total_cleaned/6,"hours")
    return df

def cleanCol(df, threshold, zone):
    c,d,e = False, False, False
    cs, ds = None, None
    for i, r in df.iterrows():
        if not c and r[zone].any():
            c, cs = True, i
        elif c and not r[zone].any():
            c,d = False, False
            if e:
                df.loc[cs:i,zone] = 0
                e = False
        if c and not d and r["Demand"] > r["Generation"]:
            d, ds = True, i
        elif c and d and r["Demand"] <= r["Generation"]:
            d = False
        if not e and d and i-ds >= threshold:
            e = True
