from app.controllers.base_controller import BaseController
from app.repositories.request_repo import RequestRepo
from app.utils import request_status_text, request_item_title
from app.utils.slackhelper import SlackHelper


class HomeController(BaseController):
	def __init__(self, request):
		BaseController.__init__(self, request)
		self.request_repo = RequestRepo()
		self.slackhelper = SlackHelper()
		
	def home_page(self):
		all_requests = self.request_repo.list_requests()
		return self.handle_response('OK', payload={'requests': all_requests[0], 'meta': all_requests[1]})
	
	def update_request_status(self, request_id):
		msg, status = self.request_params('msg', 'status')
		try:
			status_text = request_status_text(status)
			request_obj = self.request_repo.get(request_id)
			if request_obj:
				
				# This request has been marked ad completed already. No Updates allowed.
				if request_obj.status == 2:
					return self.handle_response(msg='This request has already been marked as completed. No Updates allowed', status_code=400)
				
				# Update Request Object
				self.request_repo.update(request_obj, **{'status': status})
				
				slack_msg = f'''
				```Request Update \n
RequestID: {request_obj.id} \n
Item Requested: {request_item_title(request_obj.item)} \n
Status: {status_text} \n
Staff Message: {msg}```
				
				'''
				
				self.slackhelper.post_message(msg=slack_msg, recipient=request_obj.user.slack_id)
			
			return self.handle_response('OK', payload={'request': self.request_repo.serialize_request_response(request_obj)})
		except Exception as e:
			return self.handle_response(msg='Invalid Status ID Provided', status_code=400)

