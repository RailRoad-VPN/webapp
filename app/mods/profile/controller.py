import datetime
import logging
from http import HTTPStatus

from flask import Blueprint, render_template, session, jsonify, request, json

from app import rrn_usersapi_service, rrn_servicesapi_service, app_config, rrn_ordersapi_service, \
    rrn_userserverconfigurationsapi_service, RRNServiceType, rrn_vpnserversapi_service
from app.flask_utils import login_required, _pull_lang_code, _add_language_code
from app.models import AjaxResponse
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

    user_uuid = session.get('user').get('uuid')

    try:
        user_services = rrn_usersapi_service.get_user_services(user_uuid=user_uuid)
    except APIException:
        user_services = []
    services = rrn_servicesapi_service.get_services_by_type(service_type=RRNServiceType.VPN_SUBSCRIPTION)
    if services is None:
        pass
    else:
        services = {services[i]['id']: services[i] for i in range(0, len(services))}
        for us in user_services:
            sub = services.get(us['service_id'])
            us['service'] = sub

            us_order_uuid = us['order_uuid']
            us_order = rrn_ordersapi_service.get_order(suuid=us_order_uuid)
            api_response = rrn_ordersapi_service.get_order_payments(order_uuid=us_order['uuid'])
            us_order['payments'] = api_response.data

            us['order'] = us_order

    try:
        user_device_list = rrn_usersapi_service.get_user_devices(user_uuid=user_uuid)
    except (APIException, APINotFoundException) as e:
        user_device_list = []

    user_vpn_servers = None
    vpn_config_rdy = None
    if services is not None and (len(user_device_list) > 0 or ('pin_code' in session['user']
                                                               and session['user']['pin_code'] is not None)):
        generate_available = True
        try:
            user_vpn_servers = rrn_usersapi_service.get_user_vpn_servers(user_uuid=user_uuid)
        except (APIException, APINotFoundException) as e:
            user_vpn_servers = []
    else:
        generate_available = True
        try:
            random_server_uuid = rrn_vpnserversapi_service.get_random_server_uuid(user_uuid=user_uuid)
            vpn_config_rdy = rrn_userserverconfigurationsapi_service.get_vpn_configurations_ready(user_uuid=user_uuid,
                                                                                                  any_server_uuid=random_server_uuid)
            for val in vpn_config_rdy.values():
                if not val:
                    generate_available = False
                    break
        except (APIException, APINotFoundException) as e:
            logger.error(e)

    return render_template('profile/profile.html', code=HTTPStatus.OK, user_services=user_services,
                           vpn_config_rdy=vpn_config_rdy, generate_available=generate_available,
                           user_devices=user_device_list, user_vpn_servers=user_vpn_servers)


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
    updated_user_json = rrn_usersapi_service.get_user(uuid=user_session['uuid'])

    logger.debug("Updater user in session")
    session['user'] = updated_user_json

    pin_code = updated_user_json.get('pin_code', None)
    pin_code_expire_date = updated_user_json.get('pin_code_expire_date', None)
    is_pin_code_activated_var = updated_user_json.get('is_pin_code_activated', None)

    if pin_code is not None and pin_code_expire_date is not None and not is_pin_code_activated_var:
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

    # we try to get user by pin code. if we found - we have to generate new pin code
    ok = False
    while not ok:
        try:
            logger.debug('Generate PIN code')
            pin_code = random_with_n_digits(4)
            logger.debug(f"PIN code: {pin_code}")
            logger.debug("Searching user by new generated pin code")
            rrn_usersapi_service.get_user(pin_code=pin_code)
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

    rrn_usersapi_service.update_user(user_json=updated_user_json)

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


@mod_profile.route('/is_pin_code_activated', methods=['GET'])
@login_required
def is_pin_code_activated():
    logger.info('is_pin_code_activated method')

    r = AjaxResponse(success=True)

    updated_user_json = rrn_usersapi_service.get_user(uuid=session['user']['uuid'])
    session['user'] = updated_user_json

    is_pin_code_activated_var = updated_user_json.get('is_pin_code_activated')

    r.add_data('is_pin_code_activated', is_pin_code_activated_var)
    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp


@mod_profile.route('/user_devices/delete', methods=['POST'])
@login_required
def delete_user_device():
    logger.info("delete_user_device method")

    r = AjaxResponse(success=True)

    data = json.loads(request.data)

    device_uuid = data.get('device_uuid')

    rrn_usersapi_service.delete_user_device(user_uuid=session.get('user').get('uuid'), device_uuid=device_uuid)

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

    rrn_usersapi_service.change_status_user_device(user_uuid=session['user']['uuid'], device_uuid=device_uuid,
                                                   status=status)

    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp
