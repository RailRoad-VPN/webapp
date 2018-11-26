import json
import logging
import sys
from http import HTTPStatus
from uuid import UUID

from flask import Blueprint, request, render_template, \
    session, jsonify, redirect, url_for, abort

from app import rrn_usersapi_service, rrn_ordersapi_service, app_config, rrn_servicesapi_service, email_service, \
    RRNServiceType, user_policy
from app.flask_utils import _add_language_code, _pull_lang_code, authorize_user, login_required
from app.models import AjaxResponse, AjaxError
from app.models.exception import DFNError, UserPolicyException
from app.models.order_status import OrderStatus
from app.models.user_service_status import UserServiceStatus
from utils import check_uuid

sys.path.insert(0, '../rest_api_library')
from rest import APIException, APINotFoundException

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_order = Blueprint('order', __name__, url_prefix='/<lang_code>/order')

logger = logging.getLogger(__name__)


@mod_order.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_order.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_order.route('', methods=['GET'])
def order_page():
    logger.info('order_page method')

    if 'order' not in session or session.get('order', None) is None:
        # create new order
        try:
            logger.info("create order")
            order_json = rrn_ordersapi_service.create_order(status=OrderStatus.NEW.sid)
            session['order'] = order_json
            logger.debug("order created: %s" % order_json)
        except APIException as e:
            logger.debug(e.serialize())
            abort(500)

    subscriptions = user_policy.get_user_available_services()
    logger.debug("got services. Size: %s" % len(subscriptions))

    return render_template('order/order.html', subscriptions=subscriptions, code=200)


@mod_order.route('/submit', methods=['POST'])
def submit_order() -> bool:
    logger.info('submit_order method')

    r = AjaxResponse(success=True)

    email = request.form.get('email', None)
    password = request.form.get('password', None)
    password_repeat = request.form.get('password_repeat', None)

    is_trial_available = False
    order_uuid = session.get('order').get('uuid')
    service_id = session.get('order').get('service_id')

    if 'user' not in session:
        is_trial_available = True
        try:
            logger.debug('create user')
            user_json = user_policy.create_user(email=email, password=password, password_repeat=password_repeat)
            logger.debug('authorise user in system')
            authorize_user(user_json=user_json)
        except UserPolicyException as e:
            r.set_failed()
            error = AjaxError(message=e.error, code=e.error_code, developer_message=e.developer_message)
            r.add_error(error)
            resp = jsonify(r.serialize())
            resp.code = HTTPStatus.BAD_REQUEST
            return resp
    else:
        user_json = session.get('user')
        is_trial_available = user_policy.is_trial_available_for_service(user_uuid=user_json['uuid'],
                                                                        service_id=service_id)
        # TODO if trial is not available check payment

    user_uuid = user_json.get('uuid')
    user_email = user_json.get('email')

    try:
        user_policy.create_user_service(user_uuid=user_uuid, service_id=service_id, order_uuid=order_uuid,
                                        is_trial=is_trial_available)
    except UserPolicyException as e:
        r.set_failed()
        error = AjaxError(message=e.error, code=e.error_code, developer_message=e.developer_message)
        r.add_error(error)
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.BAD_REQUEST
        return resp

    logger.debug('get service')
    service = rrn_servicesapi_service.get_service_by_id(service_id=service_id)

    logger.debug('send user email')
    email_service.send_new_sub_email(to_name=user_email, to_email=user_email, sub_name=service.get('service_name'))

    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp


@mod_order.route('/<int:order_code>/payment')
@login_required
def get_order_payment(order_code: int):
    logger.info('get_order_payment method')

    r = AjaxResponse(success=True)

    try:
        order_json = rrn_ordersapi_service.get_order(code=order_code)
    except APIException as e:
        logger.debug(e.serialize())
        r.set_failed()
        error = AjaxError(message=DFNError.UNKNOWN_ERROR_CODE.message,
                          code=DFNError.UNKNOWN_ERROR_CODE.code,
                          developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
        r.add_error(error)
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp

    is_order_success = order_json['status_id'] == OrderStatus.SUCCESS.sid

    order_r = {
        'is_success': is_order_success,
        'code': order_code
    }

    if is_order_success:
        api_response = rrn_ordersapi_service.get_order_payments(order_uuid=order_json['uuid'])
        order_r['payments'] = api_response.data

    r.add_data('order', order_r)
    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp


@mod_order.route('/choose_pack', methods=['POST'])
def choose_service_pack() -> bool:
    logger.info('choose_service_pack method')

    r = AjaxResponse(success=True)

    data = json.loads(request.data)

    service_id = data.get('service_id', None)
    if service_id is None:
        r.set_failed()
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.BAD_REQUEST
    else:
        session['order']['service_id'] = service_id
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
    return resp
