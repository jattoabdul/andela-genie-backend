from app.repositories.base_repo import BaseRepo
from app.models.locker import Locker


class LockerRepo(BaseRepo):
	
	def __init__(self):
		BaseRepo.__init__(self, Locker)
