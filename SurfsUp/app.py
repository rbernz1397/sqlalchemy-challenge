# Import the dependencies.
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup

engine = create_engine('sqlite:///Resources/hawaii.sqlite')

#################################################
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
Measurements = Base.classes.measurements
Stations = Base.classes.stations

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup

app = Flask(__name__)

#################################################
# Flask Routes


@app.route("/")
def welcome():
    return (
        '''
        Welcome to the Climate Analysis API!
        Available Routes:
        /api/v1.0/precipitation
        /api/v1.0/stations
        /api/v1.0/tobs
        /api/v1.0/temp/start
        /api/v1.0/temp/start/end
        '''
        );


# list of stations
@app.route("/api/v1.0/stations")
def stations():
    
    results = session.query(Stations.station).all()

    return jsonify(results);

# dates and precipitation observations from the last year in the dataset
@app.route("/api/v1.0/precipitation")
def precipitation():
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   precipitation = session.query(Measurements.date, Measurements.prcp).filter(Measurements.date >= prev_year).all()
   precip = {date: prcp for date, prcp in precipitation}

   return jsonify(precip);

# json list of Temperature Observations (tobs) for the last year of data
@app.route('/api/v1.0/tobs')
def tobs():
   last_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first()
   last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   tobs_data = session.query(Measurements.date, Measurements.tobs).filter(Measurements.date>=last_year).order_by(Measurements.date).all()

   return jsonify(tobs_data);

# json list of the min temp, avg temp, max temp where date = given start<=
@app.route("/api/v1.0/<start>")
def calc_temps(start):
    start_date = dt.datetime.strptime(start,"%Y-%m-%d")
    query_data = session.query(func.min(Measurements.tobs),func.max(Measurements.tobs),func.round(func.avg(Measurements.tobs))).filter(Measurements.date >= start_date).all()

    result = list(np.ravel(query_data))

    return jsonify(result);

# json list: min temp, avg temp, max temp for dates between start/end inclusive
@app.route("/api/v1.0/<start>/<end>")
def calc_temps2(start,end):
    start_date = dt.datetime.strptime(start,"%Y-%m-%d")
    end_date = dt.datetime.strptime(end,"%Y-%m-%d")
    query_data = session.query(func.min(Measurements.tobs),func.max(Measurements.tobs),func.round(func.avg(Measurements.tobs))).filter(Measurements.date.between(start_date,end_date)).all()
    
    result = list(np.ravel(query_data))

    return jsonify(result);  

# ----------------------------------------------------------------------
# Step 4: Define main
# ---------------------------------------------------------------------- 
if __name__ == "__main__":
    app.run(debug=False)
                
#################################################
