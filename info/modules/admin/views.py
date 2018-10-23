import time
from datetime import datetime, timedelta
from flask import current_app, redirect, render_template, request, session, jsonify
from flask import g

from info import constants
from info import user_login_data
from info.models import User, News, Category
from info.utils.image_storage import image_storage

from info.utils.response_code import RET
from . import admin_blue


# 新闻编辑详情
# 请求路径: /admin/news_edit_detail
# 请求方式: GET, POST
# 请求参数: GET, news_id, POST(news_id,title,digest,content,index_image,category_id)
# 返回值:GET,渲染news_edit_detail.html页面,data字典数据, POST(errno,errmsg)
@admin_blue.route('/news_edit_detail', methods=["GET", "POST"])
def news_edit_detail():
    """
    1.判断请求方式,如果GET,渲染页面
        校验参数
        根据新闻编号获取新闻对象,并判断是否存在
        查询所有分类信息
        携带新闻数据,渲染页面
    2.如果是POST请求,获取参数
    3.校验参数,为空校验
    4.判断新闻是否存在
    5.上传图片
    6.判断图片是否上传成功
    7.设置属性到新闻对象
    8.返回响应
    :return:
    """
    # 1.判断请求方式,如果GET,渲染页面
    if request.method == "GET":
        # 获取参数,新闻编号
        news_id = request.args.get("news_id")
        # 校验参数
        if not news_id:
            return jsonify(errno=RET.DBERR, errmsg="参数不全")
        # 根据新闻编号获取新闻对象,并判断是否存在
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")
        # 查询所有分类信息
        try:
            categories = Category.query.all()
            categories.pop(0)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="获取分类失败")
        # 携带新闻数据,渲染页面
        return render_template("admin/news_edit_detail.html", news=news.to_dict(), categories=categories)
    # 2.如果是POST请求,获取参数
    news_id = request.form.get("news_id")
    title = request.form.get("title")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")
    # 3.校验参数,为空校验
    if not all([news_id, title, digest, content, index_image, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    # 4.根据编号查询新闻对象,判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")
    # 5.上传图片
    try:
        image_name = image_storage(index_image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="七牛云异常")

    # 6.判断图片是否上传成功
    if not image_name:
        return jsonify(errno=RET.DBERR, errmsg="图片上传失败")
    # 7.设置属性到新闻对象
    news.title = title
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    # 8.返回响应
    return jsonify(errno=RET.OK, errmsg="编辑成功")


# 功能:新闻编辑列表
# 请求路径: /admin/news_edit
# 请求方式: GET
# 请求参数: GET, p, keywords
# 返回值:GET,渲染news_edit.html页面,data字典数据
@admin_blue.route('/news_edit')
def news_edit():
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
    keyword = request.args.get("keyword")
    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    # 3.分页查询
    try:
        filters = []
        if keyword:
            filters.append(News.title.contains(keyword))
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户失败")

    # 4.获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items
    # 5.对象列表转成,字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())
    # 6.拼接数据,渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": news_list,
    }
    return render_template("admin/news_edit.html", data=data)


# 功能:新闻审核详情
# 请求路径: /admin/news_review_detail
# 请求方式: GET,POST
# 请求参数: GET, news_id, POST,news_id, action
# 返回值:GET,渲染news_review_detail.html页面,data字典数据
@admin_blue.route('/news_review_detail', methods=["GET", "POST"])
def news_review_detail():
    """
    # 1.判断请求方式,如果GET,渲染页面
        # 1.1 获取参数,新闻编号
        # 1.2 校验参数
        # 1.3 根据新闻编号获取新闻对象,并判断是否存在
        # 1.4 携带新闻数据,渲染页面
    # 2.如果是POST请求,获取参数
    # 3.校验参数,为空校验
    # 4.操作类型校验
    # 5.通过编号获取新闻对象
    # 6.判断新闻对象是否存在
    # 7.根据操作类型,改变新闻状态
    # 8.返回响应
    :return:
    """
    # 1.判断请求方式,如果GET,渲染页面
    if request.method == "GET":
        # 1.1 获取参数,新闻编号
        news_id = request.args.get("news_id")
        # 1.2 校验参数
        if not news_id:
            return jsonify(errno=RET.DBERR, errmsg="参数不全")
        # 1.3 根据新闻编号获取新闻对象,并判断是否存在
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")
        # 1.4 携带新闻数据,渲染页面
        return render_template("admin/news_review_detail.html", news=news.to_dict())
    # 2.如果是POST请求,获取参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")
    # 3.校验参数,为空校验
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    # 4.操作类型校验
    if not action in ["accept", "reject"]:
        return jsonify(errno=RET.DATAERR, errmsg="操作类型有误")
    # 5.通过编号获取新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")
    # 6.判断新闻对象是否存在
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")
    # 7.根据操作类型,改变新闻状态
    if action == "accept":
        news.status = 0
    else:
        reason = request.json.get("reason", "")
        news.reason = reason
        news.status = -1
    # 8.返回响应
    return jsonify(errno=RET.OK, errmsg="操作成功")


# 功能:新闻审核
# 请求路径: /admin/news_review
# 请求方式: GET
# 请求参数: GET, p,keyword
# 返回值:渲染user_list.html页面,data字典数据
@admin_blue.route('/news_review')
def news_review():
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
    keyword = request.args.get("keyword")
    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    # 3.分页查询
    try:
        filters = [News.status != 0]
        if keyword:
            filters.append(News.title.contains(keyword))
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户失败")

    # 4.获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items
    # 5.对象列表转成,字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())
    # 6.拼接数据,渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": news_list,
    }
    return render_template("admin/news_review.html", data=data)


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
        return jsonify(errno=RET.DBERR, errmsg="获取用户失败")

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
