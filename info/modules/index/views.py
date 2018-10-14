from info import redis_store
from . import index_blue

@index_blue.route("/")
def hello_world():
    # 测试redis
    redis_store.set("name","zhangsan")
    print(redis_store.get("name"))

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


    return "helloworld"