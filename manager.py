"""
1.数据库配置
2.redis配置
3.session配置
4.CSRFProtect配置
5.日志文件
6.数据库迁移

"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis

app = Flask(__name__)


class Config(object):
    DEBUG = True
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost:3306/information15"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379


app.config.from_object(Config)

db = SQLAlchemy(app)

# 创建redis对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)


@app.route("/")
def hello_world():
    # 测试redis
    # redis_store.set("name","zhangsan")
    # print(redis_store.get("name"))

    return "helloworld"


if __name__ == "__main__":
    app.run()
