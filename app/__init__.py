import os
from http import HTTPStatus
from pprint import pprint

from flask import Flask, url_for, redirect, request
from flask_babel import Babel
from flask_disqus import Disqus
from flask_moment import Moment

from app.cache import CacheService
from app.mods.error import page_not_found, forbidden, internal_server_error
from app.policy import *
from app.service import *

logging.basicConfig(level=logging.DEBUG, format='WEBAPP: %(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

app = Flask(__name__)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')

babel = Babel(app)

disq = Disqus(app)

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

rrn_usersapi_service = RRNUsersAPIService(api_url=app_config['API_URL'],
                                          resource_name=app_config['USERS_API_RESOURCE_NAME'])

rrn_vpnserversapi_service = RRNVPNServersAPIService(api_url=app_config['API_URL'],
                                                    resource_name=app_config['USER_VPNSERVERS_API_RESOURCE_NAME'])

rrn_billingapi_service = RRNBillingAPIService(api_url=app_config['API_URL'],
                                              resource_name=app_config['SERVICES_API_RESOURCE_NAME'])

rrn_ordersapi_service = RRNOrdersAPIService(api_url=app_config['API_URL'],
                                            resource_name=app_config['ORDERS_API_RESOURCE_NAME'])

rrn_userserverconfigurationsapi_service = RRNUserServerConfigurationsAPIService(api_url=app_config['API_URL'],
                                                                                resource_name=app_config[
                                                                                    'USER_VPNSERVER_CONFIGS_API_RESOURCE_NAME'])

email_service = EmailService(smtp_server=app_config['EMAIL_SMTP']['server'],
                             smtp_port=app_config['EMAIL_SMTP']['port'],
                             smtp_username=app_config['EMAIL_SMTP']['support_account']['email'],
                             smtp_password=app_config['EMAIL_SMTP']['support_account']['password'],
                             from_name=app_config['EMAIL_SMTP']['support_account']['from_name'],
                             from_email=app_config['EMAIL_SMTP']['support_account']['email'],
                             templates_path="%s%s" % (app.root_path, "/static/assets/email-tmpls"))

rrn_servicesapi_service = RRNServicesAPIService(billing_service=rrn_billingapi_service, cache_service=cache_service)

user_policy = UserPolicy(rrn_users_api_service=rrn_usersapi_service, rrn_services_api_service=rrn_servicesapi_service)
order_policy = OrderPolicy(rrn_orders_api_service=rrn_ordersapi_service)

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
    return redirect(location=redirect_url, code=302)


@app.route('/confirm-email', methods=['GET'])
def confirm_email():
    logger.info('confirm_email method')

    e = request.args.get('e', None)
    token = request.args.get('token', None)

    logger.debug(f"email: {e}, token: {token}")

    if 'user' not in session or not e or not token:
        logger.info('no user in session or no email or no token. redirect to index')
        return redirect(url_for('index.index_lang_page'))

    user_json = session.get('user')

    src_token = user_json['email_confirm_token']

    if src_token != token:
        logger.error('tokens does not match')
        return redirect(url_for('index.index_lang_page'))

    logger.info('update user')
    user_json['modify_reason'] = 'confirm email'
    user_json['is_email_confirmed'] = True

    rrn_usersapi_service.update_user(user_json=user_json)
    session['user'] = user_json
    return redirect(url_for('profile.profile_page'))


@app.route('/profile/', methods=['GET'])
def profile_page():
    logger.info('profile page')
    redirect_url = url_for('profile.profile_page', lang_code=session['lang_code'])
    return redirect(location=redirect_url, code=302)


@app.route('/pricing/', methods=['GET'])
def pricing_page():
    logger.info('pricing page')
    redirect_url = url_for('pricing.pricing_page', lang_code=session['lang_code'])
    return redirect(location=redirect_url, code=302)


@app.route('/order/', methods=['GET'])
def order_page():
    logger.info('order page')
    redirect_url = url_for('order.order_page', lang_code=session['lang_code'])
    return redirect(location=redirect_url, code=302)


@app.route('/download/', methods=['GET'])
def download_page():
    logger.info('downloads page')
    redirect_url = url_for('download.download_page', lang_code=session['lang_code'])
    return redirect(location=redirect_url, code=302)


@app.route('/downloads/', methods=['GET'])
def downloads_page():
    logger.info('downloads page')
    redirect_url = url_for('download.download_page', lang_code=session['lang_code'])
    return redirect(location=redirect_url, code=302)


@app.route('/down/', methods=['GET'])
def down_page():
    logger.info('downloads page')
    redirect_url = url_for('download.download_page', lang_code=session['lang_code'])
    return redirect(location=redirect_url, code=302)


pprint(app.url_map._rules_by_endpoint)
