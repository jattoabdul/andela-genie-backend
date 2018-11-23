from app.repositories.base_repo import BaseRepo
from app.models.request import Request as GenieRequest


class RequestRepo(BaseRepo):
	
	def __init__(self):
		BaseRepo.__init__(self, GenieRequest)
		
	@staticmethod
	def new_request(user_id, item, qty, info=None):
		request = GenieRequest(user_id=user_id, item=item, qty=qty, info=info)
		request.save()
		return request
