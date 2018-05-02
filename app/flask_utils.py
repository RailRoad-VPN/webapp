import datetime
import logging
from functools import wraps

from dateutil.parser import parse
from flask import session, g, request, redirect, url_for

from app import app, babel

logging.basicConfig(level=logging.DEBUG)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            user = g.user
            if user is None:
                return redirect(url_for('login', next=request.url))
        except AttributeError:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def before_request():
    # logging.debug('clean jinja_env cache')
    app.jinja_env.cache = {}

    # logging.debug('get best locale')
    locale = request.accept_languages.best
    # logging.debug('check locale in session')
    if 'locale' in session:
        # logging.debug('locale exist in session')
        locale = session['locale']
    # logging.debug('check force_locale in session')
    if 'force_locale' in session:
        # logging.debug('force locale exist in session')
        locale = session['force_locale']
    session['locale'] = locale

    # logging.debug('check cfg.DEVELOPMENT is False')
    if app.config['DEBUG'] is False:
        # logging.debug('Debug is False')
        if 'debug' in session:
            session.pop('debug')
    else:
        # logging.debug('Debug is True')
        session['debug'] = True
    # logging.debug('check user in session')
    if 'user' in session:
        # logging.debug('user exist in session')
        try:
            g.user = session['user']
        except (TypeError, KeyError) as e:
            logging.error(e)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


@app.template_filter('format_date')
def format_date(s):
    if s is None:
        return None
    return parse(s).strftime('%Y-%m-%d %H:%M:%S')


@app.template_filter('format_human_date')
def format_human_date(s):
    if s is None:
        return None
    return parse(s).strftime('%B %d, %Y')


@app.template_filter('ut2df')
def unixtime2dateformat(s):
    if s is None:
        return None
    return datetime.datetime.fromtimestamp(
        int(s)
    ).strftime('%Y-%m-%d %H:%M:%S')


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


@app.template_filter('date_calc_from_today')
def date_calc_from_today(s):
    if s is None:
        return None
    today = datetime.datetime.today()
    date_in_past = parse(s)

    delta = today - date_in_past

    past_days = delta.days
    if past_days < 1:
        past_seconds = delta.seconds
        past_minutes = past_seconds / 60
        if past_minutes < 1:
            past_seconds = round(past_seconds)
            time_ago = decOfNum(past_seconds, ['секунду', 'секунды', 'секунд'])
            return "%s %s" % (past_seconds, time_ago)
        elif past_minutes > 60:
            # past more than hour and less than day
            past_hours = past_minutes / 60
            past_hours = round(past_hours)
            time_ago = decOfNum(past_hours, ['час', 'часа', 'часов'])
            return "%s %s" % (past_hours, time_ago)
        else:
            past_minutes = round(past_minutes)
            time_ago = decOfNum(past_minutes, ['минуту', 'минуты', 'минут'])
            return "%s %s" % (past_minutes, time_ago)
    elif past_days > 30:
        past_months = (12 * today.year + today.month) - (12 * date_in_past.year + date_in_past.month)
        past_months = round(past_months)
        time_ago = decOfNum(past_months, ['месяц', 'месяца', 'месяцев'])
        return "%s %s" % (past_months, time_ago)
    else:
        past_days = round(past_days)
        time_ago = decOfNum(past_days, ['день', 'дня', 'дней'])
        return "%s %s" % (past_days, time_ago)


@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now().replace(microsecond=0).isoformat()}
