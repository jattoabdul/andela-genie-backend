from .base_model import BaseModel, db


class Request(BaseModel):
	__tablename__ = 'requests'
	
	user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
	item = db.Column(db.Integer())
	qty = db.Column(db.String())
	info = db.Column(db.Text(), nullable=True)
	
	user = db.relationship('User')