from flask import redirect, session, url_for
from functools import wraps

def login_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if not is_authenticated():
			return redirect(url_for('.logout'))
		return f(*args, **kwargs)
	return wrapper

def admin_login_required(f):
	@wraps(f)
	def admin_wrapper(*args, **kwargs):
		if not is_authenticated(for_admin = True):
			return redirect(url_for('.logout'))
		return f(*args, **kwargs)
	return admin_wrapper

def is_authenticated(for_admin = False):
	user_id = -1
	if 'user_id' in session:
		user_id = session['user_id']

	type = 0
	if 'user_type' in session:
		type = session['user_type']
	type_matches = False
	if for_admin:
		type_matches = type == 1
	else:
		type_matches = type == 2
	return user_id and user_id > 0 and type_matches

def save_session(user):
	session['user_id'] = user.id
	session['user_name'] = user.user_name
	session['user_type'] = user.type

def get_user_name():
	if 'user_name' in session:
		return session['user_name']
	return ''

def get_user_id():
	if 'user_id' in session:
		return session['user_id']
	return -1

def is_admin():
	if 'user_type' in session:
		return session['user_type'] == 1
	return False



def clear_session():
	session.pop('user_id', None)
	session.pop('user_name', None)
	session.pop('user_type', None)


	
