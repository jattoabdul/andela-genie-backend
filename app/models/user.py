from .base_model import BaseModel, db


class User(BaseModel):
	__tablename__ = 'users'
	
	first_name = db.Column(db.String())
	last_name = db.Column(db.String())
	email = db.Column(db.String())
	slack_id = db.Column(db.String(), nullable=False)
	
	requests = db.relationship('Request')