import logging

from flask import Blueprint, render_template, g, url_for, redirect, session, request

# Define the blueprint: 'index', set its url prefix: app.url/
mod_index = Blueprint('index', __name__, url_prefix='/')


@mod_index.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', session['lang_code'])


@mod_index.route('/', methods=['GET'])
def index():
    logging.info('index page')
    return render_template('index.html', code=200)


@mod_index.route('/<lang_code>', methods=['GET'])
def index_lang(lang_code):
    logging.info('index_lang page')
    session['lang_code'] = lang_code
    return render_template('index.html', code=200)