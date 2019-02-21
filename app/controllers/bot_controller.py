import json
import requests
import humanize
import threading
from app.repositories.locker_repo import LockerRepo
from app.utils import request_item_title, floor_wings, request_location_title, request_category_title
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
		self.locker_repo = LockerRepo()
		
	def bot(self):
		slack_id, trigger_id = self.post_params('user_id', 'trigger_id')
		slack_user_info = self.slackhelper.user_info(slack_id)
		user_real_name = slack_user_info['user']['profile']['first_name']
		
		slack_response = {
			"text": f'Welcome {user_real_name} - What request do you need granted',
			"attachments": [
				{
					"text": "",
					"fallback": "You are unable to choose a game",
					"callback_id": "request_type_selector",
					"color": "#3AA3E3",
					"attachment_type": "default",
					"actions":
						[
							{'name': 'request_type', 'text': 'Allocations', 'type': "button", 'value': 1},
							{'name': 'request_type', 'text': 'More Options', 'type': "button", 'value': 0, 'style': 'danger'}
						]
				}
			]
		}
		return self.handle_response(slack_response=slack_response)
		
	def interactions(self):
		request_payload, = self.post_params('payload')
		payload = json.loads(request_payload)
		
		webhook_url = payload["response_url"]
		slack_id = payload['user']['id']
		
		if payload['type'] == 'interactive_message':
			trigger_id = payload['trigger_id']
			
			if payload['callback_id'] == 'request_type_selector':
				
				if payload['actions'][0]['value'] == '0': # more options was pressed
					dialog_element = [
						{
							"label": "What Do You Need",
							"type": "select",
							"name": "item",
							"options": [
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
					self.create_dialog(trigger_id=trigger_id, dialog_element=dialog_element, callback_id='genie_request_form')
					return make_response('', 200)
				
				if payload['actions'][0]['value'] == '1':
					
					slack_response = {
						"text": f'Which do you need?',
						"attachments": [
							{
								"text": "",
								"callback_id": "allocation_type_selector",
								"color": "#3AA3E3",
								"attachment_type": "default",
								"actions":
									[
										{'name': 'allocation_type', 'text': 'Locker Allocation', 'type': "button", 'value': 'locker_allocation'},
										{'name': 'allocation_type', 'text': 'Amity Allocation', 'type': "button", 'value': 'amity_allocation'}
									]
							}
						]
					}
					return self.handle_response(slack_response=slack_response)
					
			if payload['callback_id'] == 'allocation_type_selector':
				
				if payload['actions'][0]['value'] == 'locker_allocation':
					dialog_element = [
						{
							"label": "Select Your Floor",
							"type": "select",
							"name": "floor",
							"options": [
								{
									"label": "1st Floor",
									"value": "1"
								},
								{
									"label": "3rd Floor",
									"value": "3"
								},
								{
									"label": "4th Floor",
									"value": "4"
								},
								{
									"label": "5th Floor",
									"value": "5"
								}
							]
						},
						{
							"label": "Select Wing",
							"type": "select",
							"name": "wing",
							"options": [
								{
									"label": "Gold Coast",
									"value": "1"
								},
								{
									"label": "Naija",
									"value": "2"
								},
								{
									"label": "Kampala",
									"value": "3"
								},
								{
									"label": "Safari",
									"value": "4"
								},
								{
									"label": "Big Apple",
									"value": "5"
								},
								{
									"label": "City By The Bay",
									"value": "6"
								},
								{
									"label": "Eko",
									"value": "7"
								},
							]
						},
					]
					self.create_dialog(trigger_id=trigger_id, dialog_element=dialog_element, callback_id='locker_request_form')
					return self.handle_response(slack_response={'text': 'Select Floor and Wing'})
		
		if payload['type'] == 'dialog_submission':
			slack_user_info = self.slackhelper.user_info(slack_id)
			slack_user_email = slack_user_info['user']['profile']['email']
			slack_user_fname = slack_user_info['user']['profile']['first_name']
			slack_user_lname = slack_user_info['user']['profile']['last_name']
			
			user = self.user_repo.find_or_create(
				email=slack_user_email, **{'first_name': slack_user_fname, 'last_name': slack_user_lname, 'slack_id': slack_id}
			)
			
			if payload['callback_id'] == 'genie_request_form':
				request_item = int(payload['submission']['item'])
				request_qty = payload['submission']['qty']
				info = payload['submission']['info']
				category = payload['submission']['category']
				location = payload['submission']['location']
				
				if not request_qty.isdigit():
					return self.handle_response(slack_response={'errors': [{'name': 'qty', 'error': 'Quantity Must Be Numeric'}]})
				
				# Write to DB here
				genie_request = self.request_repo.new_request(
					user_id=user.id, item=request_item, qty=request_qty, category=category, location=location, info=info
				)
				
				slack_data = {'text': f"I've got your request. Let me do some magic now. Request ID: {genie_request.id}"}
				data = json.dumps(slack_data)
				headers = {'Content-Type': 'application/json'}
				t = threading.Thread(target=requests.post, args=(webhook_url, data, headers))
				t.daemon = True
				t.start()

				t = None
				
				t = threading.Thread(target=self.notify_request_channel, args=(
					f'New Request Alert: {slack_user_fname} {slack_user_lname} - (<@{slack_id}>) | Request ID: {genie_request.id}',
					[
						{
							'fields': [
								{'title': 'Item', 'value': request_item_title(int(request_item)), 'short': True},
								{'title': 'Location', 'value': request_location_title(int(location)), 'short': True},
								{'title': 'Category', 'value': request_category_title(int(category)), 'short': True},
								{'title': 'Quantity', 'value': request_qty, 'short': True}
							]
						}
					]
				))
				t.daemon = True
				t.start()
				
				requests.post(payload['response_url'], data=None, headers={'Content-Type': 'application/json'})
				return make_response('', 200)
			
			if payload['callback_id'] == 'locker_request_form':
				floor = payload['submission']['floor']
				wing = payload['submission']['wing']
				
				assigned_locker = self.locker_repo.find_first(user_id=user.id)
				if assigned_locker:
					slack_data = {
						'text': f'You already have an assigned locker.',
						'attachments': [
							{
								'fields': [
									{'title': 'Floor', 'value': humanize.ordinal(int(assigned_locker.floor)), 'short': True},
									{'title': 'Wing', 'value': floor_wings(int(assigned_locker.wing)), 'short': True},
									{'title': 'Locker Number', 'value': assigned_locker.locker_number, 'short': True},
								]
							}
						]
					}
					requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
					return make_response('', 200)
				
				free_locker = self.locker_repo.find_first(floor=floor, wing=wing, status=0)
				if free_locker:
					self.locker_repo.update(free_locker, **{'user_id': user.id})
					
					slack_data = {
						'text': f'Awesome. You have been assigned a locker. Contact Facilities Team to pick up your key.',
						'attachments': [
							{
								'fields': [
									{'title': 'Floor', 'value': humanize.ordinal(int(floor)), 'short': True},
									{'title': 'Wing', 'value': floor_wings(int(wing)), 'short': True},
									{'title': 'Locker Number', 'value': free_locker.locker_number, 'short': True},
								]
							}
						]
					}
					data = json.dumps(slack_data)
					headers = {'Content-Type': 'application/json'}
					t = threading.Thread(target=requests.post, args=(webhook_url, data, headers))
					t.daemon = True
					t.start()
					
					t = threading.Thread(target=self.notify_request_channel, args=(
						f'New Locker Allocation: {slack_user_fname} {slack_user_lname} - (<@{slack_id}>) has been assigned a locker.',
						[
							{
								'fields': [
									{'title': 'Floor', 'value': humanize.ordinal(int(floor)), 'short': True},
									{'title': 'Wing', 'value': floor_wings(int(wing)), 'short': True},
									{'title': 'Locker Number', 'value': free_locker.locker_number, 'short': True},
								]
							}
						]
					))
					t.daemon = True
					t.start()
					
					requests.post(payload['response_url'], data=None, headers={'Content-Type': 'application/json'})
					return make_response('', 200)
				
				slack_data = {
					'text': f'Sorry No Free Lockers Found at the moment. Please check another floor or wing',
					'attachments': [
						{
							'fields': [
								{'title': 'Floor', 'value': humanize.ordinal(int(floor)), 'short': True},
								{'title': 'Wing', 'value': floor_wings(int(wing)), 'short': True}
							]
						}
					]
				}
				requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
				return make_response('', 200)
				
		elif payload['type'] == 'dialog_cancellation':
			slack_data = {'text': "Aww! - I'm always here for when next you need me. :genie: "}
			requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
		
		return make_response('', 200)
		
	def create_dialog(self, trigger_id, dialog_element, callback_id):
		dialog = {
			"title": 'Genie Request Form',
			"submit_label": "Submit",
			"callback_id": callback_id,
			"notify_on_cancel": True,
			"elements": dialog_element
		}
		return self.slackhelper.dialog(dialog=dialog, trigger_id=trigger_id)
	
	def notify_request_channel(self, msg, attachments=None):
		return self.slackhelper.post_message(msg=msg, recipient='genie_los_facilities', attachments=attachments)
