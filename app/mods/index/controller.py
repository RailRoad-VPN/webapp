import logging

from flask import Blueprint, render_template, session, request, redirect

# Define the blueprint: 'index', set its url prefix: app.url/
mod_index = Blueprint('index', __name__, url_prefix='/<lang_code>/')


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
        if lang_code != session['lang_code']:
            session['lang_code'] = lang_code
        values.pop('lang_code')


@mod_index.route('/', methods=['GET'])
def index_lang_page():
    logging.info('index_lang page')
    redirect_url = request.args.get('next', None)
    if redirect_url:
        return redirect(request.base_url[:-1] + redirect_url) # remove trailing slash after base url
    return render_template('index/index.html', code=200)


@mod_index.route('/features', methods=['GET'])
def features_page():
    logging.info('features_page method')
    return render_template('index/features.html', code=200)


@mod_index.route('/pricing', methods=['GET'])
def pricing_page():
    logging.info('pricing_page method')
    return render_template('index/pricing.html', code=200)


@mod_index.route('/download', methods=['GET'])
def download_page():
    logging.info('download_page method')
    return render_template('index/download.html', code=200)


@mod_index.route('/contact', methods=['GET'])
def contact_page():
    logging.info('contact_page method')
    return render_template('index/download.html', code=200)
