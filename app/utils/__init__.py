from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


def to_camel_case(snake_str):
	"""Format string to camel case."""
	title_str = snake_str.title().replace("_", "")
	return title_str[0].lower() + title_str[1:]
	
	
def to_pascal_case(word, sep='_'):
	return ''.join(list(map(lambda x: x.capitalize(), word.split(sep))))


def request_item_title(item):
	items = {1: 'Locker Allocation', 2: 'Back / Lumbar Support', 3: 'Temporary ID Cards', 4: 'Chair', 5: 'Maintenance', 50: 'Other'}
	if type(item) is int and item in items:
		return items[item]
	raise TypeError('argument must be of type int or invalid ID provided')


def request_category_title(item):
	items = {0: 'Not Applicable', 1: 'Electrical', 2: 'Carpentry', 3: 'Plumbing', 4: 'HVAC', 50: 'Other'}
	if type(item) is int and item in items:
		return items[item]
	raise TypeError('argument must be of type int or invalid ID provided')


def request_location_title(item):
	items = {1: 'EPIC Tower', 2: 'Amity', 3: 'Jacob Mews'}
	if type(item) is int and item in items:
		return items[item]
	raise TypeError('argument must be of type int or invalid ID provided')


def request_status_text(status):
	statues = {0: 'Received', 1: 'In Progress', 2: 'Resolved'}
	if type(status) is int and status in statues:
		return statues[status]
	raise TypeError('argument must be of type int or invalid ID provided')


def format_response_timestamp(date_obj):
	if isinstance(date_obj, datetime):
		return {'isoDate': date_obj.isoformat(), 'datePretty': date_obj,
				'datePrettyShort': date_obj.strftime('%b %d, %Y')}