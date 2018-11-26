from app.models.user_service_status import UserServiceStatus
from app.service import *
from app.models.exception import UserPolicyException, DFNError

sys.path.insert(0, '../rest_api_library')
from rest import APINotFoundException, APIException


class UserPolicy(object):
    __version__ = 1

    logger = logging.getLogger(__name__)

    _rrn_users_api_service = None
    _rrn_services_api_service = None

    def __init__(self, rrn_users_api_service: RRNUsersAPIService, rrn_services_api_service: RRNServicesAPIService):
        self._rrn_users_api_service = rrn_users_api_service
        self._rrn_services_api_service = rrn_services_api_service

    def create_user(self, email: str, password: str, password_repeat: str) -> dict:
        self.logger.info('create_user method')

        if email is None or password is None or password_repeat is None or password != password_repeat:
            raise UserPolicyException(error=DFNError.USER_SIGNUP_FIELDS_INCOMPLETE.message,
                                      error_code=DFNError.USER_SIGNUP_FIELDS_INCOMPLETE.code,
                                      developer_message=DFNError.USER_SIGNUP_FIELDS_INCOMPLETE.developer_message)

        try:
            # try to find user by email
            self._rrn_users_api_service.get_user(email=email)
            raise UserPolicyException(error=DFNError.USER_SIGNUP_EMAIL_BUSY.message,
                                      error_code=DFNError.USER_SIGNUP_EMAIL_BUSY.code,
                                      developer_message=DFNError.USER_SIGNUP_EMAIL_BUSY.developer_message)
        except APINotFoundException:
            pass
        except APIException as e:
            self.logger.debug(e.serialize())
            raise UserPolicyException(error=DFNError.UNKNOWN_ERROR_CODE.message,
                                      error_code=DFNError.UNKNOWN_ERROR_CODE.code,
                                      developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)

        # try to create user
        try:
            user_json = self._rrn_users_api_service.create_user(email=email, password=password)
            self.logger.info("created user: %s" % user_json)
        except APIException as e:
            self.logger.debug(e.serialize())
            raise UserPolicyException(error=DFNError.UNKNOWN_ERROR_CODE.message,
                                      error_code=DFNError.UNKNOWN_ERROR_CODE.code,
                                      developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)

        return user_json

    def create_user_service(self, user_uuid: str, service_id: int, order_uuid: str, is_trial: bool):
        try:
            self.logger.info("Creating user service...")
            user_service = self._rrn_users_api_service.create_user_service(user_uuid=user_uuid,
                                                                           status_id=UserServiceStatus.ACTIVE.sid,
                                                                           service_id=service_id,
                                                                           is_trial=is_trial,
                                                                           order_uuid=order_uuid)
            self.logger.error(f"user service was created: {user_service}")
        except APIException as e:
            self.logger.error("user service was not created")
            self.logger.debug(e.serialize())
            raise UserPolicyException(error=DFNError.UNKNOWN_ERROR_CODE.message,
                                      error_code=DFNError.UNKNOWN_ERROR_CODE.code,
                                      developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)

    def get_user(self, suuid: str):
        try:
            self.logger.info("get user")
            return self._rrn_users_api_service.get_user(uuid=suuid)
        except APIException as e:
            self.logger.error("get user exception")
            self.logger.debug(e.serialize())
            raise UserPolicyException(error=DFNError.UNKNOWN_ERROR_CODE.message,
                                      error_code=DFNError.UNKNOWN_ERROR_CODE.code,
                                      developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)

    def get_user_available_services(self):
        self.logger.debug("get_user_available_services method")
        services = self._rrn_services_api_service.get_services()
        self.logger.debug(f"Size: %s" % len(services))

        if 'user' in session:
            user_uuid = session.get('user').get('uuid')
            for sub in services:
                if sub['is_free']:
                    is_free_available = self.is_free_available_for_service(user_uuid=user_uuid, service=sub)
                    if not is_free_available:
                        services.remove(sub)
                        continue
                if sub['is_trial']:
                    is_trial_available = self.is_free_available_for_service(user_uuid=user_uuid, service=sub)
                    if not is_trial_available:
                        sub['is_trial_available'] = False
        return services

    def is_trial_available_for_service(self, user_uuid: str, service_id: int):
        try:
            service_id = int(service_id)
            service = self._rrn_services_api_service.get_service_by_id(service_id=service_id)
            if not service['is_trial']:
                return False
            user_services = self._rrn_users_api_service.get_user_services(user_uuid=user_uuid)
            for user_service in user_services:
                user_service_id = user_service['service_id']
                if service_id == user_service_id:
                    return False
        except APIException as e:
            raise UserPolicyException(error=DFNError.UNKNOWN_ERROR_CODE.message,
                                      error_code=DFNError.UNKNOWN_ERROR_CODE.code,
                                      developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
        return True

    def is_free_available_for_service(self, user_uuid: str, service: dict):
        if not service['is_free']:
            return False
        try:
            user_services = self._rrn_users_api_service.get_user_services(user_uuid=user_uuid)
            for user_service in user_services:
                user_service_id = user_service['service_id']
                if user_service_id == service['id']:
                    return False
        except APIException as e:
            raise UserPolicyException(error=DFNError.UNKNOWN_ERROR_CODE.message,
                                      error_code=DFNError.UNKNOWN_ERROR_CODE.code,
                                      developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
        return True
