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


if __name__ == "__main__":
    app.run()