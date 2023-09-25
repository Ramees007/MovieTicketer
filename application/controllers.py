from flask import Flask, request, redirect, url_for, session
from flask import render_template
from flask import current_app as app
from application.controller_utils import *
from application.db_helper import *
from application.model import User,Venue, Show, Screen, Tag, TagsShow, Rating, Timeslot, ScreenTimeSlot, Booking

@app.route("/", methods =["GET"])
def index():
	if is_authenticated():
		return redirect('/user/home')
	return render_template("index.html")

@app.route("/user/auth", methods =["GET", "POST"])
def user_auth():
	if request.method == "GET":
		if is_authenticated():
			return redirect('/user/home')
		return logout()

	username = request.form['username'].strip()
	password = request.form['password'].strip()
	if 'login' in request.form:
		user = get_user(username, password)
		if user is None:
			return redirect(url_for('.error', message = 'Invalid username or password'))
		save_session(user)
		return redirect('/user/home')
	existing = get_user(username)
	if existing:
		return redirect(url_for('.error', message = 'Username already taken'))
	user = create_user(username, password)
	save_session(user)
	return redirect('/user/home')


@app.route("/user/home", methods =["GET"])
@login_required
def home():
	venues_dict = get_venues_shows_with_ts()
	return render_template("home.html", user_name = get_user_name(), venues_data = venues_dict)	

@app.route("/logout", methods =["GET"])
def logout():
	is_admin_user = is_admin()
	clear_session()
	if is_admin_user:
		return redirect(url_for('.admin_auth'))
	return redirect(url_for('.index'))

@app.route("/error", methods =["GET"])
def error():
	message = 'Oops... Something went wrong!!'
	if 'message' in request.args:
		message = request.args['message']
	return render_template("error.html", message = message)	


@app.route("/admin/auth", methods =["GET", "POST"])
def admin_auth():
	if request.method == "GET":
		if is_authenticated(for_admin = True):
			return redirect('/admin/home')
		return render_template('admin_auth.html')

	username = request.form['username'].strip()
	password = request.form['password'].strip()
	if 'login' in request.form:
		admin = get_admin(username, password)
		if admin is None:
			return redirect(url_for('.error', message = 'Invalid username or password for admin'))
		save_session(admin)
		return redirect('/admin/auth')
	existing = get_admin(username)
	if existing:
		return redirect(url_for('.error', message = 'Admin username already taken'))
	admin = create_admin(username, password)
	save_session(admin)
	return redirect('/admin/auth')


@app.route("/admin/home", methods =["GET"])
@admin_login_required
def admin_home():
	venues_dict = get_venues_shows()
	return render_template('admin_home.html', user_name = get_user_name(), venues_data = venues_dict)

@app.route("/admin/add_venue", methods =["GET","POST"])
@admin_login_required
def add_venue():
	if request.method == "GET":
		return render_template('add_venue.html', user_name = get_user_name())
	name = request.form['name'].strip()
	place = request.form['place'].strip()
	location = request.form['location'].strip()
	capacity = request.form['capacity'].strip()
	create_venue(name, place, location, int(capacity))
	return redirect('/admin/home', code = 302)


@app.route("/admin/add_show/<int:venue_id>", methods =["GET","POST"])
@admin_login_required
def add_show(venue_id):
	if request.method == "GET":
		return render_template('add_show.html', venue_id = venue_id, user_name = get_user_name())
	name = request.form['name'].strip()
	rating = request.form['rating'].strip()
	start_time = request.form['start_time'].strip()
	end_time = request.form['end_time'].strip()
	tags = request.form['tags'].strip()
	price = request.form['price'].strip()
	result = save_show(venue_id, name, float(rating), start_time, end_time, tags, int(price), get_user_id())
	if result is None:
		return redirect(url_for('.error', message = 'Something went wrong'))

	return redirect('/admin/home', code = 302)

@app.route("/admin/show_details/<int:show_id>", methods =["GET"])
@admin_login_required
def show_details(show_id):
	venues = get_all_venues(show_id)
	show = get_show(show_id)
	screen_ts = get_all_timeslots(show_id)
	venue_ts = {}
	for v in venues:
		for screen in screen_ts:
			if screen.venue_id == v.id:
				if v.id in venue_ts:
					venue_ts[v.id].append(screen_ts[screen])
				else:
					venue_ts[v.id] = screen_ts[screen]
	return render_template('show_details.html', show = show, venues = venues, venue_ts = venue_ts)

@app.context_processor
def inject_user():
    return dict(user_name = get_user_name())

@app.route("/admin/show/edit", methods =["GET","POST"])
@admin_login_required
def edit_show():
	if not all(key in request.args for key in ("venue_id", "show_id", "timeslot")):
		return render_template(url_for('.error', message = 'Venue id, show id, time slot required to edit show'))
	venue_id = request.args.get('venue_id')
	show_id = request.args.get('show_id')
	timeslot_id = request.args.get('timeslot')
	if request.method == "GET":
		show = get_show(show_id)
		rating = get_rating(get_user_id(), show_id)
		timeslot = get_timeslot(timeslot_id)
		price = get_price(venue_id, show_id, timeslot_id)
		tags = get_tags(show_id)
		tags_name_list = [tag.name for tag in tags]
		tags_str = ",".join(tags_name_list)
		return render_template('edit_show.html', venue_id = venue_id, show = show, rating = rating, timeslot=timeslot, price=price, tags = tags_str)
	rating = request.form['rating'].strip()
	start_time = request.form['start_time'].strip()
	end_time = request.form['end_time'].strip()
	tags = request.form['tags'].strip()
	price = request.form['price'].strip()
	user_id = get_user_id()
	result = update_show(venue_id, show_id, rating, start_time, end_time, tags, price, user_id, timeslot_id)

	if not result:
		return redirect(url_for('.error', message = 'Something went wrong'))

	return redirect('/admin/home', code = 302)

@app.route("/admin/show/remove", methods =["GET"])
@admin_login_required
def remove_show():
	if not all(key in request.args for key in ("venue_id", "show_id", "timeslot")):
		return render_template(url_for('.error', message = 'Venue id, show id, time slot required to edit show'))
	venue_id = request.args.get('venue_id')
	show_id = request.args.get('show_id')
	timeslot_id = request.args.get('timeslot')
	res = delete_screen_timeslot(venue_id, show_id, timeslot_id)
	if res:
		return redirect('/admin/home', code = 302)
	return redirect(url_for('.error', message = 'Something went wrong, failed removing show'))


@app.route("/admin/show/delete/<int:show_id>", methods =["GET"])
@admin_login_required
def delete_show(show_id):
	if delete_show_completely(show_id):
		return redirect('/admin/home', code = 302)
	return redirect(url_for('.error', message = 'Something went wrong, failed deleting show'))


@app.route("/admin/venue/venue_details/<int:venue_id>", methods =["GET"])
@admin_login_required
def venue_details(venue_id):
	shows = get_all_shows(venue_id)
	venue = get_venue(venue_id)
	screen_ts = get_all_timeslots_for_venue(venue_id)
	show_ts = {}
	for s in shows:
		for screen in screen_ts:
			if screen.show_id == s.id:
				if s.id in show_ts:
					show_ts[s.id].append(screen_ts[screen])
				else:
					show_ts[s.id] = screen_ts[screen]
	return render_template('venue_details.html', venue = venue, shows = shows, show_ts=show_ts)

@app.route("/admin/venue/delete/<int:venue_id>", methods =["GET"])
@admin_login_required
def delete_venue(venue_id):
	if delete_venue_completely(venue_id):
		return redirect('/admin/home', code = 302)
	return redirect(url_for('.error', message = 'Something went wrong, failed deleting Venue'))

@app.route("/admin/summary", methods =["GET"])
@admin_login_required
def summary():
	location = None
	locations = get_all_locations()	
	print(request.args)
	if 'locations' in request.args:
		location = request.args.get('locations')
	else:
		location = 'all_locations'
	show_date_dict = get_shows_revenue(location)
	dates = []
	start_date = date.today() - timedelta(7)
	for single_date in (start_date + timedelta(n) for n in range(7)):
		dates.append(single_date)

	return render_template('summary.html', locations = locations, show_date_dict = show_date_dict, user_name = get_user_name(), show_home_in_nav = True,
	 selected_location = location, dates = dates)

@app.route("/book_ticket", methods =["GET","POST"])
@login_required
def book_ticket():
	if not all(key in request.args for key in ("venue_id", "show_id", "timeslot_id")):
		return render_template(url_for('.error', message = 'Venue id, show id, time slot required to book show'))
	venue_id = request.args.get('venue_id')
	show_id = request.args.get('show_id')
	timeslot_id = request.args.get('timeslot_id')
	venue = get_venue(venue_id)
	show = get_show(show_id)
	timeslot = get_timeslot(timeslot_id)
	(available_seats, price) = get_available_seats_and_price(venue, show_id, timeslot_id)
	if request.method == "GET":
		return render_template('book_ticket.html', user_name = get_user_name(), show=show, venue = venue, timeslot = timeslot, 
		                       available_seats = available_seats, ticket_count = 1, price=price)

	ticket_count = request.form.get('tickets')
	total_amount = int(ticket_count) * int(price)
	if available_seats > 0:
		return render_template('booking_confirm.html', user_name = get_user_name(), show=show, venue = venue, timeslot = timeslot, 
		                       available_seats = available_seats, ticket_count = ticket_count, price=price, total_amount = total_amount)
	else:
		return redirect(url_for('.error', message = 'Seats just got filled up, Sorry for the inconvenience'))

@app.route("/book_ticket/confirm", methods =["GET"])
@login_required
def confirm_ticket():
	if not all(key in request.args for key in ("venue_id", "show_id", "timeslot_id", "tickets")):
		return render_template(url_for('.error', message = 'Venue id, show id, time slot & ticket count required to book show'))
	venue_id = request.args.get('venue_id')
	show_id = request.args.get('show_id')
	timeslot_id = request.args.get('timeslot_id')
	tickets = request.args.get('tickets')
	if book_n_save_ticket(get_venue(venue_id), show_id, timeslot_id, tickets, get_user_id()):
		return redirect('/user/home', code = 302)
	return redirect(url_for('.error', message = 'Something went wrong, please retry'))

@app.route("/user/bookings", methods =["GET"])
@login_required
def bookings():
	bookings = get_bookings(get_user_id())
	return render_template('bookings.html', user_name = get_user_name(), bookings = bookings, show_home_in_nav = True)

@app.route("/user/rate", methods =["GET", "POST"])
@login_required
def rate_show():
	if 'show_id' not in request.args:
		return redirect(url_for('.error', message = 'Show id required for rating'))
	show_id = request.args.get('show_id')
	show = get_show(show_id)
	if request.method == "GET":
		return render_template('rate_show.html', user_name = get_user_name(), show_name = show.name, show_id = show_id)
	if 'rating' not in request.form:
		return redirect(url_for('.error', message = 'rating value required for rating'))
	rating = request.form['rating']
	save_rating(rating, show_id, get_user_id())
	return redirect('/user/home', code=302)

@app.route("/user/search", methods =["GET"])
@login_required
def search():
	query = request.args.get('q')
	rating_above = request.args.get('rating_above')
	tag_ids = request.args.get('tags')
	if not rating_above:
		rating_above = 'all_ratings'
	if not tag_ids:
		tag_ids = 'all_tags'
	if not query:
		query = ''
	shows = []
	print('Paramters', tag_ids)
	if query or rating_above or tag_ids:
		shows = get_shows(query , tag_ids, rating_above)
	return render_template('search_show.html', user_name = get_user_name(), tags = get_all_tags() ,
	 selected_tag = tag_ids,selected_rating =rating_above,  hide_search_in_nav = True, shows = shows, q = query)

@app.route("/user/show_details/<int:show_id>", methods =["GET"])
@login_required
def user_show_details(show_id):
	venues = get_all_venues(show_id)
	show = get_show(show_id)
	screen_ts = get_all_timeslots(show_id)
	venue_ts = {}
	for v in venues:
		for screen in screen_ts:
			if screen.venue_id == v.id:
				if v.id in venue_ts:
					venue_ts[v.id].append(screen_ts[screen])
				else:
					venue_ts[v.id] = screen_ts[screen]
	return render_template('user_show_details.html', show = show, venues = venues, venue_ts = venue_ts, user_name = get_user_name())

@app.route("/admin/search", methods =["GET"])
@admin_login_required
def admin_search():
	query = request.args.get('q')
	location = request.args.get('location')
	if not query:
		query = ''
	if not location:
		location = 'all_locations'
	locations = get_all_locations()
	venues = []

	if query or location:
		venues = get_venues(query, location)
	return render_template('search_venue.html', q = query, selected_location = location, venues = venues,
	locations = locations,  hide_search_in_nav = True, show_home_in_nav = True)

@app.route("/admin/edit_venue/<int:venue_id>", methods =["GET", "POST"])
@admin_login_required
def edit_venue(venue_id):
	venue = get_venue(venue_id)
	if request.method == "GET":
		return render_template('edit_venue.html', venue = venue)

	name = request.form.get('name')
	place = request.form.get('place')
	venue.name = name
	venue.place = place
	if update_venue(venue):
		return redirect('/admin/home', code=302)
	return redirect(url_for('.error', message = 'Update venue failed'))

	


		


		
		 
		

	





	











		
			
		
















		



