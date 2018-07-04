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

    LANGUAGES = ['ru', 'en']

    USERS_API_RESOURCE_NAME = 'users'
    SUBSCRIPTIONS_API_RESOURCE_NAME = 'subscriptions'
    ORDERS_API_RESOURCE_NAME = 'orders'

    PAY_PRO_GLOBAL = {
        'base_url': 'https://store.payproglobal.com/checkout?products[1][id]=%s&use-test-mode=%s&secret-key=%s',
        'secret_key': '848dee',
        'params_name': {
            'payment_method': '&payment-method=%s',
            'language': '&language=%s',
            'order_code': '&x-ordercode=%s',
        }
    }

    EMAIL_SMTP = {
        'server': 'smtp.novicorp.co',
        'port': 465,
        'support_account': {
            'from_name': _('Support Railroad'),
            'email': 'support@rroadvpn.net',
            'password': 'X29fRtP0G9bfVW',
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
    DEBUG = True

    API_URL = 'http://127.0.0.1:61885/api/v1'

    FS = {
        'contact': '/opt/apps/dfn/contact/',
        'subscribe': '/opt/apps/dfn/subscribe.log'
    }
