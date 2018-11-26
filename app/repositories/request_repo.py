from app.repositories.base_repo import BaseRepo
from app.utils import request_item_title, format_response_timestamp, request_status_text
from app.models.request import Request as GenieRequest


class RequestRepo(BaseRepo):
	
	def __init__(self):
		BaseRepo.__init__(self, GenieRequest)
		
	def list_requests(self):
		
		all_requests = self.fetch_all()
		
		request_list = [self.serialize_request_response(request_item) for request_item in all_requests.items]
		return tuple((request_list, self.pagination_meta(all_requests)))
	
	def serialize_request_response(self, genie_request_obj):
		return {
			'id': genie_request_obj.id, 'info': genie_request_obj.info, 'itemId': genie_request_obj.item,
			'item': request_item_title(genie_request_obj.item), 'qty': genie_request_obj.qty,
			'userId': genie_request_obj.user_id, 'user': genie_request_obj.user.serialize(),
			'statusText': request_status_text(genie_request_obj.status), 'status': genie_request_obj.status,
			'timestamps': {'createdAt': format_response_timestamp(genie_request_obj.created_at),
						   'updatedAt': format_response_timestamp(genie_request_obj.updated_at)}
		}
	
	@staticmethod
	def new_request(user_id, item, qty, info=None):
		request = GenieRequest(user_id=user_id, item=item, qty=qty, info=info)
		request.save()
		return request
