import json
import logging
import sys
from http import HTTPStatus
from uuid import UUID

from flask import Blueprint, request, render_template, \
    session, jsonify, redirect, url_for, abort

from flask_babel import _

from app import rrn_usersapi_service, rrn_ordersapi_service, app_config, rrn_servicesapi_service, email_service, \
    RRNServiceType, user_policy, order_policy
from app.flask_utils import _add_language_code, _pull_lang_code, authorize_user, login_required
from app.models import AjaxResponse, AjaxError
from app.models.exception import DFNError, UserPolicyException, OrderPolicyException
from app.models.order_status import OrderStatus
from app.models.user_service_status import UserServiceStatus

sys.path.insert(0, '../rest_api_library')
from api import APIException, APINotFoundException
from utils import check_uuid

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
            order_json = order_policy.create_order()
            session['order'] = order_json
            logger.debug("order created: %s" % order_json)
        except OrderPolicyException as e:
            logger.error("OrderPolicyException: {}", e)
            abort(500)

    services = user_policy.get_user_available_services()
    logger.debug("got services. Size: %s" % len(services))

    return render_template('order/order.html', services=services, code=200)


@mod_order.route('/submit', methods=['POST'])
def submit_order() -> bool:
    logger.info('submit_order method')

    r = AjaxResponse(success=True)

    logger.debug("get parameters from request form")
    email = request.form.get('email', None)
    logger.debug(f"email: {email}")
    password = request.form.get('password', None)
    logger.debug(f"password: {password}")
    password_repeat = request.form.get('password_repeat', None)
    logger.debug(f"password_repeat: {password_repeat}")
    service_id = request.form.get('service_id', None)
    logger.debug(f"service_id: {service_id}")

    logger.debug("get parameters from session")
    order = session.get("order")
    logger.debug(f"session order: {order}")
    order_uuid = order.get('uuid')
    logger.debug(f"order_uuid: {order_uuid}")

    if not service_id:
        service_id = order.get('service_id', None)

    if service_id is None:
        r.set_failed()
        error = AjaxError(message=_('System error. Please write us support@rroadvpn.net'), code='RRN-001',
                          developer_message="service id is None")
        r.add_error(error)
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.BAD_REQUEST
        return resp

    logger.debug('get service by service_id')
    service = rrn_servicesapi_service.get_service_by_id(service_id=service_id)
    logger.debug(f"service: {service}")

    is_trial_available = service.get('is_trial')

    if 'user' not in session:
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

    # TODO if trial is not available we have to check payment, check order, change status of order

    user_uuid = user_json.get('uuid')
    user_email = user_json.get('email')

    order_json = session.get('order')

    try:
        updated_order = order_policy.finish_order(order_json=order_json)
        session['order'] = updated_order
    except OrderPolicyException as e:
        logger.error("OrderPolicyException: {}", e)
        abort(500)

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

    logger.debug("get service_id")
    service_id = data.get('service_id', None)
    logger.debug(f"service_id: {service_id}")
    if service_id is None:
        logger.debug(f"service_id is None")
        r.set_failed()
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.BAD_REQUEST
    else:
        logger.debug(f"save service_id to session")
        session['order']['service_id'] = service_id
        logger.debug(f"service_id from session: {session['order']['service_id']}")

        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
    return resp
