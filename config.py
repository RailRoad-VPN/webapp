from flask_babel import _


class Config(object):
    DEBUG = False
    TESTING = False

    APP_SESSION_SK = '4yjBJ6pDwfFKh8UR2yM'
    SESSION_TYPE = 'filesystem'
    SECRET_KEY = APP_SESSION_SK
    TEMPLATES_AUTO_RELOAD = True
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    LANGUAGES = ['en']

    USERS_API_RESOURCE_NAME = 'users'
    USER_VPNSERVERS_API_RESOURCE_NAME = f"{USERS_API_RESOURCE_NAME}/user_uuid/servers"
    USER_VPNSERVER_CONFIGS_API_RESOURCE_NAME = f"{USER_VPNSERVERS_API_RESOURCE_NAME}/server_uuid/configurations"
    SERVICES_API_RESOURCE_NAME = 'services'
    ORDERS_API_RESOURCE_NAME = 'orders'

    EMAIL_SMTP = {
        'server': 'mail.rroadvpn.net',
        'port': 465,
        'support_account': {
            'from_name': _('Support Railroad VPN'),
            'email': 'support@rroadvpn.net',
            'password': 'C8fk2m8iaW6n',
        },
    }


class ProductionConfig(Config):
    ENV = 'production'

    API_URL = 'http://IP:8000/api/v1'

    FS = {
        'contact': '/opt/apps/dfn/contact/',
        'subscribe': '/opt/apps/dfn/subscribe.log'
    }


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True

    API_URL = 'http://127.0.0.1:8000/api/v1'

    FS = {
        'contact': './',
        'subscribe': './subscribe.log'
    }


class TestingConfig(Config):
    ENV = 'testing'
    TESTING = True
    DEBUG = False

    API_URL = 'https://api.rroadvpn.net/api/v1'

    FS = {
        'contact': '/opt/apps/dfn/contact/',
        'subscribe': '/opt/apps/dfn/subscribe.log'
    }
