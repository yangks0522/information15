"""
1.数据库配置
2.redis配置
3.session配置,为后续登陆保持做铺垫
4.CSRFProtect配置
5.日志文件
6.数据库迁移

"""
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

    return "helloworld"


if __name__ == "__main__":
    app.run()
