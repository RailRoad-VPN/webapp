import hashlib
import logging
import sys
import uuid
from http import HTTPStatus

from flask import Blueprint, request, render_template, \
    g, session, redirect, url_for, jsonify
from werkzeug.security import check_password_hash

from app import rrn_user_service
from app.flask_utils import login_required
from app.models import AjaxResponse, AjaxError
from app.models.exception import DFNError

sys.path.insert(0, '../rest_api_library')
from rest import APIException
from response import APIResponseStatus

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

    return render_template('index/order.html', pack=pack, code=200)