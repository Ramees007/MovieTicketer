


class Config():
	DEBUG = False
	SQLALCHEMY_DATABASE_URI = None
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SECRET_KEY = None

class LocalDevConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = "sqlite:///TicketBook.sqlite3"
	SECRET_KEY = "test_secret"
	
