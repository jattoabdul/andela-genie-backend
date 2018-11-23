from app.repositories.base_repo import BaseRepo
from app.models.user import User

class UserRepo(BaseRepo):
	
	def __init__(self):
		BaseRepo.__init__(self, User)
		
	def new_user(self, first_name, last_name, email, slack_id):
		user = User(first_name=first_name, last_name=last_name, email=email, slack_id=slack_id)
		user.save()
		return user
	
	def find_or_create(self, email, **kwargs):
		user = self.find_first(**{'email':email})
		if user:
			return user
		
		return self.new_user(kwargs['first_name'], kwargs['last_name'], email, kwargs['slack_id'])
