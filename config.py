import os


class Config(object):   # 所有配置类的父类，通用的配置写在这里
    SECRET_KEY = 'Secret Key!'
    pass
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # SQLALCHEMY_TRACK_MODIFICATIONS = True
    # SCHEDULE_API_ENABLE = True


class DevelopmentConfig(Config):    # 开发环境配置类
    DEBUG = True
    url = os.environ.get('DATABASE_URL')
    # print(url)
    if url is not None:
        url = url.split('postgres://')[1]
        SQLALCHEMY_URL = 'postgresql+psycopg2://{}'.format(url)
    ENV = 'development'


class TestingConfig(Config):    # 测试环境配置类
    # for docker
    DEBUG = True
    url = os.environ.get('DATABASE_URL')
    if url is not None:
        url = url.split('postgres://')[1]
        SQLALCHEMY_URL = 'postgresql+psycopg2://{}'.format(url)


class ProductionConfig(Config):     # 生产环境配置类
    DEBUG = False
    # For Heroku deploy
    url = os.environ.get('DATABASE_URL')
    if url is not None:
        url = url.split('postgres://')[1]
        SQLALCHEMY_URL = 'postgresql+psycopg2://{}'.format(url)


config = {  # config字典注册了不同的配置，默认配置为开发环境，本例使用开发环境
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}