import datetime
import logging
import uuid
from functools import wraps

from flask import session, g, request, redirect, url_for

from app import app, babel, user_discovery_service

logging.basicConfig(level=logging.DEBUG)


def authorize_user(user_json):
    session['logged_in'] = True
    session['user'] = user_json
    session['notifications'] = []
    session['locale'] = request.accept_languages.best
    g.user = user_json
    notification = {
        'id': uuid.uuid4(),
        'message': 'You were logged in',
        'time': 'just now'
    }
    if 'notifications' in session:
        session['notifications'].append(notification)
    else:
        session['notifications'] = []


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


def _set_user_network_status(ip: str):
    if ip == '127.0.0.1':
        ip = '185.89.8.144'
    net_st = user_discovery_service.discover_ip(ip)
    if net_st is not None:
        ns = {
            'ip': ip,
            'city': net_st.city,
            'isp': net_st.isp,
            'status': net_st.status
        }
    else:
        ns = None
    session['network-status'] = ns


def before_request():
    # clean jinja_env cache
    app.jinja_env.cache = {}

    if 'network-status' not in session or (
                    session['network-status'] is not None and session['network-status']['ip'] != request.remote_addr):
        _set_user_network_status(request.remote_addr)

    if 'user_locale' in session and 'gdpr' not in session:
        session['gdpr'] = True

    if 'lang_code' not in session or session['lang_code'] == 'None':
        session['lang_code'] = str(get_locale())

    if 'user_locale' not in session:
        session['user_locale'] = request.accept_languages.best

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


def _add_language_code(endpoint, values):
    if 'lang_code' in values:
        lang_code = values['lang_code']
        if lang_code != session['lang_code']:
            session['lang_code'] = lang_code
    values.setdefault('lang_code', session['lang_code'])


def _pull_lang_code(endpoint, values, app_config):
    if 'lang_code' in values:
        lang_code = values['lang_code']
        if lang_code not in app_config['LANGUAGES']:
            lang_code = 'en'
        if 'lang_code' in session:
            if lang_code != session['lang_code']:
                session['lang_code'] = lang_code
        else:
            session['lang_code'] = lang_code
        values.pop('lang_code')


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
