# 初始化信息
from flask import Flask
from config import config_dict
import redis
from flask_sqlalchemy import SQLAlchemy

from flask_session import Session
from flask_wtf import CSRFProtect
def create_app(config_name):
    app = Flask(__name__)
    # 根据传入的配置名称,获取对应的配置类
    config = config_dict.get(config_name)
    # 加载配置类信息
    app.config.from_object(config)

    db = SQLAlchemy(app)

    # 创建redis对象
    redis_store = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

    # 初始化session,读取app上的配置信息
    Session(app)

    # 保护app使用CSRFProtect
    CSRFProtect(app)

    return app
