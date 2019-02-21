from app.controllers.base_controller import BaseController
from app.repositories.request_repo import RequestRepo
from app.utils import request_status_text, request_item_title, floor_wings
from app.utils.slackhelper import SlackHelper
import pandas as pd
from app.repositories.user_repo import UserRepo
from app.models.locker import Locker
import threading
import humanize


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
	
	def import_data(self):
		issues = []
		page_number, = self.get_params('page')
		
		csv = pd.read_csv(f'lockers-{page_number}.csv', )
		for row in csv.itertuples():
			email = row[1]
			name = row[2]
			locker_number = row[3]
			status = row[4]
			floor = row[5].lower()
			wing = row[6].lower()
			
			if floor == 'fifth':
				floor_id = 5
				
			if floor == 'fourth':
				floor_id = 4
				
			if floor == 'third':
				floor_id = 3
				
			if floor == 'first':
				floor_id = 1
				
			if wing == 'eko':
				wing_id = 7
				
			if wing == 'bay':
				wing_id = 6
				
			if wing == 'big apple':
				wing_id = 5
				
			if wing == 'safari':
				wing_id = 4
				
			if wing == 'kampala':
				wing_id = 3
				
			if wing == 'naija':
				wing_id = 2
				
			if wing == 'gold coast':
				wing_id = 1
			
			if type(email) is str:
				first_name = name.split()[0]
				last_name = name.split()[-1]
				print(first_name, last_name)
				
				slack_user = self.slackhelper.find_by_email(email)
				
				if slack_user['ok'] is False:
					missing_users = {'name': name, 'email': email, 'locker': locker_number, 'floor': floor, 'wing': wing}
					issues.append(missing_users)
					locker = Locker(locker_number=locker_number, floor=floor_id, wing=wing_id, status=0)
					locker.save()
				
				else:
					slack_id = slack_user['user']['id']
				
					user = UserRepo().find_or_create(email=email, **{'first_name': first_name, 'last_name': last_name, 'slack_id': slack_id})
					locker = Locker(locker_number=locker_number, floor=floor_id, wing=wing_id, user_id=user.id, status=1)
					locker.save()
					
					msg = f'Hi {first_name}, \n' \
						f'You currently are assigned locker number {locker_number} on the {humanize.ordinal(int(floor_id))} floor {floor_wings(int(wing_id))} wing. \n' \
						f'If this information is wrong, please reach out to the facilities team for correction. If correct, kindly ignore this message and have a great day.\n' \
						f'`Genie`'
					
					t = threading.Thread(target=self.slackhelper.post_message, args=(msg, slack_id))
					t.daemon = True
					t.start()
			
			if type(email) is float or status.lower == 'free':
				locker = Locker(locker_number=locker_number, floor=floor_id, wing=wing_id, status=0)
				locker.save()
		
		return self.handle_response('OK', payload={'missing users': issues, 'info': 'Invalid or Ex-Andela Staff. Their Lockers have been marked as available by default.'})

