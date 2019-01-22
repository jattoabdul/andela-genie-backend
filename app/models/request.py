from .base_model import BaseModel, db


class Request(BaseModel):
	__tablename__ = 'requests'
	
	user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
	item = db.Column(db.Integer())
	qty = db.Column(db.String())
	category = db.Column(db.Integer(), nullable=True)
	location = db.Column(db.Integer(), nullable=True)
	info = db.Column(db.Text(), nullable=True)
	status = db.Column(db.Integer(), default=0)
	
	user = db.relationship('User')