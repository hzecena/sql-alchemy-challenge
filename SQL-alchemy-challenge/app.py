# IMPORT DEPENDENCIES
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# SET UP THE DB
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# REFLECT DB
Base = automap_base()

# REFLECT TABLES
Base.prepare(engine, reflect=True)

# TABLE REFERENCE
M = Base.classes.measurement
S = Base.classes.station

# SET UP FLASK
app = Flask(__name__)

# ASSIGN FLASK ROUTES 
# List all routes that are available.
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to the Home Page!<br/><br/>"
        f"AVAILABLE ROUTES: <br/><br/>"
        f"List of Precipitation Totals:<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"List of Stations:<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"List of Temperature Observations:<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Enter a Start Date [yyyymmdd] for MAX, AVG, MIN Temperature:<br/>"
        f"/api/v1.0/<start><br/><br/>"
        f"Enter a Start and End Date [yyyymmdd/yyyymmdd] for MAX, AVG, MIN Temperature:<br/>"
        f"/api/v1.0/<start>/<end>"
           )

# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")

    session = Session(engine)
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(M.date, M.prcp).filter(M.date >= query_date).all()
    session.close()

    prcp_li = []
    for date, prcp in results:
            prcp_dict = {}
            prcp_dict["Date"] = date
            prcp_dict["Precipitation"] = prcp
            prcp_li.append(prcp_dict)
            
    return jsonify(prcp_li)

@app.route("/api/v1.0/stations")
# Return a JSON list of stations from the dataset.
def stations():
    print("Server received request for 'Stations' page...")

    session = Session(engine)
    results = session.query(S.station).all()
    session.close()
    
    stations_li = list(np.ravel(results))

    return jsonify(stations_li)
            
@app.route("/api/v1.0/tobs")
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
def tobs():
    print("Server received request for 'Temp Observations' page...")

    session = Session(engine)
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(M.tobs).filter(M.station == "USC00519281").filter(M.date >= query_date).all()
    session.close()
    
    active_station = list(np.ravel(results))

    return jsonify(active_station)

# # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>") 
def date_picker(start):
    session = Session(engine)
    
    year=int(start[:4])
    month=int(start[4:6])
    day=int(start[6:])

    print(year, month, day)
    
    start_date = dt.date(year, month, day)
    
    results = session.query(func.min(M.tobs),func.avg(M.tobs),func.max(M.tobs)).filter(M.date == start_date).all()
    session.close()

    start_li = []
    
    for TMIN, TAVG, TMAX in results:
            start_dict = {}
            start_dict["a. Date"] = start_date
            start_dict["b. Min Precipitation"] = TMIN
            start_dict["c. Ave Precipitation"] = TAVG
            start_dict["d. Max Precipitation"] = TMAX
            start_li.append(start_dict)
            
    return jsonify(start_li)

@app.route("/api/v1.0/<start>/<end>") #20160102/20171220
def date_picker2(start,end):
    session = Session(engine)
    
    s_year=int(start[:4])
    s_month=int(start[4:6])
    s_day=int(start[6:])

    e_year=int(end[:4])
    e_month=int(end[4:6])
    e_day=int(end[6:])
    
    print(s_year, s_month, s_day, e_year, e_month, e_day)
    
    start_date = dt.date(s_year, s_month, s_day)
    end_date = dt.date(e_year, e_month, e_day)
    
    results = session.query(func.min(M.tobs),func.avg(M.tobs),func.max(M.tobs)).filter(M.date >= start_date).filter(M.date <= end_date).all()
    
    session.close()

    range_li = []

    for e_TMIN, e_TAVG, e_TMAX in results:
            range_dict = {}
            range_dict["a. Starting Date"] = start_date
            range_dict["b. Ending Date"] = end_date
            range_dict["c. Min Precipitation"] = e_TMIN
            range_dict["d. Ave Precipitation"] = e_TAVG
            range_dict["e. Max Precipitation"] = e_TMAX
            range_li.append(range_dict)
            
    return jsonify(range_li)

if __name__ == "__main__":
    app.run(debug=True)