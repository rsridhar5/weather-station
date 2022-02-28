from flask import Flask, render_template, request, url_for, session, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlite3

from datetime import datetime
import json

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TotalData.sqlite3' #temp
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.secret_key = 'temp'

db = SQLAlchemy(application)

# DB Model for the Weather data
class Data(db.Model):
	_id = db.Column("id", db.Integer, primary_key=True)
	date_time = db.Column(db.String, nullable=False)
	avg_temp = db.Column(db.Integer, nullable=False)
	high_temp = db.Column(db.Integer, nullable=False)
	low_temp = db.Column(db.Integer, nullable=False)
	avg_humidity = db.Column(db.Integer, nullable=False)
	high_humidity = db.Column(db.Integer, nullable=False)
	low_humidity = db.Column(db.Integer, nullable=False)
	avg_wind_speed = db.Column(db.Integer, nullable=False)
	high_wind_speed = db.Column(db.Integer, nullable=False)
	low_wind_speed = db.Column(db.Integer, nullable=False)
	std_wind_speed = db.Column(db.Integer, nullable=False)
	wind_direction = db.Column(db.Integer, nullable=False)

	def __init__(self, date_time, avg_temp, high_temp, low_temp, 
				avg_humidity, high_humidity, low_humidity, 
				avg_wind_speed, high_wind_speed, low_wind_speed,
				std_wind_speed, wind_direction):
		self.date_time = date_time
		self.avg_temp = avg_temp
		self.high_temp = high_temp
		self.low_temp = low_temp
		self.avg_humidity = avg_humidity
		self.high_humidity = high_humidity
		self.low_humidity = low_humidity
		self.avg_wind_speed = avg_wind_speed
		self.high_wind_speed = high_wind_speed
		self.low_wind_speed = low_wind_speed
		self.std_wind_speed = std_wind_speed
		self.wind_direction = wind_direction

	def __repr__(self):
		return '<Data %d>' % self._id


def insert_data(d):
	db.session.add(d)
	db.session.commit()


def parse_binary_data(bin_data):
	### TODO Based on data sent ###
	# s = d.decode('ascii')
	D : [Data] = list()

	msg = json.loads(bin_data)
	hex_data = msg['data']

	n = 0
	while n < len(hex_data):
		t = hex_data[n:n+24]
		if len(t) < 24:
			break
		d = dict()
		d['hour'] = int(t[0:2], 16)
		d['avgtemp'] = int(t[2:4], 16)
		d['hightemp'] = int(t[4:6], 16)
		d['lowtemp'] = int(t[6:8], 16)
		d['avghum'] = int(t[8:10], 16)
		d['highhum'] = int(t[10:12], 16)
		d['lowhum'] = int(t[12:14], 16)
		d['avgwind'] = int(t[14:16], 16)
		d['highwind'] = int(t[16:18], 16)
		d['lowwind'] = int(t[18:20], 16)
		d['stddevwind'] = int(t[20:22], 16)
		d['winddir'] = int((int(t[22:24], 16)/256)*360) # Converts angle to 0-360

		s  = str(d['hour'])
		if len(s) == 1:
			s = '0' + s
		date_time = msg['transmit_time'].split()[0] + " " + s + ":00"

		data = Data(date_time, d['avgtemp'], d['hightemp'], d['lowtemp'],
			d['avghum'], d['highhum'], d['lowhum'], d['avgwind'], d['highwind'], d['lowwind'],
			d['stddevwind'], d['winddir'])

		D.append(data)
		n += 24


	# Add Data entries to D
	# depends on how data is formatted...
	return D

# Gets all the data from the database
def get_all(l=None) -> list:
	# Can be overloaded to limit results etc.
	if l:
		return Data.query.limit(l).all()

	# Returns all data from the database
	return Data.query.all()

# Homepage
@application.route("/", methods=['GET'])
def index():
	# Sets up the db if not made
	db.create_all()
	# Loads a sample data into the database
	# load_sample_data()
	totalData = get_all() # Get from database
	return render_template("index.html", data=totalData)

# Endopoint that allows Iridium to send data
@application.route("/_update", methods=['POST', 'PUT'])
def _update():
	data = request.get_data() # get_json()
	if data == None:
		return jsonify(success=False)

	D = parse_binary_data(data) 
	# for multiple data entries in one POST
	for d in D:
		insert_data(d)

	# HTTP 200 Success
	return jsonify(success=True)

if __name__=='__main__':
	db.create_all()
	application.run(debug = True)

