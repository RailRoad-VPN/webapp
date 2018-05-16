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


class ProductionConfig(Config):
    API_URL = 'http://IP:8000/api/v1'


class DevelopmentConfig(Config):
    DEBUG = True

    API_URL = 'http://127.0.0.1:8000/api/v1'


class TestingConfig(Config):
    TESTING = True
