import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.station

from flask import Flask, jsonify

session = Session(engine)

#Create the app
app = Flask(__name__) 

#List all routes
@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

#Retrieve Data in JSON format
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= "2016-08-23").all()

    session.close()

    precipitation_list = []
    PrecipitationbyDate = {}

    for x in results:
        PrecipitationbyDate[x[0]] = x[1]
        print(x[0])

    return jsonify(PrecipitationbyDate)

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    #Get the data in JSON format

    stations = session.query(
        Station.station,
        Station.name,
        Station.longitude,
        Station.latitude,
        Station.elevation
    ).all()

    session.close()

    list_of_stations = list(np.ravel(stations))
    return jsonify(list_of_stations)

@app.route("/api/v1.0/tobs")
def tobs():
  
    session = Session(engine)

    #JSON list of temperature observations for the previous year (TOBS)#

    most_activations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc())[0][0]
    
    tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date > "2016-08-23").\
        filter(Measurement.tobs).\
        order_by(Measurement.date).all()

    session.close()
    
    result_list = []  

    for date in tobs:
        result = {
            "date": date,
            "tobs": tobs
        }

    result_list.append(result)
    
    return jsonify(result_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start(start = None, end = None):

    session = Session(engine)

    if not end:

        query_result = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                            filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).all()

        result_list = []

        for min, max, avg in query_result:
            result = {
                "TMIN": min,
                "TMAX": max,
                "TAVG": avg   
            }

            result.append(result)
        
        return jsonify(result)

    query_result = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                        filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).\
                        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).all()
    
    session.close()

    result_list = []

    for min, max, avg in query_result:
        result = {
            "TMIN": min,
            "TMAX": max,
            "TAVG": avg   
        }

        result_list.append(result)
    
    return jsonify(result_list)

if __name__ == "__main__":
    app.run(host = '127.0.0.1',port = 8083,debug = True)