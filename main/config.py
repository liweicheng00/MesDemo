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
    # SQLALCHEMY_URL = "postgresql+psycopg2://liweicheng:@127.0.0.1:5432/flask_blog"


class TestingConfig(Config):    # 测试环境配置类
    pass


class ProductionConfig(Config):     # 生产环境配置类
    DEBUG = False
    ENV = 'production'
    # For Heroku deploy
    url = os.environ.get('DATABASE_URL')
    if url is not None:
        url = url.split('postgres://')[1]
        SQLALCHEMY_URL = 'postgresql+psycopg2://{}'.format(url)
    # else:
    #     url = 'postgres://efvqrloxqjscdd:8c926512129cef10eff642b351d94f5c19667b4066db120736ec68d79e48346f@ec2-52-23-14-156.compute-1.amazonaws.com:5432/ddta1c426nbije'
    #     url = url.split('postgres://')[1]
    #     SQLALCHEMY_URL = 'postgresql+psycopg2://{}'.format(url)


config = {  # config字典注册了不同的配置，默认配置为开发环境，本例使用开发环境
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}