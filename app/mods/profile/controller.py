import logging
from http import HTTPStatus

from flask import Blueprint, render_template, session

from app import rrn_user_service, subscription_service, app_config
from app.flask_utils import login_required, _pull_lang_code, _add_language_code

mod_profile = Blueprint('profile', __name__, url_prefix='/<lang_code>/profile')

logger = logging.getLogger(__name__)


@mod_profile.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_profile.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_profile.route('/', methods=['GET', 'POST'])
@login_required
def profile_page():
    logger.info('profile_page method')
    user_subscriptions = rrn_user_service.get_user_subscriptions(user_uuid=session['user']['uuid'])
    subscriptions_dict = subscription_service.get_subscriptions_dict(lang_code=session['lang_code'])
    for us in user_subscriptions:
        sub = subscriptions_dict.get(us['subscription_id'])
        us['subscription'] = sub

    return render_template('profile/profile.html', code=HTTPStatus.OK, user_subscriptions=user_subscriptions)
