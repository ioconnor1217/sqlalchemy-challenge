# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

#################################################
# Database Setup
#################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

# Create Flask app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Routes
@app.route("/")
def welcome():
    return (
        f"<h1>Welcome to the Climate API!</h1>"
        f"<h2>Available Routes:</h2>"
        f"/api/v1.0/precipitation - <b>Last 12 months of data</b><br/>"
        f"/api/v1.0/stations - <b>List of all weather stations</b><br/>"
        f"/api/v1.0/tobs - <b>Temperature observations for the most active weather station</b><br/>"
        f"/api/v1.0/&lt;start&gt; - <b>Min, avg, and max temperatures from a chosen start date (YYYY-MM-DD)</b><br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; - <b>Min, avg, and max temperatures for a chosen date range (YYYY-MM-DD)</b><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Calculate the date one year from the last data point
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query for date and precipitation
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()
    # Convert query results to dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Query for station IDs
    results = session.query(Station.station).all()
    session.close()
    # Convert tuples into a list
    station_list = [station[0] for station in results]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query temperature observations for most active station
    results = session.query(Measurement.tobs).filter(
        Measurement.station == 'USC00519281',
        Measurement.date >= one_year_ago
    ).all()
    session.close()
    # Convert tuples into a list
    temperature_data = [temp[0] for temp in results]
    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    session = Session(engine)
    try:
        # Ensure valid date format
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d") if end else None

        sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        
        # Query based on date range
        if end_date:
            results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        else:
            results = session.query(*sel).filter(Measurement.date >= start).all()
        
        session.close()

        # Convert query to dictionary
        temperature_data = {
            "start_date": start,
            "end_date": end or "latest available",
            "min_temperature": results[0][0],
            "avg_temperature": results[0][1],
            "max_temperature": results[0][2],
        }
        return jsonify(temperature_data)

    except ValueError:
        session.close()
        return jsonify({"error": "Invalid date, please use YYYY-MM-DD format"}), 400

if __name__ == "__main__":
    app.run(debug=True)