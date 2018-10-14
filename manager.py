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

app = Flask(__name__)


class Config(object):
    DEBUG = True
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost:3306/information15"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app.config.from_object(Config)

db = SQLAlchemy(app)


@app.route("/")
def hello_world():
    return "helloworld"


if __name__ == "__main__":
    app.run()
