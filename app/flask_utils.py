import datetime
import logging
from functools import wraps

from flask import session, g, request, redirect, url_for

from app import app, babel

logging.basicConfig(level=logging.DEBUG)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user = g.user
            if user is None:
                return redirect(url_for('auth.signin', next=request.url))
        except AttributeError:
            return redirect(url_for('auth.signin', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def before_request():
    # clean jinja_env cache
    app.jinja_env.cache = {}

    if 'lang_code' not in session or session['lang_code'] == 'None':
        session['lang_code'] = str(get_locale())

    # check DEBUG is False
    if app.config['DEBUG'] is False:
        # Debug is False
        if 'debug' in session:
            session.pop('debug')
    else:
        # Debug is True
        session['debug'] = True
    # check user in session
    if 'user' in session:
        # user exist in session
        try:
            g.user = session['user']
        except (TypeError, KeyError) as e:
            logging.error(e)


@babel.localeselector
def get_locale():
    if 'lang_code' not in session:
        locale = request.accept_languages.best_match(app.config['LANGUAGES'])
        if locale is None:
            locale = request.accept_languages.best.split('-')[0]
            if locale not in app.config['LANGUAGES']:
                locale = 'en'
        return locale
    else:
        return session['lang_code']


decCache = dict()
decCases = [2, 0, 1, 1, 1, 2]


def decOfNum(number, titles):
    if number not in decCache:
        if 4 < number % 100 < 20:
            n = 2
        else:
            n = decCases[min(number % 10, 5)]
        decCache[number] = n
    return titles[decCache[number]]


@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now().replace(microsecond=0).isoformat()}
