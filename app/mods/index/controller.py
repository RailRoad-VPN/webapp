import logging
import sys

from flask import Blueprint, render_template, session, request, redirect

# Define the blueprint: 'index', set its url prefix: app.url/
from app import rrn_billing_service

sys.path.insert(0, '../rest_api_library')
from rest import APIException

mod_index = Blueprint('index', __name__, url_prefix='/<lang_code>/')

logger = logging.getLogger(__name__)


@mod_index.url_defaults
def add_language_code(endpoint, values):
    if 'lang_code' in values:
        lang_code = values['lang_code']
        if lang_code != session['lang_code']:
            session['lang_code'] = lang_code
    values.setdefault('lang_code', session['lang_code'])


@mod_index.url_value_preprocessor
def pull_lang_code(endpoint, values):
    if 'lang_code' in values:
        lang_code = values['lang_code']
        if 'lang_code' in session:
            if lang_code != session['lang_code']:
                session['lang_code'] = lang_code
        else:
            session['lang_code'] = lang_code
        values.pop('lang_code')


@mod_index.route('/', methods=['GET'])
def index_lang_page():
    logger.info('index_lang page')

    if 'locale' in request.args:
        r_url = str(request.base_url) + str(request.referrer).split("/")[-1]
        return redirect(r_url)

    subscriptions = None
    try:
        subscriptions = rrn_billing_service.get_subscriptions(lang_code=session['lang_code'])
    except APIException as e:
        pass
    return render_template('index/index.html', code=200, subscriptions=subscriptions)


@mod_index.route('/features', methods=['GET'])
def features_page():
    logger.info('features_page method')
    return render_template('index/features.html', code=200)


@mod_index.route('/pricing', methods=['GET'])
def pricing_page():
    logger.info('pricing_page method')

    subscriptions = None
    try:
        subscriptions = rrn_billing_service.get_subscriptions(lang_code=session['lang_code'])
    except APIException:
        pass

    return render_template('index/pricing.html', code=200, subscriptions=subscriptions)


@mod_index.route('/download', methods=['GET'])
def download_page():
    logger.info('download_page method')
    return render_template('index/download.html', code=200)


@mod_index.route('/contact', methods=['GET'])
def contact_page():
    logger.info('contact_page method')
    return render_template('index/download.html', code=200)
