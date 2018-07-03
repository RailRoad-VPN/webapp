import logging
import sys
from http import HTTPStatus

import datetime
from flask import Blueprint, render_template, session, request, redirect, abort, jsonify

# Define the blueprint: 'index', set its url prefix: app.url/
from app import rrn_billing_service, app_config
from app.flask_utils import _pull_lang_code, _add_language_code
from app.models import AjaxResponse

sys.path.insert(0, '../rest_api_library')
from rest import APIException

mod_index = Blueprint('index', __name__, url_prefix='/<lang_code>/')

logger = logging.getLogger(__name__)


@mod_index.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_index.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_index.route('/', methods=['GET'])
def index_lang_page():
    logger.info('index_lang page')
    
    try:
        subscriptions = rrn_billing_service.get_subscriptions(lang_code=session['lang_code'])
    except APIException:
        subscriptions = None

    return render_template('index/index.html', code=200, subscriptions=subscriptions)


@mod_index.route('/', methods=['POST'])
def subscribe_trial():
    logger.info('subscribe_trial method')

    r = AjaxResponse(success=True)

    email = request.form.get('email', None)

    if email is None:
        r.set_failed()
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp

    # TODO send email

    with open('%s' % (app_config['FS']['subscribe']), 'a') as file:
        file.write("%r\n" % email)
        file.close()

    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp