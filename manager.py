"""
1.数据库配置
2.redis配置
3.session配置,为后续登陆保持做铺垫
4.CSRFProtect配置
5.日志文件
6.数据库迁移

"""

from flask import Flask,session

from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session


app = Flask(__name__)


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
    #redis服务器地址
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True # session的签名信息
    PERMANENT_SESSION_LIFETIME = 3600*24*2  # 有效期两天 单位秒
    SECRET_KEY = "asdasdasfasfassa"


app.config.from_object(Config)

db = SQLAlchemy(app)

# 创建redis对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)

# 初始化session,读取app上的配置信息
Session(app)





@app.route("/")
def hello_world():
    # 测试redis
    # redis_store.set("name","zhangsan")
    # print(redis_store.get("name"))

    # 测试session存储数据
    # session["age"] = 15
    # print(session.get("age"))

    return "helloworld"


if __name__ == "__main__":
    app.run()
