from flask import Flask, render_template, request, url_for
import os
import pandaPlotter
import getData
import gc

app = Flask(__name__)

def displayGraph(file_name):
    full_filename = os.path.join(os.path.sep, 'static', 'graphs', file_name)
    gc.collect()
    return render_template("graph.html", graph_image = full_filename)


@app.route('/')
def get_index():
    return render_template("index.html")

@app.route('/graph/<start>/<end>/<zones>')
def get_graph_by_start_end_zone(start,end,zones):
    file = pandaPlotter.buildGraph(start,end,zones.split(","))
    return displayGraph(file)

@app.route('/graph/<start>/<end>')
def get_graph_by_start_end(start,end):
    file = pandaPlotter.buildGraph(start,end)
    return displayGraph(file)

@app.route('/graph/<start>')
def get_graph_by_start(start):
    file = pandaPlotter.buildGraph(start)
    return displayGraph(file)

@app.route('/delta/<start>/<end>/<zones>')
def get_delta_by_start_end_zone(start,end,zones):
    file = pandaPlotter.buildDeltaGraph(start,end,zones.split(","))
    return displayGraph(file)

@app.route('/delta/<start>/<end>')
def get_delta_by_start_end(start,end):
    file = pandaPlotter.buildDeltaGraph(start,end)
    return displayGraph(file)

@app.route('/delta/<start>')
def get_delta_by_start(start):
    file = pandaPlotter.buildDeltaGraph(start)
    return displayGraph(file)

@app.route('/deltaZone/<start>/<end>/<zones>')
def get_deltaZone_by_start_end_zone(start,end,zones):
    file = pandaPlotter.buildDeltaZoneGraph(start,end,zones.split(","))
    return displayGraph(file)

@app.route('/deltaZone/<start>/<end>')
def get_deltaZone_by_start_end(start,end):
    file = pandaPlotter.buildDeltaZoneGraph(start,end)
    return displayGraph(file)

@app.route('/deltaZone/<start>')
def get_deltaZone_by_start(start):
    file = pandaPlotter.buildDeltaZoneGraph(start)
    return displayGraph(file)

@app.route('/wind/<start>/<end>')
def get_wind_by_start_end(start,end):
    file = pandaPlotter.buildWeatherGraph(start,end)
    return displayGraph(file)

@app.route('/json/<start>/<end>')
def get_json_by_start_end(start,end):
    start = datetime.strptime(start, '%Y-%m-%d').timestamp()
    stop = datetime.strptime(stop, '%Y-%m-%d').timestamp()
    df = getData.getDataFrame(start,end)
    return df.to_json()
