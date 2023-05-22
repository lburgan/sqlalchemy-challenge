# Import the dependencies.

import pandas as pd
import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func, desc
from flask import Flask,jsonify

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    #welcome page with api links 
    return(
        f"Welcome to the Hawaii Weather API!<br/>"
        f"Available Routes:<br/>"
        f"Dates and Precipitation from the most current year: /api/v1.0/precipitation<br/>"
        f"Information on Stations: /api/v1.0/stations<br/>"
        f"Dates and Temps. from Most Active Station for most current year: /api/v1.0/tobs<br/>"
        f"Temp min/avg/max from a start date to today (format YYYY-MM-DD): /api/v1.0/start<br/>"
        f"Temp min/avg/max from a start date to an end date, inclusive (format YYYY-MM-DD): /api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    #start session
    session = Session(engine)

    #get dt of most recent year
    recent_date = dt.date(2017,8,23)
    year_ago = dt.date(recent_date.year - 1,recent_date.month,recent_date.day)

    #get prcp data, then close session
    data = [measurement.date,measurement.prcp]
    year_results = session.query(*data).filter(measurement.date >= year_ago).all()
    session.close()

    #turn results into a pretty dictionary and return
    all_prcp = []
    for date, rain in year_results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Prcp"] = rain
        all_prcp.append(prcp_dict)
    return(jsonify(all_prcp))


@app.route("/api/v1.0/stations")
def stations():
    #start session
    session = Session(engine)

    #get station data, then close session
    data = [station.station, station.name,station.latitude,station.longitude, station.elevation]
    results = session.query(*data).all()
    session.close()

    #turn results into a pretty dictionary and return
    all_stats = []
    for stat,name,lat,lon,elv in results:
        stats_dict = {}
        stats_dict["Station"] = stat
        stats_dict["Name"] = name
        stats_dict["Latitude"] = lat
        stats_dict["Longitude"] = lon
        stats_dict["Elevation"] = elv
        all_stats.append(stats_dict)
    return(jsonify(all_stats))


@app.route("/api/v1.0/tobs")
def tobs():
    #start session
    session = Session(engine)

    #get most recent year
    recent_date = dt.date(2017,8,23)
    year_ago = dt.date(recent_date.year - 1,recent_date.month,recent_date.day)

    #get temp data, then close session
    tobs = [measurement.date,measurement.tobs]
    results = session.query(*tobs).filter(measurement.date >= year_ago).\
    filter(measurement.station == "USC00519281").all()
    session.close()

    #turn results into a pretty dictionary and return
    all_tobs = []
    for date, temp in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temp"] = temp
        all_tobs.append(tobs_dict)
    return(jsonify(all_tobs))

#########################################
# Dynamic Routes
#########################################
@app.route("/api/v1.0/<start>/<end>")
@app.route("/api/v1.0/<start>")
def temps(start = None, end = None):
    #start session
    session = Session(engine)

    #check if the user input an end date. If not, run code for only start date route
    if not end:
      #find data from start date to recent, then close session
      data = [func.min(measurement.tobs),func.avg(measurement.tobs), func.max(measurement.tobs)]
      results = session.query(*data).filter(measurement.date >= start).all()
      session.close()

    #turn results into a pretty dictionary and return
      for list in results:
          temp_results = {"Min" : list[0], "Avg" :list[1], "Max": list[2]}
      return(jsonify(temp_results))
    
    #Else, if end date is provided, run code for that route
    else:
       #find data from start date to end date
       data = [func.min(measurement.tobs),func.avg(measurement.tobs), func.max(measurement.tobs)]
       results = session.query(*data).filter(measurement.date >= start).filter(measurement.date <= end).all()
       session.close()

    #turn results into a pretty dictionary and return
       for list in results:
          temp_results = {"Min" : list[0], "Avg" :list[1], "Max": list[2]}
       return(jsonify(temp_results)) 
    
#Finally, run the app! 

if __name__ == '__main__':
    app.run(debug=True)