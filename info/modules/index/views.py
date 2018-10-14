from info import redis_store
from . import index_blue
from flask import render_template ,current_app

@index_blue.route("/")
def hello_world():
    # 测试redis
    # redis_store.set("name","zhangsan")
    # print(redis_store.get("name"))

    # 测试session存储数据
    # session["age"] = 15
    # print(session.get("age"))

    # 输入记录信息
    # 输入记录信息,可以代替print
    # logging.debug("调试信息")
    # logging.info("详细信息")
    # logging.warning("警告信息")
    # logging.error("错误信息")

    # current_app 来输出
    # current_app.logger.debug("调试信息2")
    # current_app.logger.info("详细信息2")
    # current_app.logger.warning("警告信息2")
    # current_app.logger.error("错误信息2")


    return render_template("news/index.html")
# 只需要写对应的接口,返回一张图片即可
# 解决:current_app.send_static_file,自动static文件夹中寻找指定的资源
@index_blue.route('/favicon.ico')
def web_log():

    return current_app.send_static_file("news/favicon.ico")