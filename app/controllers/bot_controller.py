import json
import requests
from app.utils import request_item_title
from app.repositories.request_repo import RequestRepo
from app.repositories.user_repo import UserRepo
from app.utils.slackhelper import SlackHelper
from app.controllers.base_controller import BaseController, make_response


class BotController(BaseController):
	def __init__(self, request):
		BaseController.__init__(self, request)
		self.slackhelper = SlackHelper()
		self.user_repo = UserRepo()
		self.request_repo = RequestRepo()
		
		''' Dialogs Elements'''
		self.request_dialog_element = [
			{
				"label": "What Do You Need",
				"type": "select",
				"name": "item",
				"options": [
					{
						"label": "Locker Allocation",
						"value": "1"
					},
					{
						"label": "Back / Lumbar Support",
						"value": "2"
					},
					{
						"label": "Temporary ID Cards",
						"value": "3"
					},
					{
						"label": "Chair",
						"value": "4"
					},
					{
						"label": "Maintenance",
						"value": "5"
					},
					{
						"label": "Other",
						"value": "50"
					},
				]
			},
			{
				"label": "Category",
				"type": "select",
				"name": "category",
				"options": [
					{
						"label": "Not Applicable",
						"value": "0"
					},
					{
						"label": "Electrical",
						"value": "1"
					},
					{
						"label": "Carpentry",
						"value": "2"
					},
					{
						"label": "Plumbing",
						"value": "3"
					},
					{
						"label": "HVAC",
						"value": "4"
					},
					{
						"label": "Other",
						"value": "50"
					},
				]
			},
			{
				"label": "Location",
				"type": "select",
				"name": "location",
				"options": [
					{
						"label": "EPIC Tower",
						"value": "1"
					},
					{
						"label": "Amity",
						"value": "2"
					},
					{
						"label": "Jacob Mews",
						"value": "3"
					},
				]
			},
			{
				"label": "Quantity",
				"type": "text",
				"name": "qty",
				"value": "1",
			},
			{
				"label": "Additional Info",
				"type": "textarea",
				"name": "info",
				"optional": "true"
			},
		]
		
	def bot(self):
		slack_id, trigger_id = self.post_params('user_id', 'trigger_id')
		slack_user_info = self.slackhelper.user_info(slack_id)
		user_real_name = slack_user_info['user']['profile']['first_name']
		
		self.create_dialog(trigger_id=trigger_id)
		return self.handle_response(slack_response={'text': f'Welcome {user_real_name} - What request do you need granted?'})
	
	def interactions(self):
		request_payload, = self.post_params('payload')
		payload = json.loads(request_payload)
		
		webhook_url = payload["response_url"]
		slack_id = payload['user']['id']
		
		if payload['type'] == 'dialog_submission':
			slack_user_info = self.slackhelper.user_info(slack_id)
			slack_user_email = slack_user_info['user']['profile']['email']
			slack_user_fname = slack_user_info['user']['profile']['first_name']
			slack_user_lname = slack_user_info['user']['profile']['last_name']
			
			if payload['callback_id'] == 'genie_request_form':
				request_item = int(payload['submission']['item'])
				request_qty = payload['submission']['qty']
				info = payload['submission']['info']
				category = payload['submission']['category']
				location = payload['submission']['location']
				
				if not request_qty.isdigit():
					return self.handle_response(slack_response={'errors': [{'name': 'qty', 'error': 'Quantity Must Be Numeric'}]})
				
				# Write to DB here
				user = self.user_repo.find_or_create(email=slack_user_email,
													 **{'first_name': slack_user_fname, 'last_name': slack_user_lname,
														'slack_id': slack_id})
				genie_request = self.request_repo.new_request(
					user_id=user.id, item=request_item, qty=request_qty, category=category, location=location, info=info
				)
				
				slack_data = {'text': f"I've got your request. Let me do some magic now. Request ID: {genie_request.id}"}
				requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})

				self.notify_request_channel(f'New Request Alert: {slack_user_fname} requested for {request_item_title(request_item)}. Request ID: {genie_request.id}')
		
		elif payload['type'] == 'dialog_cancellation':
			slack_data = {'text': "Aww! - I'm always here for when next you need me. :genie: "}
			requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
		
		return make_response('', 200)
		
	def create_dialog(self, trigger_id):
		dialog = {
			"title": 'Genie Request Form',
			"submit_label": "Submit",
			"callback_id": 'genie_request_form',
			"notify_on_cancel": True,
			"elements": self.request_dialog_element
		}
		return self.slackhelper.dialog(dialog=dialog, trigger_id=trigger_id)
	
	def notify_request_channel(self, msg):
		return self.slackhelper.post_message(msg=msg, recipient='genie_los_facilities')
