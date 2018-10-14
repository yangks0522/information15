"""
1.数据库配置
2.redis配置
3.session配置,为后续登陆保持做铺垫
4.CSRFProtect配置
5.日志文件
6.数据库迁移

"""
import logging

from flask import current_app

from info import create_app

app = create_app("develop")


@app.route("/")
def hello_world():
    # 测试redis
    # redis_store.set("name","zhangsan")
    # print(redis_store.get("name"))

    # 测试session存储数据
    # session["age"] = 15
    # print(session.get("age"))

    # 输入记录信息
    # 输入记录信息,可以代替print
    logging.debug("调试信息")
    logging.info("详细信息")
    logging.warning("警告信息")
    logging.error("错误信息")

    # current_app 来输出
    current_app.logger.debug("调试信息2")
    current_app.logger.info("详细信息2")
    current_app.logger.warning("警告信息2")
    current_app.logger.error("错误信息2")


    return "helloworld"


if __name__ == "__main__":
    app.run()