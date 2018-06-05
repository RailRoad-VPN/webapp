import logging
import logging
import sys

from flask import Blueprint, request, render_template, \
    session

from app import rrn_billing_service

sys.path.insert(0, '../rest_api_library')
from rest import APIException

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_order = Blueprint('order', __name__, url_prefix='/<lang_code>/order')


@mod_order.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', session['lang_code'])


@mod_order.url_value_preprocessor
def pull_lang_code(endpoint, values):
    try:
        values.pop('lang_code')
    except:
        pass


@mod_order.route('', methods=['GET', 'POST'])
def order_page():
    logging.info('order_page method')

    pack = request.args.get('pack', None)

    subscriptions = None
    try:
        subscriptions = rrn_billing_service.get_subscriptions(lang_code=session['lang_code'])
    except APIException as e:
        pass

    return render_template('index/order.html', pack=pack, subscriptions=subscriptions, code=200)
