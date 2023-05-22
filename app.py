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
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)


    recent_date = dt.date(2017,8,23)
    year_ago = dt.date(recent_date.year - 1,recent_date.month,recent_date.day)

    data = [measurement.date,measurement.prcp]
    year_results = session.query(*data).filter(measurement.date >= year_ago).all()
    results = list(np.ravel(year_results))
    session.close()
    return(jsonify(results))

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    data = [station.station, station.name]
    results = session.query(*data).all()
    station_results = list(np.ravel(results))
    session.close()
    return(jsonify(station_results))

@app.route("/api/v1.0/<start>/<end>")
@app.route("/api/v1.0/<start>")
def temps(start = None, end = None):
    session = Session(engine)
    if not end:
      data = [func.min(measurement.tobs),func.avg(measurement.tobs), func.max(measurement.tobs)]
      results = session.query(*data).filter(measurement.date >= start).all()
      temp_results = list(np.ravel(results))
      session.close()
      return(jsonify(temp_results))
    else:
       data = [func.min(measurement.tobs),func.avg(measurement.tobs), func.max(measurement.tobs)]
       results = session.query(*data).filter(measurement.date >= start).filter(measurement.date <= end).all()
       temp_results = list(np.ravel(results))
       session.close()
       return(jsonify(temp_results)) 
    










if __name__ == '__main__':
    app.run(debug=True)