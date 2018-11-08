import codecs
import logging
import smtplib
import sys
from email.mime.text import MIMEText
from enum import Enum
from smtplib import SMTPException
from typing import Optional

import requests
from flask_babel import _
from werkzeug.security import generate_password_hash

from app.cache import CacheService
from app.models.rrn_service import RRNServiceType

sys.path.insert(0, '../rest_api_library')
from rest import RESTService, APIException
from response import APIResponse
from utils import gen_sec_token


class EmailMessageType(Enum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        return obj

    def __init__(self, sid, subject, html_template_name):
        self.sid = sid
        self.subject = subject
        self.html_template = html_template_name

    TRIAL = (0, "%s %s" % (_('Welcome to'), _('Railroad Network Services')), 'trial.html')
    NEW_SUB = (1, "%s %s" % (_('Welcome to'), _('Railroad Network Services')), 'trial.html')


class EmailService(object):
    __version__ = 1

    logger = logging.getLogger(__name__)

    __smtp_server = None
    __server = None
    __port = None

    __sender = None
    __reciever = None

    __marker = "AUNIQUEMARKER"

    __templates_path = None

    def __init__(self, smtp_server: str, smtp_port: int, smtp_username: str, smtp_password: str, from_name: str,
                 from_email: str, templates_path: str):

        self.logger.debug(f"{self.__class__}: __init__ method smtp_server: {smtp_server}, smtp_port: {smtp_port}, "
                          f"smtp_username: {smtp_username}, smtp_password: {smtp_password}, from_name: {from_name}, "
                          f"from_email: {from_email}, templates_path: {templates_path}")
        self.__server = smtp_server
        self.__port = smtp_port
        self.__username = smtp_username
        self.__password = smtp_password

        self.__from_name = from_name
        self.__from_email = from_email

        self.__templates_path = templates_path

    def send_trial_email(self, to_name: str, to_email: str) -> bool:
        self.logger.debug(
            f"{self.__class__}: send_trial_email method with parameters to_name: {to_name}, to_email: {to_email}")
        email_str = self.__prepare_trial_email(to_name=to_name, to_email=to_email)
        return self.__send_message(to_email=to_email, email_str=email_str)

    def send_new_sub_email(self, to_name: str, to_email: str, sub_name: str) -> bool:
        self.logger.debug(
            f"{self.__class__}: send_new_sub_email method with parameters to_name: {to_name}, to_email: {to_email}, "
            f"sub_name: {sub_name}")
        email_str = self.__prepare_new_subscription_email(to_name=to_name, to_email=to_email, sub_name=sub_name)
        return self.__send_message(to_email=to_email, email_str=email_str)

    def __send_message(self, to_email: str, email_str: str) -> bool:
        self.logger.debug(
            f"{self.__class__}: __send_message method with parameters to_name: {to_email}, to_email: {email_str}")
        try:
            is_connected = self.__connect()
            if not is_connected:
                self.logger.error("not connected to SMTP. error")
                return False
            self.logger.info("call sendmail method")
            self.__smtp_server.sendmail(self.__from_email, to_email, email_str)
            self.logger.info("quit")
            self.__smtp_server.quit()
            self.logger.info("email successfully sent to %s" % to_email)
            return True
        except SMTPException as e:
            self.logger.error("unable to send email to %s" % to_email, e)
            return False

    def __prepare_new_subscription_email(self, to_name: str, to_email: str, sub_name: str) -> str:
        self.logger.debug(
            f"{self.__class__}: __prepare_new_subscription_email method with parameters to_name: {to_name}, "
            f"to_email: {to_email}, sub_name: {sub_name}")

        self.logger.info("reading trial html template")
        f = codecs.open("%s/%s" % (self.__templates_path, EmailMessageType.NEW_SUB.html_template), 'r')
        email_html_text = str(f.read())

        self.logger.info("replacing anchors in HTML")
        email_html_text = email_html_text.replace("@ticket@", _('TRIAL_EMAIL_TICKET'))
        email_html_text = email_html_text.replace("@welcome_to@", _('TRIAL_EMAIL_WELCOME'))
        email_html_text = email_html_text.replace("@RNS@", _('RNS'))
        email_html_text = email_html_text.replace("@hello_user@", _('Hello'))
        email_html_text = email_html_text.replace("@trial_ready@", _('NEW_SUB_BUY_FACT') + sub_name)
        email_html_text = email_html_text.replace("@thank_you@", _('NEW_SUB_EMAIL_THANKS'))
        email_html_text = email_html_text.replace("@one_letter@", _('NEW_SUB_PAYMENT_INFORM'))
        email_html_text = email_html_text.replace("@service_ready@", '')
        email_html_text = email_html_text.replace("@unsubscribe_user_url@", '')
        email_html_text = email_html_text.replace("@unsubscribe@", '')

        self.logger.info("preparing email object")
        email_str = self.__prepare_email(to_name=to_name, to_email=to_email, subject=EmailMessageType.NEW_SUB.subject,
                                         html_message=email_html_text)
        return email_str

    def __prepare_trial_email(self, to_name: str, to_email: str) -> str:
        self.logger.debug(
            f"{self.__class__}: __prepare_trial_email method with parameters to_name: {to_email}, to_email: {to_email}")

        self.logger.info("reading trial html template")
        f = codecs.open("%s/%s" % (self.__templates_path, EmailMessageType.TRIAL.html_template), 'r')
        email_html_text = str(f.read())

        self.logger.info("replacing anchors in HTML")
        email_html_text = email_html_text.replace("@ticket@", _('TRIAL_EMAIL_TICKET'))
        email_html_text = email_html_text.replace("@welcome_to@", _('TRIAL_EMAIL_WELCOME'))
        email_html_text = email_html_text.replace("@RNS@", _('RNS'))
        email_html_text = email_html_text.replace("@hello_user@", _('Hello'))
        email_html_text = email_html_text.replace("@trial_ready@", _('TRIAL_EMAIL_SUBSCRIPTION_READY'))
        email_html_text = email_html_text.replace("@thank_you@", _('TRIAL_EMAIL_THANKS'))
        email_html_text = email_html_text.replace("@one_letter@", _('TRIAL_EMAIL_ONE_EMAIL_IN_A_WEEK'))
        email_html_text = email_html_text.replace("@service_ready@", _('TRIAL_EMAIL_INFORM'))
        # TODO URL
        email_html_text = email_html_text.replace("@unsubscribe_user_url@",
                                                  'https://rroadvpn.net/unsubscribe?email=%s' % to_email)
        email_html_text = email_html_text.replace("@unsubscribe@", _('unsubscribe'))

        self.logger.info("preparing email object")
        email_str = self.__prepare_email(to_name=to_name, to_email=to_email, subject=EmailMessageType.TRIAL.subject,
                                         html_message=email_html_text)
        return email_str

    def __prepare_email(self, to_name, to_email, subject, html_message) -> str:
        self.logger.debug(f"{self.__class__}: __prepare_email method with parameters to_name: {to_name}, "
                          f"to_email: {to_email}, subject: {subject}, html_message: {html_message}")

        html_email = MIMEText(html_message, 'html')
        html_email['From'] = '%s <%s>' % (self.__from_name, self.__from_email)
        html_email['To'] = '%s <%s>' % (to_name, to_email)
        html_email['Subject'] = subject

        email_str = html_email.as_string()
        return email_str

    def __connect(self) -> bool:
        self.logger.debug('__connect method')
        try:
            self.logger.info("connecting to SMTP server")
            self.__smtp_server = smtplib.SMTP_SSL(host=self.__server, port=self.__port)
            self.logger.info("login to SMTP server")
            self.__smtp_server.login(user=self.__username, password=self.__password)
            return True
        except SMTPException as e:
            self.logger.error("unable to connect or login", e)
            return False


class RRNOrdersAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def get_order(self, code: int = None, suuid: str = None) -> dict:
        self.logger.debug(f"{self.__class__}: get_order method with parameters code: {code}, suuid: {suuid}")
        if suuid:
            url = f"{self._url}/uuid/{suuid}"
        elif code:
            url = f"{self._url}/code/{code}"
        else:
            raise KeyError

        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        api_response = self._get(url=url, headers=headers)
        return api_response.data

    def create_order(self, status: int) -> dict:
        self.logger.debug(f"{self.__class__}: create_order method with parameters status: {status}")
        data = {
            'status_id': status
        }

        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        api_response = self._post(data=data, headers=headers)
        if 'Location' in api_response.headers:
            api_response = self._get(url=api_response.headers.get('Location'), headers=headers)
            return api_response.data
        else:
            self.logger.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def update_order(self, order_json: dict):
        self.logger.debug(f"{self.__class__}: update_order method with parameters order_json: {order_json}")
        url = f"{self._url}/{order_json['uuid']}"
        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        self._put(url=url, data=order_json, headers=headers)

    def get_order_payments(self, order_uuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_order_payments method with parameters order_uuid: {order_uuid}")
        url = f"{self._url}/{order_uuid}/payments"
        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        return self._get(url=url, headers=headers)


class RRNUsersAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, api_url: str, resource_name: str):
        super().__init__(api_url=api_url, resource_name=resource_name)

    def create_user(self, email, password) -> dict:
        self.logger.debug(f"{self.__class__}: create_user method with parameters email: {email}, password: {password}")

        self.logger.debug(f"{self.__class__}: generate password hash")
        pwd = generate_password_hash(password)
        self.logger.debug(f"{self.__class__}: generated hash: {pwd}")

        user_json = {
            'email': email,
            'password': pwd,
        }
        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        api_response = self._post(data=user_json, headers=headers)
        if 'Location' in api_response.headers:
            headers = {
                'X-Auth-Token': gen_sec_token()
            }
            api_response = self._get(url=api_response.headers.get('Location'), headers=headers)
            return api_response.data
        else:
            self.logger.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def update_user(self, user_json: dict):
        self.logger.debug(f"{self.__class__}: update_user method with parameters user_json: {user_json}")
        url = f"{self._url}/{user_json.get('uuid')}"
        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        self._put(url=url, data=user_json, headers=headers)

    def get_user(self, uuid: str = None, email: str = None, pin_code: int = None) -> dict:
        self.logger.debug(
            f"{self.__class__}: get_user method with parameters uuid: {uuid}, email: {email}, pin_code: {pin_code}")
        if uuid:
            url = f"{self._url}/uuid/{uuid}"
        elif email:
            url = f"{self._url}/email/{email}"
        elif pin_code:
            url = f"{self._url}/pincode/{pin_code}"
        else:
            raise KeyError
        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        api_response = self._get(url=url, headers=headers)
        return api_response.data

    def get_user_subscription(self, user_uuid: str, subscription_uuid: str) -> dict:
        self.logger.debug(f"{self.__class__}: get_user_subscription with parameters user_uuid: {user_uuid}, "
                          f"subscription_uuid: {subscription_uuid}")
        url = f"{self._url}/{user_uuid}/subscriptions/{subscription_uuid}"
        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        api_response = self._get(url=url, headers=headers)
        return api_response.data

    def get_user_subscriptions(self, user_uuid: str) -> dict:
        self.logger.debug(f"{self.__class__}: get_user_subscriptions method with parameters user_uuid: {user_uuid}")
        url = f"{self._url}/{user_uuid}/services"
        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        api_response = self._get(url=url, headers=headers)
        return api_response.data

    def create_user_subscription(self, user_uuid: str, status_id: int, subscription_id: int, order_uuid: str) -> dict:
        self.logger.debug(
            f"create_user_subscription method with parameters user_uuid: {user_uuid}. user_uuid: {user_uuid}, "
            f"subscription_id: {subscription_id}, order_uuid: {order_uuid}")
        data = {
            'user_uuid': user_uuid,
            'status_id': status_id,
            'subscription_id': subscription_id,
            'order_uuid': order_uuid,
        }
        url = f"{self._url}/{user_uuid}/subscriptions"
        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        api_response = self._post(data=data, url=url, headers=headers)
        if 'Location' in api_response.headers:
            api_response = self._get(url=api_response.headers.get('Location'))
            return api_response.data
        else:
            self.logger.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def update_user_service(self, user_service_json: dict):
        self.logger.debug(
            f"{self.__class__}: update_user_subscription method with parameters subscription_json: {user_service_json}")
        url = f"{self._url}/{user_service_json['user_uuid']}/services/{user_service_json['uuid']}"
        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        self._put(data=user_service_json, url=url, headers=headers)

    def get_user_devices(self, user_uuid: str) -> dict:
        self.logger.debug(f"{self.__class__}: get_user_devices method with parameters user_uuid: {user_uuid}")
        url = f"{self._url}/{user_uuid}/devices"
        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        api_response = self._get(url=url, headers=headers)
        return api_response.data

    def get_user_device(self, user_uuid: str, device_uuid: str):
        self.logger.debug(
            f"{self.__class__}: get_user_device method with parameters user_uuid: {user_uuid}, device_uuid: {device_uuid}")
        url = f"{self._url}/{user_uuid}/devices/{device_uuid}"
        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        api_response = self._get(url=url, headers=headers)
        return api_response

    def delete_user_device(self, user_uuid: str, device_uuid: str):
        self.logger.debug(
            f"delete_user_device method with parameters user_uuid: {user_uuid}, device_uuid: {device_uuid}")
        url = f"{self._url}/{user_uuid}/devices/{device_uuid}"
        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        self._delete(url=url, headers=headers)

    def change_status_user_device(self, user_uuid: str, device_uuid: str, status: bool):
        self.logger.debug(
            f"change_status_user_device method with parameters user_uuid: {user_uuid}, device_uuid: {device_uuid}, "
            f"status: {status}")
        url = f"{self._url}/{user_uuid}/devices/{device_uuid}"
        api_response = self.get_user_device(user_uuid=user_uuid, device_uuid=device_uuid)
        user_device = api_response.data
        user_device['is_active'] = status
        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        self._put(url=url, data=api_response.data, headers=headers)

    def get_user_vpn_servers(self, user_uuid: str):
        self.logger.debug(f"get_user_vpn_servers method with parameters user_uuid: {user_uuid}")
        url = f"{self._url}/{user_uuid}/servers"
        headers = {
            'X-Auth-Token': gen_sec_token()
        }
        api_response = self._get(url=url, headers=headers)
        return api_response.data


class RRNBillingAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def get_services(self) -> dict:
        self.logger.debug(f"{self.__class__}: get_services method")
        headers = {
            'X-Auth-Token': gen_sec_token()
        }

        api_response = self._get(headers=headers)
        return api_response.data


class RRNServicesService(object):
    __version__ = 1

    logger = logging.getLogger(__name__)

    _billing_service = None
    _cache_service = None

    def __init__(self, billing_service: RRNBillingAPIService, cache_service: CacheService):
        self._billing_service = billing_service
        self._cache_service = cache_service

    def get_services(self) -> list:
        self.logger.debug(f"{self.__class__}: get_services method")
        self.logger.info("Check services in cache")
        services = self._cache_service.get(key='services')
        self.logger.info("Is services exists in cache: %s" % services is not None)
        if services is None:
            self.logger.info("There are no services in cache. Call billing service")
            self.__update_cache_services()
            return self._cache_service.get(key='services')
        return services

    def get_services_by_type(self, service_type: RRNServiceType) -> list:
        self.logger.debug(f"{self.__class__}: get_services_by_type method with parameters service_type: {service_type}")
        self.logger.info("Check services in cache")
        services = self._cache_service.get(key=f'services_{service_type.sid}')
        self.logger.info("Is services exists in cache: %s" % services is not None)
        if services is None:
            self.logger.info("There are no services in cache. Call billing service")
            self.__update_cache_services()
            services = self._cache_service.get(key=f'services_{service_type.sid}')

        return services

    def get_services_dict(self) -> dict:
        self.logger.info("Check services_dict in cache")
        services_dict = self._cache_service.get(key='services_dict')
        self.logger.info("Is services dict exists in cache: %s" % services_dict is not None)
        if services_dict is None:
            self.logger.info("There are no services_dict in cache.")
            self.__update_cache_services()
            return self._cache_service.get(key='services_dict')
        return services_dict

    def __update_cache_services(self):
        self.logger.debug(
            f"{self.__class__}: __update_cache_subscriptions method")
        try:
            self.logger.info("Call billing service")
            services = self._billing_service.get_services()
            self.logger.info(f"Save services in cache. Size: {len(services)}")
            self._cache_service.set('services', services)
            for service in services:
                service_type_id = f"services_{service['type']['id']}"
                self._cache_service.add(service_type_id, service)
        except APIException as e:
            self.logger.error("Error when call billing service")
            self.logger.error(e)


class UserDiscoveryResponse(object):
    __version__ = 1

    logger = logging.getLogger(__name__)

    ip = None
    city = None
    country_name = None
    country_code = None
    continent_name = None
    latitude = None
    longitude = None
    isp = None
    is_tor = False
    is_proxy = False
    is_anonymous = False

    status = False

    def __init__(self, json):
        self.ip = json.get('ip', '???')
        self.city = json.get('city', '???')
        if json.get('primary', False):
            self.country_name = json.get('country_name', '???')
            self.country_code = json.get('country_code', '')
            self.continent_name = json.get('continent_name', '???')
            self.continent_code = json.get('continent_code', '')
            self.latitude = json.get('latitude', 0)
            self.longitude = json.get('longitude', 0)
            self.isp = json.get('organisation', '???')
            self.is_tor = json.get('is_tor', False)
            self.is_proxy = json.get('is_proxy', False)
            self.is_anonymous = json.get('is_anonymous', False)
        else:
            self.country_name = json.get('country', '???')
            self.country_code = json.get('countryCode', '')
            self.latitude = json.get('lat', 0)
            self.longitude = json.get('lon', 0)
            self.isp = json.get('isp', '???')

        # TODO make status true if uses railroad network
        self.status = False


class UserDiscoveryService(object):
    __version__ = 1

    logger = logging.getLogger(__name__)

    __cache = {}

    __headers = {
        'Accept': 'application/json'
    }

    def __init__(self):
        pass

    def discover_ip(self, ip) -> Optional[UserDiscoveryResponse]:
        # TODO expire cache entry
        cached_json = self.__cache.get(ip, None)
        if cached_json is None:
            req_json = self.__discover_ip(ip=ip)
            return UserDiscoveryResponse(json=req_json) if req_json is not None else None
        else:
            return UserDiscoveryResponse(json=cached_json)

    def __discover_ip(self, ip: str):
        url1 = 'https://api.ipdata.co/%s?api-key=9eaf33b7865b0441717e0c85ba6373f63e4178ab5abbcdbf0815441f' % ip
        url2 = 'http://ip-api.com/json/%s' % ip
        try:
            req = requests.get(url=url1, headers=self.__headers, timeout=0.5)
            if req.ok:
                req_json = req.json()
                req_json['primary'] = True
                return req_json
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
            try:
                req = requests.get(url=url2, headers=self.__headers, timeout=1)
                if req.ok:
                    req_json = req.json()
                    req_json['primary'] = False
                    return req_json
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
                return None

        return None
