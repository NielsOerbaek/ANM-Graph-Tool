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

    if stop_limit - start_limit > 172800: tick_zoom = 6
    elif stop_limit - start_limit > 86400: tick_zoom = 3
    else: tick_zoom = 1

    df = getData.getDataFrame(start_limit, stop_limit)

    if zones != 0: zone_names = zones

    # Generate x,y data for the mesh plot
    curtailments = np.zeros(shape=(len(zone_names),len(df.index)))
    for i, zone in enumerate(zone_names):
        for j, status in enumerate(df[zone+": Curtailed"] + df[zone+": Full Stop"]):
            curtailments[i,j] = status

    curtailments = curtailments[:,:-1]

    # Generate x ticks for the mesh plot
    meshxticks_major = []
    meshxticks_minor = []
    for i,d in enumerate(df.index):
        if d.hour == 0 and d.minute == 0: meshxticks_major.append(i)
        elif d.hour % tick_zoom == 0 and d.minute == 0: meshxticks_minor.append(i)


    fig = plt.figure()
    # Bottom plot
    ax1 = fig.add_axes([0.08,0.1,0.9,0.39])
    delta = (df["Generation"]-df["Demand"])#.rolling(3).mean()
    ax1.plot(df.index, delta,"k-", linewidth=1, alpha=0.8)
    plt.fill_between(df.index, delta, color="k", alpha=0.3)
    ax1.set_xlabel("Time")
    ax1.margins(x=0)
    ax1.set_ylabel("MegaWatt")
    ax1.set_ylim(-25, 25)
    ax1.set_yticks([-25,-20,-15,-10,-5,0,5,10,15,20,25])
    ax1.grid(b=True, which="both", axis="y")
    ax1.xaxis.set_major_locator(mdates.DayLocator())
    ax1.xaxis.set_minor_locator(mdates.HourLocator(interval=tick_zoom))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax1.xaxis.set_minor_formatter(mdates.DateFormatter("%H:00"))
    for i,t in enumerate(ax1.xaxis.get_minor_ticks()):
        if i % (24 / tick_zoom) == 0: t.label.set_visible(False)
    ax1.tick_params(axis="x", which="minor")
    ax1.grid(b=True, which="major", axis="x", linestyle="-.")
    ax1.grid(b=True, which="minor", axis="x", linestyle="--")
    ax1.legend(["Generation relative to Demand"], loc=1, fancybox=True, framealpha=0.5)

    # Top plot
    cm = plt.get_cmap("OrRd")
    ax2 = fig.add_axes([0.08,0.51,0.9,0.4])
    ax2.pcolormesh(curtailments, alpha=1, cmap=cm, snap=True)
    ax2.set_xticks(meshxticks_major)
    ax2.set_xticks(meshxticks_minor, minor=True)
    ax2.xaxis.set_ticklabels([])
    ax2.grid(b=True, which="major", axis="x", linestyle="-.")
    ax2.grid(b=True, which="minor", axis="x", linestyle="--")
    ax2.set_ylabel("Zones")
    ax2.set_yticks(np.arange(len(zone_names))+0.5)
    ax2.set_yticks(np.arange(len(zone_names)), minor=True)
    ax2.set_yticklabels(zone_names, rotation=0, fontsize="10", va="center")
    ax2.grid(b=True, which="minor", axis="y")
    custom_lines = [Line2D([0], [0], color=cm(0), lw=4),
    Line2D([0], [0], color=cm(.5), lw=4),
    Line2D([0], [0], color=cm(1.), lw=4)]
    ax2.legend(custom_lines, ["No curtailment in zone","Partial curtailment in zone", "Full stop in zone"], loc=1, fancybox=True, framealpha=0.5)
    plt.title("Demand, Generation for all of Orkney. \nCurtailments in " + ", ".join(zone_names))

    fig.autofmt_xdate(which="both")

    fig.set_size_inches(15, 8)
    plt.xticks(rotation=-60)

    plt.savefig("./static/graphs/"+file_name, orientation='landscape')
    #plt.savefig("./static/pgf/"+file_name[:-3]+"pgf", orientation='landscape')
    #plt.show()

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
    ax1.legend(["Generation"], loc=2)

    ax2 = ax1.twinx()
    ax2.plot(w_df.index, w_df["speed"],"b--", linewidth=1, alpha=0.8)
    ax2.set_ylabel("Windspeed")
    ax2.legend(["Windspeed in $M/S$"], loc=1)

    fig.autofmt_xdate()
    fig.set_size_inches(15, 8)
    plt.xticks(rotation=45)
    plt.title("Windspeeds near Eday")
    plt.savefig("./static/graphs/"+file_name, orientation='landscape')

    return file_name
