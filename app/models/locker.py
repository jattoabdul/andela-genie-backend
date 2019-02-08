from .base_model import BaseModel, db


class Locker(BaseModel):
	__tablename__ = 'lockers'
	
	locker_number = db.Column(db.Integer(), nullable=False)
	floor = db.Column(db.Integer(), nullable=False)
	wing = db.Column(db.Integer(), nullable=False)
	user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=True)
	status = db.Column(db.Integer(), default=0, nullable=False)
