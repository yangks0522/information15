import redis


class Config(object):
    DEBUG = True
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost:3306/information15"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # session配置信息
    SESSION_TYPE = "redis"
    # redis服务器地址
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # session的签名信息
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 2  # 有效期两天 单位秒
    SECRET_KEY = "asdasdasfasfassa"


# 开发模式的配置信息
class DeveloperConfig(Config):
    pass

# 生产模式(线上模式)
class PrductConfig(Config):
    DEBUG = False

# 测试模式
class TestingConfig(Config):
    TESTING = True


config_dict = {
    "develop": DeveloperConfig,
    "product": PrductConfig,
    "testing": TestingConfig
}

