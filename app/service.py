import logging
import sys
from http import HTTPStatus
from typing import Optional

import requests

from app.cache import CacheService
from app.models.order_status import OrderStatus

sys.path.insert(0, '../rest_api_library')
from rest import RESTService, APIException, APINotFoundException

logger = logging.getLogger(__name__)


class RRNOrdersAPIService(RESTService):
    __version__ = 1

    def get_order(self, code: int = None, suuid: str = None) -> dict:
        if suuid:
            url = '%s/uuid/%s' % (self._url, suuid)
        elif code:
            url = '%s/code/%s' % (self._url, code)
        else:
            raise KeyError
        api_response = self._get(url=url)

        if api_response.is_ok:
            return api_response.data
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def create_order(self, status: OrderStatus) -> dict:
        data = {
            'status_id': status.sid
        }
        api_response = self._post(data=data)
        if api_response.is_ok and 'Location' in api_response.headers:
            api_response = self._get(url=api_response.headers.get('Location'))
            if api_response.is_ok:
                return api_response.data
            else:
                logging.debug(api_response.serialize())
                raise APIException(http_code=api_response.code, errors=api_response.errors)
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def update_order(self, order_json: dict) -> bool:
        api_response = self._put(data=order_json)
        if api_response.is_ok and 'Location' in api_response.headers:
            api_response = self._get(url=api_response.headers.get('Location'))
            if api_response.is_ok:
                return api_response.data
            else:
                logging.debug(api_response.serialize())
                raise APIException(http_code=api_response.code, errors=api_response.errors)
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)


class RRNUsersAPIService(RESTService):
    __version__ = 1

    def __init__(self, api_url: str, resource_name: str):
        super().__init__(api_url=api_url, resource_name=resource_name)

    def create_user(self, email, password) -> dict:
        user_json = {
            'email': email,
            'password': password,
        }
        api_response = self._post(data=user_json, headers=self._headers)
        if api_response.is_ok and 'Location' in api_response.headers:
            api_response = self._get(url=api_response.headers.get('Location'))
            if api_response.is_ok:
                return api_response.data
            else:
                raise APIException(http_code=api_response.code, errors=api_response.errors)
        else:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def update_user(self, user_json: dict) -> bool:
        url = '%s/%s' % (self._url, user_json['uuid'])
        api_response = self._put(url=url, data=user_json, headers=self._headers)
        if api_response.is_ok:
            return True
        else:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def get_user(self, uuid: str = None, email: str = None) -> dict:
        if uuid:
            url = '%s/uuid/%s' % (self._url, uuid)
        elif email:
            url = '%s/email/%s' % (self._url, email)
        else:
            raise KeyError
        api_response = self._get(url=url)

        if api_response.is_ok:
            return api_response.data
        elif api_response.code == HTTPStatus.NOT_FOUND:
            logger.error(api_response.serialize())
            raise APINotFoundException(http_code=api_response.code, errors=api_response.errors)
        else:
            logger.error(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def get_user_subscription(self, user_uuid: str, subscription_uuid: str) -> dict:
        url = self._url + '/%s/subscriptions/%s' % (user_uuid, subscription_uuid)
        api_response = self._get(url=url)
        if api_response.is_ok:
            return api_response.data
        elif api_response.code == HTTPStatus.NOT_FOUND:
            raise APINotFoundException(http_code=api_response.code, errors=api_response.errors)
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def get_user_subscriptions(self, user_uuid: str) -> dict:
        url = self._url + '/%s/subscriptions' % (user_uuid)
        api_response = self._get(url=url)
        if api_response.is_ok:
            return api_response.data
        elif api_response.code == HTTPStatus.NOT_FOUND:
            raise APINotFoundException(http_code=api_response.code, errors=api_response.errors)
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def create_user_subscription(self, user_uuid: str, subscription_id: int, order_uuid: str) -> dict:
        data = {
            'user_uuid': user_uuid,
            'subscription_id': subscription_id,
            'order_uuid': order_uuid,
        }
        url = self._url + '/%s/subscriptions' % user_uuid
        api_response = self._post(data=data, url=url)
        if api_response.is_ok and 'Location' in api_response.headers:
            us_loc = api_response.headers.get('Location')
            api_response = self._get(url=us_loc)
            if api_response.is_ok:
                return api_response.data
            else:
                logging.debug(api_response.serialize())
                raise APIException(http_code=api_response.code, errors=api_response.errors)
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def update_user_subscription(self, subscription_json: dict) -> bool:
        url = self._url + '/%s/subscriptions/%s' % (subscription_json['user_uuid'], subscription_json['uuid'])
        api_response = self._put(data=subscription_json, url=url)
        if api_response.is_ok:
            return True
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)


class RRNBillingAPIService(RESTService):
    __version__ = 1

    def get_subscriptions(self, lang_code: str) -> dict:
        headers = {
            'Accept-Language': lang_code
        }

        api_response = self._get(headers=headers)

        if api_response.is_ok:
            return api_response.data
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def get_subscription_by_id(self, id: int, lang_code: str) -> dict:
        headers = {
            'Accept-Language': lang_code
        }

        url = "%s/%s" % (self._url, id)
        api_response = self._get(url=url, headers=headers)

        if api_response.is_ok:
            return api_response.data
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)


class PayProGlobalPaymentService(object):
    __version__ = 1

    _base_url = None
    _secret_key = None
    _test_mode = None

    _recurring_products = ['47197', '47198', '47199']
    _buy_products = ['47303', '47305', '47304']

    def __init__(self, config: dict):
        cfg = config['PAY_PRO_GLOBAL']
        self._base_url = cfg['base_url']
        self._secret_key = cfg['secret_key']
        self._test_mode = 'true' if config['DEBUG'] else 'false'
        self._params_dict = cfg['params_name']

    def build_redirect_url(self, order_code: str, subscription_id: int, payment_method_id: str,
                           user_locale: str = None):
        payment_method_id = str(payment_method_id)
        logger.info("build_redirect_url method with params [subscription_id=%s, user_locale=%s, payment_method_id=%s]"
                    % (str(subscription_id), str(user_locale), str(payment_method_id)))
        logger.info('Buy or Recurring? Depends on payment method.')
        if payment_method_id in ['1', '14']:
            logger.info('Payment method is CC or PayPal. Use RECURRING payments')
            product_id = self._recurring_products[int(subscription_id) - 1]
        else:
            logger.info('Payment method is NOT CC or PayPal. Use BUY payments')
            product_id = self._buy_products[int(subscription_id) - 1]

        logger.info('Production ID: %s' % product_id)

        logger.info('Create base url with base required parameters')
        redirect_url = self._base_url % (str(product_id), str(self._test_mode), str(self._secret_key))
        logger.info('Phrase #1. Redirect URL: %s' % str(redirect_url))

        logger.info('Add payment and order fields to URL.')
        redirect_url += self._params_dict['payment_method'] % str(payment_method_id)
        redirect_url += self._params_dict['order_code'] % str(order_code)
        logger.info('Phrase #1. Redirect URL: %s' % str(redirect_url))

        logger.info('Check user locale')
        if user_locale:
            logger.info('We have user locale: %s' % str(user_locale))
            if len(user_locale) > 2:
                logger.info('Too long user locale. Make it short.')
                user_locale = user_locale[0:2]
                logger.info('New user locale: %s' % str(user_locale))
            redirect_url += self._params_dict['language'] % str(user_locale)
            logger.info('Phrase #2. Redirect URL: %s' % str(redirect_url))

        return redirect_url


class SubscriptionService(object):
    __version__ = 1

    _billing_service = None
    _cache_service = None

    def __init__(self, billing_service: RRNBillingAPIService, cache_service: CacheService):
        self._billing_service = billing_service
        self._cache_service = cache_service

    def get_subscriptions(self, lang_code) -> list:
        logger.info("Check subscriptions in cache")
        subscriptions = self._cache_service.get(key='subscriptions', prefix=lang_code)
        logger.info("Is subscriptions exists in cache: %s" % subscriptions is not None)
        if subscriptions is None:
            logger.info("There are no subscriptions in cache. Call billing service")
            self.__update_cache_subscriptions(lang_code=lang_code)
            return self._cache_service.get(key='subscriptions', prefix=lang_code)
        return subscriptions

    def get_subscriptions_dict(self, lang_code) -> dict:
        logger.info("Check subscriptions_dict in cache")
        subscriptions_dict = self._cache_service.get(key='subscriptions_dict', prefix=lang_code)
        logger.info("Is subscriptions dict exists in cache: %s" % subscriptions_dict is not None)
        if subscriptions_dict is None:
            logger.info("There are no subscriptions_dict in cache.")
            self.__update_cache_subscriptions(lang_code=lang_code)
            return self._cache_service.get(key='subscriptions_dict', prefix=lang_code)
        return subscriptions_dict

    def __update_cache_subscriptions(self, lang_code):
        logger.info("Call billing service")
        try:
            subscriptions = self._billing_service.get_subscriptions(lang_code=lang_code)
            logger.info("Called. Place in cache.")
            self._cache_service.set('subscriptions', subscriptions, prefix=lang_code)
            logger.info("Create dict. Place in cache.")
            subscriptions_dict = {subscriptions[i]['id']: subscriptions[i] for i in range(0, len(subscriptions))}
            self._cache_service.set('subscriptions_dict', subscriptions_dict, prefix=lang_code)
        except APIException:
            pass


class UserDiscoveryResponse(object):
    __version__ = 1

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
