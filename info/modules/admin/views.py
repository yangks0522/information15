from flask import current_app, redirect, render_template, request, session
from info.models import User
from . import admin_blue


# 管理员登陆处理
# 请求路径: /admin/login
# 请求方式: GET,POST
# 请求参数:GET,无, POST,username,password
# 返回值: GET渲染login.html页面, POST,login.html页面,errmsg

@admin_blue.route('/login', methods=["GET", "POST"])
def admin_login():
    """
    1.判断是否是GET请求,直接渲染页面
    2. 如果是POST请求,获取参数
    3.根据用户名,查询管理员对象
    4.判断管理员对象是否存在
    5.校验管理员密码是否正确
    6.记录管理员登陆信息到session
    7.重定向到首页
    :return:
    """
    # 1.判断是否是GET请求,直接渲染页面
    if request.method == "GET":
        return render_template("admin/login.html")
    # 2. 如果是POST请求,获取参数
    username = request.form.get("username")
    password = request.form.get("password")
    # 3.根据用户名,查询管理员对象
    try:
        admin = User.query.filter(User.mobile == username, User.is_admin==True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="管理员登陆失败")
    # 4.判断管理员对象是否存在
    if not admin:
        return render_template("admin/login.html", errmsg="管理员不存在")
    # 5.校验管理员密码是否正确
    if not admin.check_passowrd(password):
        return render_template("admin/login.html", errmsg="密码错误")
    # 6.记录管理员登陆信息到session
    session["user_id"] = admin.id
    session["nick_name"] = admin.nick_name
    session["mobile"] = admin.mobile
    session["is_admin"] = admin.is_admin
    # 7.重定向到首页
    return redirect("http://www.baidu.com")
