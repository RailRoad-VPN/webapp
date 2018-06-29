import os
from pprint import pprint

import jinja2
from flask import Flask, url_for, redirect, session, request
from flask_babel import Babel
from flask_disqus import Disqus
from flask_moment import Moment
from jinja2 import Environment

from app.cache import CacheService
from app.service import *
from app.mods.error import page_not_found, forbidden, internal_server_error

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

logger.debug('debug message')
logger.info('info message')
logger.warning('warning message')
logger.error('error message')
logger.critical('critical message')

app = Flask(__name__)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')

babel = Babel(app)

disq = Disqus(app)

# TODO i10n dates
moment = Moment(app)

from app import cli

# Load config based on env variable
ENVIRONMENT_CONFIG = os.environ.get("ENVIRONMENT_CONFIG", default='DevelopmentConfig')
logger.info("Got ENVIRONMENT_CONFIG variable: %s" % ENVIRONMENT_CONFIG)
config_name = "%s.%s" % ('config', ENVIRONMENT_CONFIG)
logger.info("Config name: %s" % config_name)
app.config.from_object(config_name)

app_config = app.config

user_discovery_service = UserDiscoveryService()

cache_service = CacheService(app=app)

rrn_user_service = RRNUsersAPIService(api_url=app_config['API_URL'],
                                      resource_name=app_config['USERS_API_RESOURCE_NAME'])

rrn_billing_service = RRNBillingAPIService(api_url=app_config['API_URL'],
                                           resource_name=app_config['SUBSCRIPTIONS_API_RESOURCE_NAME'])

rrn_orders_service = RRNOrdersAPIService(api_url=app_config['API_URL'],
                                         resource_name=app_config['ORDERS_API_RESOURCE_NAME'])

ppg_payments_service = PayProGlobalPaymentService(config=app_config)

subscription_service = SubscriptionService(billing_service=rrn_billing_service, cache_service=cache_service)

from app.flask_utils import before_request, get_locale

app.before_request(before_request)

from app.mods.index.controller import mod_index as index_module

app.register_blueprint(index_module)

from app.mods.about.controller import mod_about as about_module

app.register_blueprint(about_module)

from app.mods.contact.controller import mod_contact as contact_module

app.register_blueprint(contact_module)

from app.mods.features.controller import mod_features as features_module

app.register_blueprint(features_module)

from app.mods.faq.controller import mod_faq as faq_module

app.register_blueprint(faq_module)

from app.mods.pricing.controller import mod_pricing as pricing_module

app.register_blueprint(pricing_module)

from app.mods.download.controller import mod_download as download_module

app.register_blueprint(download_module)

from app.mods.auth.controller import mod_auth as auth_module

app.register_blueprint(auth_module)

from app.mods.profile.controller import mod_profile as profile_module

app.register_blueprint(profile_module)

from app.mods.order.controller import mod_order as order_module

app.register_blueprint(order_module)

from app.mods.blog.controller import mod_blog as blog_module

app.register_blueprint(blog_module)

app.register_error_handler(HTTPStatus.NOT_FOUND, page_not_found)
app.register_error_handler(HTTPStatus.FORBIDDEN, forbidden)
app.register_error_handler(HTTPStatus.INTERNAL_SERVER_ERROR, internal_server_error)


@app.route('/', methods=['GET'])
def index_page():
    logger.info('index page')
    redirect_url = url_for('index.index_lang_page', lang_code=session['lang_code'])
    return redirect(redirect_url)


pprint(app.url_map._rules_by_endpoint)
