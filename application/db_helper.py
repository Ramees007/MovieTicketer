from application.database import db
from application.model import User,Venue, Show, Screen, Tag, TagsShow, Rating, Timeslot, ScreenTimeSlot, ShowTimeslotData, Booking
from sqlalchemy import and_, func
from datetime import date, timedelta
import collections


def get_user(username, password = None):
	if password:
		return User.query.filter(and_(User.user_name == username, User.password == password, User.type == 2)).first()
	return User.query.filter(and_(User.user_name == username, User.type == 2)).first()

def get_admin(username, password = None):
	if password:
		return User.query.filter(and_(User.user_name == username, User.password == password, User.type == 1)).first()
	return User.query.filter(and_(User.user_name == username, User.type == 1)).first()

def create_user(username, password):
	user = User(username, password, 2)
	db.session.add(user)
	db.session.commit()
	return user

def create_admin(username, password):
	user = User(username, password, 1)
	db.session.add(user)
	db.session.commit()
	return user

def create_venue(name, place, location, capacity):
	venue = Venue(name, place, location, capacity)
	db.session.add(venue)
	db.session.commit()
	return venue

def get_all_venues():
	return Venue.query.all()

def save_show(venue_id, show_name, rating, start_time, end_time, tags, price, user_id):
	try:
		show = Show.query.filter(Show.name == show_name).first()
		if show is None:
			show = Show(show_name)
			db.session.add(show)
			db.session.flush()
		screen = Screen.query.filter(and_(Screen.show_id == show.id, Screen.venue_id == venue_id)).first()
		if screen is None:
			screen = Screen(venue_id, show.id)
			db.session.add(screen)
		TagsShow.query.filter(TagsShow.show_id == show.id).delete()
		tag_list = tags.split(',')
		for tag in tag_list:
			tag_obj = get_tag(tag.strip())
			if tag_obj is None:
				tag_obj = Tag(tag.strip())
				db.session.add(tag_obj)
				db.session.flush()
			tag_show = TagsShow(tag_obj.id, show.id)
			db.session.add(tag_show)
		ts = Timeslot.query.filter(and_(Timeslot.start_time == start_time, Timeslot.end_time == end_time)).first()
		if ts is None:
			ts = Timeslot(start_time, end_time)
			db.session.add(ts)
			db.session.flush()
		screen_ts = ScreenTimeSlot.query.filter(and_(ScreenTimeSlot.screen_id == Screen.id, ScreenTimeSlot.timeslot_id == ts.id)).first()
		if screen_ts is None:
			screen_ts = ScreenTimeSlot(screen.id, ts.id, price)
			db.session.add(screen_ts)
		else:
			screen_ts.price = price
		Rating.query.filter(and_(Rating.user_id == user_id, Rating.show_id == show.id)).delete()
		rating = Rating(show.id, user_id, rating)
		db.session.add(rating)
		db.session.commit()
		return show
	except Exception as e:
		print(e)
		db.session.rollback()
	return None

def get_venues_shows():
	q = db.session.query(Venue, Show).join(Screen, Venue.id == Screen.venue_id , isouter=True).join(Show, Show.id == Screen.show_id, isouter=True)
	result = q.all()
	venues_dict = {}
	for item in result:
		v = item[0]
		if v in venues_dict:
			venues_dict[v].append(item[1])
		else:
			venues_dict[v] = [item[1]]
	return venues_dict

def get_all_venues(show_id):
	q = db.session.query(Venue).join(Screen, and_(Venue.id == Screen.venue_id, Screen.show_id == show_id))
	return q.all()

def get_show(show_id):
	return Show.query.filter(Show.id == show_id).first()

def get_rating(user_id, show_id):
	return Rating.query.filter(and_(Rating.user_id == user_id, Rating.show_id == show_id)).first()

def get_all_timeslots(show_id):
	q = db.session.query(Screen, Timeslot).filter(and_(Timeslot.id == ScreenTimeSlot.timeslot_id, ScreenTimeSlot.screen_id == Screen.id, Screen.show_id == show_id))
	results = q.all()
	screen_ts = {}
	for result in results:
		screen = result[0]
		if screen in screen_ts:
			screen_ts[screen].append(result[1])
		else:
			screen_ts[screen] = [result[1]]

	return screen_ts

def get_timeslot(id):
	return Timeslot.query.filter(Timeslot.id == id).first()

def get_tags(show_id):
	q = Tag.query.filter(and_(Tag.id == TagsShow.tag_id, TagsShow.show_id == show_id ))
	return q.all()

def get_tag(name):
	return Tag.query.filter(Tag.name == name).first()

def get_price(venue_id, show_id, slot_id):
	q = db.session.query(ScreenTimeSlot).join(Screen, and_(ScreenTimeSlot.screen_id == Screen.id, Screen.venue_id == venue_id, Screen.show_id == show_id, ScreenTimeSlot.timeslot_id == slot_id))
	print(q)
	screen_ts = q.one()
	return screen_ts.price

def update_show(venue_id, show_id, rating, start_time, end_time, tags, price, user_id, timeslot_id):
	try:
		TagsShow.query.filter(TagsShow.show_id == show_id).delete()
		tag_list = tags.split(',')
		for tag in tag_list:
			tag_obj = get_tag(tag.strip())
			if tag_obj is None:
				tag_obj = Tag(tag.strip())
				db.session.add(tag_obj)
				db.session.flush()
			tag_show = TagsShow(tag_obj.id, show_id)
			db.session.add(tag_show)
		screen = Screen.query.filter(and_(Screen.venue_id == venue_id, Screen.show_id == show_id)).first()
		ScreenTimeSlot.query.filter(and_(ScreenTimeSlot.timeslot_id == timeslot_id, ScreenTimeSlot.screen_id == screen.id)).delete()
		ts = Timeslot.query.filter(and_(Timeslot.start_time == start_time, Timeslot.end_time == end_time)).first()
		if ts is None:
			ts = Timeslot(start_time, end_time)
			db.session.add(ts)
			db.session.flush()
		screen_ts = ScreenTimeSlot(screen.id, ts.id, price)
		db.session.add(screen_ts)
		Rating.query.filter(and_(Rating.user_id == user_id, Rating.show_id == show_id)).delete()
		rating = Rating(show_id, user_id, rating)
		db.session.add(rating)
		db.session.commit()
		return True
	except Exception as e:
		print(e)
		db.session.rollback()
	return False

def delete_screen_timeslot(venue_id, show_id,timeslot_id):
	try:
		q = ScreenTimeSlot.query.filter(and_(ScreenTimeSlot.timeslot_id == timeslot_id, ScreenTimeSlot.screen_id == Screen.id, Screen.venue_id == venue_id, Screen.show_id == show_id))
		res = q.all()
		for i in res:
			db.session.delete(i)

		screen_q = ScreenTimeSlot.query.filter(and_(ScreenTimeSlot.screen_id == Screen.id, Screen.venue_id == venue_id, Screen.show_id == show_id))
		screen_res = screen_q.all()
		if not screen_res:
			screen = Screen.query.filter(and_(Screen.venue_id == venue_id, Screen.show_id == show_id)).first()
			db.session.delete(screen)
	except Exception as e:
		print(e)
		db.session.rollback()
		return False
	else:
		db.session.commit()
		return True

def delete_show_completely(show_id):
	try:
		Rating.query.filter(Rating.show_id == show_id).delete()
		TagsShow.query.filter(TagsShow.show_id == show_id).delete()
		screens = Screen.query.filter(Screen.show_id == show_id).all()
		for s in screens:
			ScreenTimeSlot.query.filter(ScreenTimeSlot.screen_id == s.id).delete()
		Screen.query.filter(Screen.show_id == show_id).delete()
		Show.query.filter(Show.id == show_id).delete()
	except Exception as e:
		print(e)
		db.session.rollback()
		return False
	db.session.commit()
	return True

def delete_venue_completely(venue_id):
	try:
		screens = Screen.query.filter(Screen.venue_id == venue_id).all()
		for s in screens:
			ScreenTimeSlot.query.filter(ScreenTimeSlot.screen_id == s.id).delete()
		Screen.query.filter(Screen.venue_id == venue_id).delete()
		Venue.query.filter(Venue.id == venue_id).delete()
	except Exception as e:
		print(e)
		db.session.rollback()
		return False
	db.session.commit()
	return True

def get_venue(venue_id):
	return Venue.query.filter(Venue.id == venue_id).first()

def update_venue(venue):
	try:
		db.session.add(venue)
		db.session.commit()
	except Exception as e:
		db.session.rollback()
		return False
	else:
		return True
	finally:
		pass
	
	

def get_all_shows(venue_id):
	q = db.session.query(Show).join(Screen, and_(Show.id == Screen.show_id, Screen.venue_id == venue_id))
	return q.all()

def get_all_timeslots_for_venue(venue_id):
	q = db.session.query(Screen, Timeslot).filter(and_(Timeslot.id == ScreenTimeSlot.timeslot_id, ScreenTimeSlot.screen_id == Screen.id, Screen.venue_id == venue_id))
	results = q.all()
	screen_ts = {}
	for result in results:
		screen = result[0]
		if screen in screen_ts:
			screen_ts[screen].append(result[1])
		else:
			screen_ts[screen] = [result[1]]

	return screen_ts

def get_venues_shows_with_ts():
	q = db.session.query(Venue, Show).join(Screen, Venue.id == Screen.venue_id , isouter=True).join(Show, Show.id == Screen.show_id, isouter=True)
	result = q.all()
	ts_q = db.session.query(Screen, Timeslot, ScreenTimeSlot).filter(and_(Timeslot.id == ScreenTimeSlot.timeslot_id, ScreenTimeSlot.screen_id == Screen.id))
	bookings = Booking.query.filter(func.DATE(Booking.booked_time) == date.today()).all()
	screen_ts = ts_q.all()
	venues_dict = {}
	for item in result:
		v = item[0]
		s = item[1]
		if v is None or s is None:
			continue
		show_ts_list = get_show_timeslot_data(v, s, screen_ts, bookings)
		if v in venues_dict:
			venues_dict[v].extend(show_ts_list)
		else:
			venues_dict[v] = show_ts_list
	return venues_dict 

def get_show_timeslot_data(venue, show, screen_ts, bookings):
	show_ts_list = []
	for item in screen_ts:
		s = item[0]
		ts = item[1]
		s_ts = item[2]
		booked_seats = 0
		for booking in bookings:
			if booking.screen_ts_id == s_ts.id:
				booked_seats += booking.seats
			
		if s is None or ts is None:
			continue
		if s.show_id == show.id and s.venue_id == venue.id:
			show_ts_list.append(ShowTimeslotData(show, ts, booked_seats < venue.capacity))
	return show_ts_list

def get_timeslot(timeslot_id):
	return Timeslot.query.filter(Timeslot.id == timeslot_id).first()

def get_available_seats_and_price(venue, show_id, timeslot_id):
	total = venue.capacity
	screen_ts = ScreenTimeSlot.query.filter(and_(ScreenTimeSlot.screen_id == Screen.id, 
	                                   ScreenTimeSlot.timeslot_id == timeslot_id, Screen.show_id == show_id, Screen.venue_id == venue.id)).first()
	booked = Booking.query.filter(and_(Booking.screen_ts_id == screen_ts.id, func.DATE(Booking.booked_time) == date.today())).all()
	booked_count = 0
	for b in booked:
		booked_count+=b.seats

	available = total - booked_count
		
	print('Available count ', available)
	return available, screen_ts.price

def book_n_save_ticket(venue, show_id, timeslot_id, ticket_count, user_id):
	try:
		(available_seats, price) = get_available_seats_and_price(venue, show_id, timeslot_id)
		if available_seats <  int(ticket_count):
			return False
		screen_ts = ScreenTimeSlot.query.filter(and_(ScreenTimeSlot.screen_id == Screen.id, 
	                                   ScreenTimeSlot.timeslot_id == timeslot_id, Screen.show_id == show_id, Screen.venue_id == venue.id)).first()
		booking = Booking(screen_ts.id, user_id, ticket_count, price)
		db.session.add(booking)
	except Exception as e:
		print(e)
		db.session.rollback()
		return False
	else:
		db.session.commit()
		return True
	
def get_bookings(user_id):
	q = db.session.query(Booking, Show, Venue, Timeslot).filter(and_(Booking.user_id == user_id, Booking.screen_ts_id == ScreenTimeSlot.id,
	                                                          ScreenTimeSlot.id == Timeslot.id, ScreenTimeSlot.screen_id == Screen.id,
	                                                          Screen.show_id == Show.id, Screen.venue_id == Venue.id))
	return q.all()

def save_rating(rating_value, show_id, user_id):
	rating = Rating.query.filter(and_(Rating.user_id == user_id, Rating.show_id == show_id)).first()
	if rating is None:
		rating = Rating(show_id, user_id, rating_value)
		db.session.add(rating)
	else:
		rating.value = rating_value
	db.session.commit()

def get_shows_revenue(location):
	results = []
	start_date = date.today() - timedelta(7)
	q = db.session.query(Booking, Show).filter(and_(Booking.screen_ts_id == ScreenTimeSlot.id, ScreenTimeSlot.screen_id == Screen.id, 
		                                                Screen.venue_id == Venue.id, Screen.show_id == Show.id, 
		                                                func.DATE(Booking.booked_time) >= start_date, func.DATE(Booking.booked_time) < date.today()))
	if location != 'all_locations':
		q = q.filter(Venue.location == location)
	results = q.all()
	show_date_dict = {}
	for res in results:
		booking = res[0]
		show = res[1]
		if booking is None or show is None:
			continue
		booked_date = booking.booked_time.date()
		if show in show_date_dict:
			if booked_date in show_date_dict[show]:
				show_date_dict[show][booked_date] = show_date_dict[show][booked_date] + (booking.seats * booking.price)
			else:
				show_date_dict[show][booked_date] = (booking.seats * booking.price)
		else:
			date_rev_dict = {booked_date: (booking.seats * booking.price)}
			show_date_dict[show] = date_rev_dict
	print(show_date_dict)

	start_date = date.today() - timedelta(7)
	for show in show_date_dict:
		for single_date in (start_date + timedelta(n) for n in range(7)):
			if single_date not in show_date_dict[show]:
				show_date_dict[show][single_date] = 0

	for s in show_date_dict:
		show_date_dict[s] = collections.OrderedDict(sorted(show_date_dict[s].items()))

	return show_date_dict

def get_all_locations():
	query = db.session.query(Venue.location.distinct().label("location"))
	locations = [row.location for row in query.all()]
	return locations

def get_all_tags():
	tags = Tag.query.all()
	return tags

def get_shows(q , tag_id, rating_above):
	query = db.session.query(Show)
	if q:
		query = query.filter(Show.name.contains(q))
	if tag_id and tag_id != 'all_tags':
		query = query.filter(and_(Show.id == TagsShow.show_id, TagsShow.tag_id == tag_id))
	if rating_above and rating_above != 'all_ratings':
		rating_avg_subq = db.session.query(func.avg(Rating.value).label('average'), Rating.show_id).group_by(Rating.show_id).subquery()
		query = query.join(rating_avg_subq, and_(rating_avg_subq.c.average > float(rating_above), rating_avg_subq.c.show_id == Show.id))
	return query.all()

def get_venues(q, location):
	query = db.session.query(Venue)
	if q:
		query = query.filter(Venue.name.contains(q))
	if location and location != 'all_locations':
		query = query.filter(Venue.location == location)
	return query.all()



















	

	



			