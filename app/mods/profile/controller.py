import logging

from flask import Blueprint, render_template, session

from app.flask_utils import login_required

mod_profile = Blueprint('profile', __name__, url_prefix='/<lang_code>/profile')


@mod_profile.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', session['lang_code'])


@mod_profile.url_value_preprocessor
def pull_lang_code(endpoint, values):
    try:
        values.pop('lang_code')
    except:
        pass


@mod_profile.route('/', methods=['GET', 'POST'])
@login_required
def profile_page():
    logging.info('profile_page method')
    return render_template('profile/profile.html', code=200)
