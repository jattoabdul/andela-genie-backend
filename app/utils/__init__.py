from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def to_camel_case(snake_str):
	"""Format string to camel case."""
	title_str = snake_str.title().replace("_", "")
	return title_str[0].lower() + title_str[1:]
	
	
def to_pascal_case(word, sep='_'):
	return ''.join(list(map(lambda x: x.capitalize(), word.split(sep))))


def request_item_title(item):
	items = {1: 'Locker Allocation', 2: 'Back / Lumbar Support', 3: 'Temporary ID Cards', 4: 'Chair', 5: 'Other'}
	
	if type(item) is int:
		return items[item]
	
	raise TypeError('argument must be of type int')
