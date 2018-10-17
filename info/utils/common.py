# 定义公共代码

# 自定义过滤器

from flask import current_app, g, session
from functools import wraps



def index_class(index):
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""

# 使用装饰器,封装用户登陆数据
def user_login_data(view_func):
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        # 获取用户的编号,从session
        user_id = session.get("user_id")

        # 判断用户是否存在
        user = None
        if user_id:
            try:
                from info.models import User
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)

        # 将用户数据封装到,g对象
        g.user = user

        return view_func(*args,**kwargs)
    return wrapper