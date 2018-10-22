from flask import Blueprint
from flask import redirect
from flask import request
from flask import session

admin_blue = Blueprint("admin",__name__,url_prefix="/admin")

from . import views


# 只要访问了管理员的视图,需要做蓝图,判断当前用户是否是管理员
# 如果访问管理员登录页面不需要做拦截,因为需要输入密码
# 如果访问访问管理员其他页面需要做拦截
@admin_blue.before_request
def visit_admin():
    if not request.url.endswith("/admin/login"):
        if not session.get("is_admin"):
            # print(request.url)
            return redirect("/")

