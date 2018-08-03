import datetime
import logging
from http import HTTPStatus

from flask import Blueprint, render_template, session, jsonify, request, url_for, json

from app import rrn_user_service, subscription_service, app_config, rrn_orders_service
from app.flask_utils import login_required, _pull_lang_code, _add_language_code
from app.models import AjaxResponse, AjaxError
from app.models.exception import DFNError
from rest import APINotFoundException, APIException

mod_profile = Blueprint('profile', __name__, url_prefix='/<lang_code>/profile')

logger = logging.getLogger(__name__)


@mod_profile.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_profile.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_profile.route('/', methods=['GET', 'POST'])
@login_required
def profile_page():
    logger.info('profile_page method')
    user_subscriptions = rrn_user_service.get_user_subscriptions(user_uuid=session['user']['uuid'])
    subscriptions_dict = subscription_service.get_subscriptions_dict(lang_code=session['lang_code'])
    for us in user_subscriptions:
        sub = subscriptions_dict.get(us['subscription_id'])
        us['subscription'] = sub

        us_order_uuid = us['order_uuid']
        us_order = rrn_orders_service.get_order(suuid=us_order_uuid)
        us['order'] = us_order

    try:
        user_devices = rrn_user_service.get_user_devices(user_uuid=session['user']['uuid'])
    except (APIException, APINotFoundException) as e:
        user_devices = None

    return render_template('profile/profile.html', code=HTTPStatus.OK, user_subscriptions=user_subscriptions,
                           user_devices=user_devices)


@mod_profile.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_profile.route('/generate_pincode', methods=['GET'])
@login_required
def generate_pincode():
    logger.info('generate_pincode method')

    r = AjaxResponse(success=True)

    logger.debug('Check PIN code')
    need_gen = True
    now = datetime.datetime.now()

    logger.debug('Get user from session')
    user_session = session['user']

    logger.debug("Refresh user from service")
    updated_user_json = rrn_user_service.get_user(uuid=user_session['uuid'])

    logger.debug("Updater user in session")
    session['user'] = updated_user_json

    pin_code = updated_user_json.get('pin_code', None)
    pin_code_expire_date = updated_user_json.get('pin_code_expire_date', None)
    is_pin_code_activated = updated_user_json.get('is_pin_code_activated', None)

    if pin_code is not None and pin_code_expire_date is not None and not is_pin_code_activated:
        import dateutil.parser
        pin_code_expire_date = dateutil.parser.parse(pin_code_expire_date)
        if now > pin_code_expire_date:
            need_gen = True
        else:
            delta = pin_code_expire_date - now
            delta_minutes = delta.seconds / 60
            if delta_minutes > 5:
                need_gen = False

    if not need_gen:
        delta = pin_code_expire_date - now

        r.add_data('pin_code', pin_code)
        r.add_data('seconds', delta.seconds)
        r.set_success()
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp

    logger.debug('Generate PIN code')
    pin_code = random_with_n_digits(4)
    logger.debug('PIN code: %s' % pin_code)

    # we try to get user by pin code. if we found - we have to generate new pin code
    ok = False
    while not ok:
        try:
            logger.debug('Generate PIN code')
            pin_code = random_with_n_digits(4)
            logger.debug(f"PIN code: {pin_code}")
            logger.debug("Searching user by new generated pin code")
            rrn_user_service.get_user(pin_code=pin_code)
            logger.debug("Found")
        except APIException:
            logger.debug("User not found")
            ok = True

    logger.debug('Generate PIN code expire date now + 30 min')
    pin_code_expire_date = datetime.datetime.now() + datetime.timedelta(minutes=30)
    logger.debug('PIN code expire date: %s' % pin_code_expire_date)

    updated_user_json['pin_code'] = pin_code
    updated_user_json['pin_code_expire_date'] = pin_code_expire_date.isoformat()
    updated_user_json['modify_reason'] = 'generate pin code'

    rrn_user_service.update_user(user_json=updated_user_json)

    delta = pin_code_expire_date - now

    r.add_data('pin_code', pin_code)
    r.add_data('seconds', delta.seconds)
    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp


def random_with_n_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    from random import randint
    return randint(range_start, range_end)


@mod_profile.route('/renew_sub', methods=['POST'])
@login_required
def renew_sub():
    logger.info('renew_sub method')

    r = AjaxResponse(success=True)

    data = json.loads(request.data)

    sub_id = data.get('sub_id', None)
    order_code = data.get('order_code', None)

    if sub_id is None or order_code is None:
        r.set_failed()
        error = AjaxError(message=DFNError.UNKNOWN_ERROR_CODE.message,
                          code=DFNError.UNKNOWN_ERROR_CODE.code,
                          developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
        r.add_error(error)
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp

    order = rrn_orders_service.get_order(code=order_code)
    session['order'] = order

    redirect_url = url_for('order.order', pack=sub_id)

    r.add_data('redirect_url', redirect_url)
    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp


@mod_profile.route('/is_pin_code_activated', methods=['GET'])
@login_required
def is_pin_code_activated():
    logger.info('is_pin_code_activated method')

    r = AjaxResponse(success=True)

    updated_user_json = rrn_user_service.get_user(uuid=session['user']['uuid'])
    session['user'] = updated_user_json

    is_pin_code_activated = updated_user_json['is_pin_code_activated']

    r.add_data('is_pin_code_activated', is_pin_code_activated)
    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp


@mod_profile.route('/user_devices/delete', methods=['POST'])
@login_required
def delete_user_device():
    logger.info("delete_user_device method")

    r = AjaxResponse(success=True)

    device_uuid = request.args.get('device_uuid')

    rrn_user_service.delete_user_device(user_uuid=session.get('user').get('uuid'), device_uuid=device_uuid)

    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp


@mod_profile.route('/user_devices/status', methods=['POST'])
@login_required
def change_status_user_device():
    logger.info("change_status_user_device method")

    r = AjaxResponse(success=True)

    data = json.loads(request.data)

    device_uuid = data.get('device_uuid')
    status = data.get('status')

    rrn_user_service.change_status_user_device(user_uuid=session['user']['uuid'], device_uuid=device_uuid, status=status)

    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp

# @mod_profile.route('/get_user_devices', methods=['GET'])
# @login_required
# def get_user_devices():
#     logger.info("get_user_devices method")
#
#     r = AjaxResponse(success=True)
#
#     user_devices = rrn_user_service.get_user_devices(user_uuid=session['user_uuid'])
#
#     r.add_data('user_devices', user_devices)
#     r.set_success()
#     resp = jsonify(r.serialize())
#     resp.code = HTTPStatus.OK
#     return resp
