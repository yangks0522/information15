import time
from datetime import datetime, timedelta
from flask import current_app, redirect, render_template, request, session, jsonify
from flask import g

from info import user_login_data
from info.models import User
from info.utils.response_code import RET
from . import admin_blue


# 功能: 管理用户列表
# 请求路径: /admin/user_list
# 请求方式: GET
# 请求参数: p
# 返回值:渲染user_list.html页面,data字典数据
@admin_blue.route('/user_list')
def user_list():
    """
    1.获取参数
    2.参数类型转换
    3.分页查询
    4.获取分页对象属性,总页数,当前页,当前页对象列表
    5.对象列表转成,字典列表
    6.拼接数据,渲染页面
    :return:
    """
    # 1.获取参数
    page = request.args.get("p", "1")
    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    # 3.分页查询
    try:
        paginate = User.query.filter(User.is_admin == False).order_by(User.create_time.desc()).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET, errmsg="获取用户失败")

    # 4.获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items
    # 5.对象列表转成,字典列表
    user_list = []
    for user in items:
        user_list.append(user.to_admin_dict())
    # 6.拼接数据,渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "user_list": user_list,
    }
    return render_template("admin/user_list.html", data=data)


# 功能:管理员用户统计
# 请求路径: /admin/user_count
# 请求方式: GET
# 请求参数: 无
# 返回值:渲染页面user_count.html,字典数据
@admin_blue.route('/user_count')
def user_count():
    """
    1.查询总人数,不包括管理员
    2.查询月活人数
    3.查询日活人数
    4.查询时间段内活跃人数
    5.携带数据,渲染页面
    :return:
    """
    # 1.查询总人数,不包括管理员
    try:
        totel_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/user_count.html")
    # 2.查询月活人数
    calender = time.localtime()
    try:
        # 获取到本月的一号0点钟
        month_starttime_str = "%d-%d-01" % (calender.tm_year, calender.tm_mon)
        month_starttime_data = datetime.strptime(month_starttime_str, "%Y-%m-%d")
        # 获取当前时间
        month_endtime_data = datetime.now()
        # 根据时间查询用户
        month_count = User.query.filter(User.last_login >= month_starttime_data, User.last_login <= month_endtime_data,
                                        User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
    # 3.查询日活人数
    try:
        # 获取到本日的0点钟
        day_starttime_str = "%d-%d-%d" % (calender.tm_year, calender.tm_mon, calender.tm_mday)
        day_starttime_data = datetime.strptime(day_starttime_str, "%Y-%m-%d")
        # 获取当前时间
        day_endtime_data = datetime.now()
        # 根据时间查询用户
        day_count = User.query.filter(User.last_login >= day_starttime_data, User.last_login <= day_endtime_data,
                                      User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
    # 4.查询时间段内活跃人数
    active_date = []
    active_count = []
    for i in range(0, 31):
        begin_date = day_starttime_data - timedelta(
            days=i)  # timedelta()对象代表两个时间之间的时间差，两个date或datetime对象相减就可以返回一个timedelta对象
        end_date = day_starttime_data - timedelta(days=i - 1)

        active_date.append(begin_date.strftime("%Y-%m-%d"))  # strftime()函数接收以时间元组，并返回以可读字符串表示的当地时间

        everyday_active_count = User.query.filter(User.last_login >= begin_date, User.last_login <= end_date,
                                                  User.is_admin == False).count()
        active_count.append(everyday_active_count)
    active_count.reverse()
    active_date.reverse()

    # 5.携带数据,渲染页面
    data = {
        "totel_count": totel_count,
        "month_count": month_count,
        "day_count": day_count,
        "active_date": active_date,
        "active_count": active_count,
    }
    return render_template("admin/user_count.html", data=data)


# 功能:管理员首页
# 请求路径: /admin/index
# 请求方式: GET
# 请求参数: 无
# 返回值:渲染页面index.html,user字典数据
@admin_blue.route('/index')
@user_login_data
def admin_index():
    # if not session.get("is_admin"):
    #     return redirect("/")
    return render_template("admin/index.html", admin=g.user.to_dict() if g.user else "")


# 功能:管理员登陆处理
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
        # 判断管理员是否已经登录过,如果登录过直接重定向到首页
        if session.get("is_admin"):
            return redirect("/admin/index")
        return render_template("admin/login.html")
    # 2. 如果是POST请求,获取参数
    username = request.form.get("username")
    password = request.form.get("password")
    # 3.根据用户名,查询管理员对象
    try:
        admin = User.query.filter(User.mobile == username, User.is_admin == True).first()
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
    return redirect("/admin/index")
