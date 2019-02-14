import sys
import numpy as np
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import pandas as pd
import getData
from datetime import datetime
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from matplotlib.lines import Line2D


def makeFileName(start_limit=0, stop_limit=0, zones=0):
    file_name = "graph"
    if start_limit != 0 and stop_limit != 0: file_name += "-from_"+start_limit+"_to_"+stop_limit
    elif start_limit != 0: file_name += "-from_"+start_limit+"_to_"+datetime.now().strftime('%Y-%m-%d')
    else: file_name += "-from_"+df.index[0].strftime('%Y-%m-%d')+"_to_"+datetime.now().strftime('%Y-%m-%d')
    if zones != 0: file_name += "-"+"_".join(zones).replace(" ","_")
    file_name += ".png"
    return file_name

def buildGraph(start_limit=0, stop_limit=0, zones=0):
    zone_names = ["Core Zone", "Zone 1", "Zone 1A", "Zone 2", "Zone 2A", "Zone 2B", "Zone 3", "Zone 4", "Zone 4A"]

    file_name = makeFileName(start_limit, stop_limit, zones)

    if start_limit != 0: start_limit = datetime.strptime(start_limit, '%Y-%m-%d').timestamp()
    if stop_limit != 0: stop_limit = datetime.strptime(stop_limit, '%Y-%m-%d').timestamp()

    df = getData.getDataFrame(start_limit, stop_limit)

    if zones != 0: zone_names = zones

    #Make separate columns for partial and full curtailment
    zones_cs = list(map(lambda z: z+": Curtailed", zone_names))
    zones_ss = list(map(lambda z: z+": Full Stop", zone_names))
    ss_bar = df[zones_ss].sum(axis=1)
    cs_bar = df[zones_cs].sum(axis=1)

    fig, ax1 = plt.subplots()
    ax1.plot(df.index,df["Demand"],"b--",df.index,df["Generation"],"k-", linewidth=1, alpha=1)
    ax1.set_xlabel("Time")
    ax1.set_ylabel("MegaWatt")
    ax1.legend(["Demand", "Generation"], loc=2)
    ax1.set_zorder(10)
    ax1.patch.set_visible(False)

    ax2 = ax1.twinx()
    ax2.plot(df.index, ss_bar, "r", df.index, cs_bar, "y", linewidth=0, alpha=0.7)
    plt.fill_between(df.index, cs_bar, step="post", color="y", alpha=0.5)
    plt.fill_between(df.index, ss_bar, step="post", color="r", alpha=0.5)
    ax2.set_ylabel("Zones with curtailment", color="0.75")
    ax2.set_ylim(0, len(zone_names))
    ax2_leg = ax2.legend(["Full Stop", "Partial Curtailment"], loc=1)
    for l in ax2_leg.legendHandles: l.set_linewidth(10)
    fig.autofmt_xdate()
    fig.set_size_inches(15, 8)
    plt.xticks(rotation=-45)
    plt.title("Demand, Generation for all of Orkney. Curtailments in " + ", ".join(zone_names))
    plt.savefig("./static/graphs/"+file_name, orientation='landscape')

    return file_name

def buildDeltaGraph(start_limit=0, stop_limit=0, zones=0):
    zone_names = ["Core Zone", "Zone 1", "Zone 1A", "Zone 2", "Zone 2A", "Zone 2B", "Zone 3", "Zone 4", "Zone 4A"]

    file_name = "delta-" + makeFileName(start_limit, stop_limit, zones)

    if start_limit != 0: start_limit = datetime.strptime(start_limit, '%Y-%m-%d').timestamp()
    if stop_limit != 0: stop_limit = datetime.strptime(stop_limit, '%Y-%m-%d').timestamp()

    df = getData.getDataFrame(start_limit, stop_limit)

    if zones != 0: zone_names = zones

    #Make separate columns for partial and full curtailment
    zones_cs = list(map(lambda z: z+": Curtailed", zone_names))
    zones_ss = list(map(lambda z: z+": Full Stop", zone_names))
    ss_bar = df[zones_ss].sum(axis=1)
    cs_bar = df[zones_cs].sum(axis=1)

    fig, ax1 = plt.subplots()
    delta = (df["Generation"]-df["Demand"])#.rolling(3).mean()
    ax1.plot(df.index, delta,"k-", linewidth=1, alpha=1)
    plt.fill_between(df.index, delta, color="k", alpha=0.5)
    ax1.set_xlabel("Time")
    ax1.set_ylabel("MegaWatt")
    ax1.set_ylim(-30, 30)
    ax1.legend(["Generation relative to Demand"], loc=2)
    ax1.set_zorder(10)
    ax1.patch.set_visible(False)

    ax2 = ax1.twinx()
    ax2.plot(df.index, ss_bar, "r", df.index, cs_bar, "y", linewidth=0, alpha=0.7)
    plt.fill_between(df.index, cs_bar, step="post", color="y", alpha=0.5)
    plt.fill_between(df.index, ss_bar, step="post", color="r", alpha=0.5)
    ax2.set_ylabel("Zones with curtailment", color="0.75")
    ax2.set_ylim(0, len(zone_names))
    ax2_leg = ax2.legend(["Full Stop", "Partial Curtailment"], loc=1)
    for l in ax2_leg.legendHandles: l.set_linewidth(10)
    fig.autofmt_xdate()
    fig.set_size_inches(15, 8)
    plt.xticks(rotation=-45)
    plt.title("Demand, Generation for all of Orkney. Curtailments in " + ", ".join(zone_names))
    plt.savefig("./static/graphs/"+file_name, orientation='landscape')

    return file_name

def buildDeltaZoneGraph(start_limit=0, stop_limit=0, zones=0):
    zone_names = ["Core Zone", "Zone 1", "Zone 1A", "Zone 2", "Zone 2A", "Zone 2B", "Zone 3", "Zone 4", "Zone 4A"]

    file_name = "delta-zone-" + makeFileName(start_limit, stop_limit, zones)

    if start_limit != 0: start_limit = datetime.strptime(start_limit, '%Y-%m-%d').timestamp()
    if stop_limit != 0: stop_limit = datetime.strptime(stop_limit, '%Y-%m-%d').timestamp()

    df = getData.getDataFrame(start_limit, stop_limit)

    if zones != 0: zone_names = zones

    curtailments = np.zeros(shape=(len(zone_names),len(df.index)))

    for i, zone in enumerate(zone_names):
        for j, status in enumerate(df[zone+": Curtailed"] + df[zone+": Full Stop"]):
            curtailments[i,j] = status


    fig, ax1 = plt.subplots()
    delta = (df["Generation"]-df["Demand"])#.rolling(3).mean()
    ax1.plot(df.index, delta,"k-", linewidth=1, alpha=0.8)
    plt.fill_between(df.index, delta, color="k", alpha=0.3)
    ax1.set_xlabel("Time")
    ax1.margins(x=0)
    ax1.set_ylabel("MegaWatt")
    ax1.yaxis.tick_right()
    ax1.yaxis.set_label_position("right")
    ax1.set_ylim(-30, 30)
    ax1.legend(["Generation relative to Demand"], loc=1)
    ax1.set_zorder(10)
    ax1.patch.set_visible(False)

    cm = plt.get_cmap("OrRd")

    ax2 = fig.add_subplot(111)
    ax2.pcolormesh(curtailments, alpha=1, cmap=cm, snap=True)
    ax2.set_ylabel("Zones")
    ax2.set_xticks([])
    ax2.set_yticks(np.arange(len(zone_names))+0.5)
    ax2.set_yticks(np.arange(len(zone_names)), minor=True)
    ax2.set_yticklabels(zone_names, rotation=0, fontsize="10", va="center")
    ax2.grid(b=True, which="minor", axis="y")

    custom_lines = [Line2D([0], [0], color=cm(0), lw=4),
                    Line2D([0], [0], color=cm(.5), lw=4),
                    Line2D([0], [0], color=cm(1.), lw=4)]
    ax2.legend(custom_lines, ["No curtailment in zone","Partial curtailment in zone", "Full stop in zone"], loc=2)

    fig.autofmt_xdate()
    fig.set_size_inches(15, 8)
    plt.xticks(rotation=-45)
    plt.title("Demand, Generation for all of Orkney. \nCurtailments in " + ", ".join(zone_names))
    plt.savefig("./static/graphs/"+file_name, orientation='landscape')

    return file_name

def buildWeatherGraph(start_limit=0, stop_limit=0, zones=0):
    file_name = "weather-" + makeFileName(start_limit, stop_limit, zones)

    if start_limit != 0: start_limit = datetime.strptime(start_limit, '%Y-%m-%d').timestamp()
    if stop_limit != 0: stop_limit = datetime.strptime(stop_limit, '%Y-%m-%d').timestamp()

    sse_df = getData.getDataFrame(start_limit, stop_limit)
    w_df = getData.getWeatherDataFrame(start_limit, stop_limit)

    fig, ax1 = plt.subplots()
    ax1.plot(sse_df.index, sse_df["Generation"],"k-", linewidth=1, alpha=0.8)
    ax1.set_xlabel("Time")
    ax1.margins(x=0)
    ax1.set_ylabel("MegaWatt")
    ax1.legend(["Generation"], loc=1)

    ax2 = ax1.twinx()
    ax2.plot(w_df.index, w_df["speed"],"b--", linewidth=1, alpha=0.8)
    ax2.set_ylabel("Windspeed")
    ax2.legend(["Windspeed in $M/S$"], loc=2)

    fig.autofmt_xdate()
    fig.set_size_inches(15, 8)
    plt.xticks(rotation=45)
    plt.title("Windspeeds near Eday")
    plt.savefig("./static/graphs/"+file_name, orientation='landscape')

    return file_name
