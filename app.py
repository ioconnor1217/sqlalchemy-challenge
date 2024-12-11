# Import the dependencies.
from flask import Flask, jsonify

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

# Create our session (link) from Python to the DB


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
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()
    precipitation = {date: prcp for date, prcp in data}
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.station).all()
    session.close()
    return jsonify([station[0] for station in stations])

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    data = session.query(Measurement.tobs).filter(
        Measurement.station == 'USC00519281',
        Measurement.date >= one_year_ago
    ).all()
    session.close()
    return jsonify([temp[0] for temp in data])

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if end:
        stats = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        stats = session.query(*sel).filter(Measurement.date >= start).all()
    session.close()
    return jsonify({"min": stats[0][0], "avg": stats[0][1], "max": stats[0][2]})

if __name__ == "__main__":
    app.run(debug=True)