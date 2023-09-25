from application.database import db
from sqlalchemy import func

class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	user_name = db.Column(db.String, unique = True, nullable = False)
	password = db.Column(db.String, nullable = False)
	type = db.Column(db.Integer, nullable = False)

	def __init__(self, user_name, password, type):
		self.user_name = user_name
		self.password = password
		self.type = type

class Venue(db.Model):
	__tablename__ = 'venue'
	id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	name = db.Column(db.String, nullable = False)
	place = db.Column(db.String, nullable = False)
	location = db.Column(db.String, nullable = False)
	capacity = db.Column(db.Integer, nullable = False)
	__table_args__ = (db.UniqueConstraint('name', 'location'), )

	def __init__(self, name, place, location, capacity):
		self.name = name
		self.place = place
		self.location = location
		self.capacity = capacity

class Show(db.Model):
	__tablename__ = 'show'
	id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	name = db.Column(db.String, unique = True, nullable = False)

	def __init__(self, name):
		self.name = name

class Screen(db.Model):
	__tablename__ = 'screen'
	id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable= False)
	show_id = db.Column(db.Integer, db.ForeignKey('show.id'),  nullable= False)

	def __init__(self, venue_id, show_id):
		self.venue_id = venue_id
		self.show_id = show_id

class Tag(db.Model):
	__tablename__ = 'tag'
	id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	name = db.Column(db.String, unique = True, nullable = False)

	def __init__(self, name):
		self.name = name

class TagsShow(db.Model):
	__tablename__ = 'tags_show'
	id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable= False)
	show_id = db.Column(db.Integer, db.ForeignKey('show.id'),  nullable= False)

	def __init__(self, tag_id, show_id):
		self.tag_id = tag_id
		self.show_id = show_id

class Rating(db.Model):
	__tablename__ = 'rating'
	id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	show_id = db.Column(db.Integer, db.ForeignKey('show.id'),  nullable= False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'),  nullable= False)
	value = db.Column(db.DECIMAL(1,1),   nullable= False)

	def __init__(self, show_id, user_id, value):
		self.show_id = show_id
		self.user_id = user_id
		self.value = value


class Timeslot(db.Model):
	__tablename__ = 'timeslot'
	id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	start_time = db.Column(db.String,  nullable= False)
	end_time = db.Column(db.String,  nullable= False)
	def __init__(self, start_time, end_time):
		self.start_time = start_time
		self.end_time = end_time

class ScreenTimeSlot(db.Model):
	__tablename__ = 'screen_timeslot'
	id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	screen_id = db.Column(db.Integer, db.ForeignKey('screen.id'),  nullable= False)
	timeslot_id = db.Column(db.Integer, db.ForeignKey('timeslot.id'),  nullable= False)
	price = db.Column(db.Integer, nullable= False)
	def __init__(self, screen_id, timeslot_id, price):
		self.screen_id = screen_id
		self.timeslot_id = timeslot_id
		self.price = price

class Booking(db.Model):
	__tablename__ = 'booking'
	id = db.Column(db.Integer, autoincrement = True, primary_key = True)
	screen_ts_id = db.Column(db.Integer, db.ForeignKey('screen_timeslot.id'),  nullable= False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'),  nullable= False)
	seats = db.Column(db.Integer, nullable= False)
	price = db.Column(db.Integer, nullable= False)
	booked_time = db.Column(db.DateTime(timezone=True), server_default=func.now())

	def __init__(self, screen_ts_id, user_id, seats, price):
		self.screen_ts_id = screen_ts_id
		self.user_id = user_id
		self.seats = seats
		self.price = price
		self.booked_time = func.now()

class ShowTimeslotData():

	def __init__(self, show, timeslot, is_open):
		self.show = show
		self.timeslot = timeslot
		self.is_open = is_open

	def set_timeslot(timeslot):
		self.timeslot = timeslot













