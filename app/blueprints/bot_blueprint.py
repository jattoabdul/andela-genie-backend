from app.blueprints.base_blueprint import Blueprint, BaseBlueprint, request, Security, Auth
from app.controllers.bot_controller import BotController

url_prefix = '{}/bot'.format(BaseBlueprint.base_url_prefix)
bot_blueprint = Blueprint('bot', __name__, url_prefix=url_prefix)

bot_controller = BotController(request)

@bot_blueprint.route('/', methods=['GET','POST'])
def bot():
	return bot_controller.bot()


@bot_blueprint.route('/interactions/', methods=['GET', 'POST'])
def interactions():
	return bot_controller.interactions()
