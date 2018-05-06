import hashlib
import logging
import uuid
from functools import wraps

from flask import Blueprint, request, render_template, \
    g, session, redirect, url_for, jsonify
from werkzeug.security import check_password_hash

from app import user_service
from app.models.exception import UserException, UserNotFoundException, DFNError, APIException
from app.models import AjaxResponse


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


# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')


@mod_auth.route('/signin', methods=['GET', 'POST'])
def signin():
    logging.info('signin method')
    r = AjaxResponse(success=True)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email is None or email == '':
            r.set_failed()
            r.add_error(DFNError.USER_LOGIN_NOT_EXIST)
        elif password is None or password == '':
            r.set_failed()
            r.add_error(DFNError.USER_LOGIN_BAD_PASSWORD)
        else:
            try:
                user_json = user_service.get_user_by_email(email=email)
            except UserNotFoundException as e:
                r.set_failed()
                r.add_error(DFNError.USER_LOGIN_NOT_EXIST)
                resp = jsonify(r.serialize())
                resp.code = 404
                return resp
            except UserException as e:
                r.set_failed()
                r.add_error(DFNError.USER_UNKNOWN_ERROR)
                resp = jsonify(r.serialize())
                resp.code = 500
                return resp
            is_ok = check_password_hash(user_json['password'], password)
            if not is_ok:
                r.set_failed()
                r.add_error(DFNError.USER_LOGIN_BAD_PASSWORD)
            else:
                authorize_user(user_json=user_json)
                r.set_success()
        resp = jsonify(r.serialize())
        resp.code = 200
        return resp
    else:
        return render_template('auth/signin.html', code=200)


@mod_auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        r = AjaxResponse(success=True)

        email = request.form['email']
        password = request.form['password']

        try:
            # try to find user by username
            user_by_email = user_service.get_user_by_email(email=email)
            if user_by_email is not None:
                r.add_error(DFNError.USER_SIGNUP_EXIST)
                resp = jsonify(r)
                resp.code = 200
                return resp
        except APIException as e:
            logging.error("APIException", e)
            return render_template("errors/%s.html" % e.http_code, code=e.http_code)

        # we did not find any user by email fields, let's create it
        m = hashlib.md5()
        st = password.encode('utf-8')
        m.update(st)
        pwd = m.hexdigest()

        user_dict = {
            'email': email,
            'password': pwd,
        }

        try:
            user = user_service.create_user(user_dict=user_dict)
        except APIException as e:
            logging.error("APIException", e)
            return render_template("errors/%s.html" % e.http_code, code=e.http_code)

        authorize_user(user_json=user)

        resp = jsonify(r)
        resp.code = 200
        return resp
    else:
        return render_template('auth/signup.html', code=200)


@mod_auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logging.info('logout method')
    session.clear()
    g.user = None
    return redirect(url_for('index.index'))
