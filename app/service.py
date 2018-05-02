import json
import logging
import sys

import os
from json import JSONDecodeError

import requests

from exception import APIException, DFNError


class RESTService(object):
    __version__ = 1

    _url = None

    def __init__(self, api_url: str) -> None:
        super().__init__()

        self._url = api_url
        logging.debug("RESTService init. %s" % self.__repr__())

    def _get(self, url: str = None, params: dict = None, headers: dict = None):
        if url is None:
            url = self._url
        try:
            get_req = requests.get(url=url, params=params, headers=headers)
        except requests.exceptions.ConnectionError:
            raise APIException(data={}, http_code=503, code=DFNError.UNKNOWN_ERROR_CODE, message='Service Unavailable')
        get_req_sc = get_req.status_code
        if get_req_sc == 200:
            get_json = get_req.json()
        elif get_req_sc == 404:
            # get_req_error_dict = get_req.json()
            # error_dict = get_req_error_dict['error']
            # code = error_dict['code']
            # message = error_dict['message']
            # data = error_dict['data']
            # raise APIObjectNotFoundException(data=data, http_code=get_req_sc, code=code, message=message)

            # Return None instead of raising exception
            return None
        else:
            try:
                get_req_error_dict = get_req.json()
                error_dict = get_req_error_dict['error']
                code = error_dict['code']
                message = error_dict['message']
                data = error_dict['data']
                raise APIException(data=data, http_code=get_req_sc, code=code, message=message)
            except (KeyError, TypeError, JSONDecodeError) as err:
                data = {
                    'system_error_code': DFNError.UNKNOWN_ERROR_CODE,
                    'developer_message': err.args[0],
                }
                raise APIException(data=data, http_code=get_req_sc, code=DFNError.UNKNOWN_ERROR_CODE,
                                   message="Internal unknown error")
        return get_json

    def _post(self, data: dict, url: str = None, headers: dict = None):
        if url is None:
            url = self._url
        try:
            post_req = requests.post(url=url, json=data, headers=headers)
        except requests.exceptions.ConnectionError:
            raise APIException(data={}, http_code=503, code=DFNError.UNKNOWN_ERROR_CODE, message='Service Unavailable')
        post_req_sc = post_req.status_code
        if post_req_sc == 201:
            return post_req.headers.get('Location')
        elif post_req_sc == 400:
            # TODO does 400 diff 500 and others?
            post_req_error_dict = post_req.json()
            error_dict = post_req_error_dict['error']
            code = error_dict['code']
            message = error_dict['message']
            data = error_dict['data']
            raise APIException(data=data, http_code=post_req_sc, code=code, message=message)
        else:
            try:
                post_req_error_dict = post_req.json()
                error_dict = post_req_error_dict['error']
                code = error_dict['code']
                message = error_dict['message']
                data = error_dict['data']
                raise APIException(data=data, http_code=post_req_sc, code=code, message=message)
            except (KeyError, JSONDecodeError) as err:
                data = {
                    'system_error_code': DFNError.UNKNOWN_ERROR_CODE,
                    'developer_message': err.args[0],
                }
                raise APIException(data=data, http_code=post_req_sc, code=DFNError.UNKNOWN_ERROR_CODE,
                                   message="Internal unknown error")

    def _put(self, data: dict, url: str = None, headers: dict = None):
        if url is None:
            url = self._url
        try:
            put_req = requests.put(url=url, data=json.dumps(data), headers=headers)
        except requests.exceptions.ConnectionError:
            raise APIException(data={}, http_code=503, code=DFNError.UNKNOWN_ERROR_CODE, message='Service Unavailable')
        put_req_sc = put_req.status_code
        if put_req_sc == 200:
            return put_req.headers.get('Location')
        elif put_req_sc == 400:
            # TODO does 400 diff 500 and others?
            put_req_error_dict = put_req.json()
            error_dict = put_req_error_dict['error']
            code = error_dict['code']
            message = error_dict['message']
            data = error_dict['data']
            raise APIException(data=data, http_code=put_req_sc, code=code, message=message)
        else:
            try:
                put_req_error_dict = put_req.json()
                error_dict = put_req_error_dict['error']
                code = error_dict['code']
                message = error_dict['message']
                data = error_dict['data']
                raise APIException(data=data, http_code=put_req_sc, code=code, message=message)
            except (KeyError, JSONDecodeError) as err:
                data = {
                    'system_error_code': DFNError.UNKNOWN_ERROR_CODE,
                    'developer_message': err.args[0],
                }
                raise APIException(data=data, http_code=put_req_sc, code=DFNError.UNKNOWN_ERROR_CODE,
                                   message="Internal unknown error")

    def __repr__(self):
        return self.__dict__


class FeedbackService(RESTService):
    __version__ = 1

    _headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_feedback(self, feedback_dict) -> dict:
        self._post(data=feedback_dict, headers=self._headers)
        # TODO get feedback
        return {}


class UserService(RESTService):
    __version__ = 1

    _headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_user(self, user_dict: dict) -> dict:
        # TODO role
        user_dict['role_id'] = 1
        user_dict['enabled'] = True
        user_dict['account_non_expired'] = True
        user_dict['account_non_locked'] = True
        user_dict['credentials_non_expired'] = True

        user_uri = self._post(data=user_dict, headers=self._headers)
        return self._get(url=user_uri)

    def update_user(self, user_dict: dict) -> dict:
        url = '%s/uuid/%s' % (self._url, user_dict['uuid'])
        user_uri = self._put(url=url, data=user_dict, headers=self._headers)
        return self._get(url=user_uri)

    def get_user_by_uuid(self, uuid: str) -> dict:
        url = '%s/uuid/%s' % (self._url, uuid)
        return self._get(url=url)

    def get_user_by_username(self, username: str) -> dict:
        url = '%s/username/%s' % (self._url, username)
        return self._get(url=url)

    def get_user_by_email(self, email: str) -> dict:
        url = '%s/email/%s' % (self._url, email)
        return self._get(url=url)