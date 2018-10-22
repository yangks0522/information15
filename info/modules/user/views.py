from flask import current_app, g, jsonify, redirect, render_template, request
from info import constants, db
from info.models import Category, News, User
from info.utils.image_storage import image_storage
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import user_blue





# 功能:获取其他用户发布的新闻
# 请求路径: /user/other_news_list
# 请求方式: GET
# 请求参数:p,user_id
# 返回值: errno,errmsg
@user_blue.route('/other_news_list')
def other_news_list():
    """
    1.获取参数
    2.校验参数,参数类型转换
    3.根据作者编号取出作者对象,并判断是否存在
    4.分页查询
    5.获取分页对象属性,总页数,当前页,当前页对象列表
    6.携带参数,返回响应
    :return:
    """
    # 1.获取参数
    page = request.args.get("p")
    other_id = request.args.get("user_id")
    # 2.校验参数,参数类型转换
    if not other_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    try:
        page = int(page)
    except Exception as e:
        page = 1
    # 3.根据作者编号取出作者对象,并判断是否存在
    try:
        author = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="或者作者失败")
    if not author:
        return jsonify(errno=RET.NODATA, errmsg="作者不存在")
    # 4.分页查询
    try:
        paginate = author.news_list.order_by(News.create_time.desc()).paginate(page, 2, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    # 5.获取分页对象属性,总页数,当前页,当前页对象列表
    total_page = paginate.pages
    current_page = paginate.page
    items = paginate.items

    news_list = []
    for news in items:
        news_list.append(news.to_dict())
    # 6.携带参数,返回响应
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_list": news_list
    }
    return jsonify(errno=RET.OK, errmsg="获取成功", data=data)


# 功能:作者详情页面
# 请求路径: /user/other
# 请求方式: GET
# 请求参数:id
# 返回值: 渲染other.html页面,字典data数据
@user_blue.route('/other')
@user_login_data
def other_info():
    """
    1.获取参数
    2.校验参数
    3.通过作者编号,取出作者对象
    4.判断作者对象是否存在
    5.携带作者信息,到页面渲染
    :return:
    """
    # 1.获取参数
    author_id = request.args.get("id")
    # 2.校验参数
    if not author_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    # 3.通过作者编号,取出作者对象
    try:
        author = User.query.get(author_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取作者失败")
    # 4.判断作者对象是否存在
    if not author:
        return jsonify(errno=RET.DBERR, errmsg="获取作者失败")
    if_followed = False
    if g.user:
        if g.user in author.followers:
            is_followed = True
    # 5.携带作者信息,到页面渲染
    data = {
        "author_info": author.to_dict(),
        "is_followed": is_followed,
        "user_info": g.user.to_dict() if g.user else "",
    }
    return render_template("news/other.html", data=data)


# 功能: 获取我的关注列表
# 请求路径: /user/user_follow
# 请求方式: GET
# 请求参数:p
# 返回值: 渲染user_follow.html页面,字典data数据
@user_blue.route('/user_follow')
@user_login_data
def user_follow():
    """
    1.获取参数
    2.参数类型转换
    3.分页查询
    4.获取到分页对象属性,总页数,当前页,当前页对象列表
    5.对象列表转成字典列表
    6.拼接数据,渲染页面
    :return:
    """
    # 1.获取参数
    page = request.args.get("p", "1")
    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1
    # 3.分页查询
    try:
        paginate = g.user.followed.paginate(page, 2, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户失败")
    # 4.获取到分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items
    # 5.对象列表转成字典列表
    author_list = []
    for author in items:
        author_list.append(author.to_dict())
    # 6.拼接数据,渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "author_list": author_list
    }
    return render_template("news/user_follow.html", data=data)


# 功能: 获取我发布的新闻列表
# 请求路径: /user/news_list
# 请求方式:GET
# 请求参数:p
# 返回值:GET渲染user_news_list.html页面
@user_blue.route('/news_list')
@user_login_data
def news_list():
    """
    1.获取页数,参数
    2.参数类型转换
    3.分页查询我发布的新闻
    4.获取分页对象属性,总页数,当前页,当前页对象列表
    5.将当前页对象列表转成,字典列表
    6.携带数据渲染页面
    :return:
    """
    # 1.获取页数,参数
    page = request.args.get("p", "1")

    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # 3.分页查询我发布的新闻
    try:
        paginate = News.query.filter(News.user_id == g.user.id).order_by(News.create_time.desc()).paginate(page, 2,
                                                                                                           False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    # 4.获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将当前页对象列表转成,字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

    # 6.携带数据渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": news_list
    }
    return render_template("news/user_news_list.html", data=data)


# 功能描述:新闻发布
# 请求路径: /user/news_release
# 请求方式:GET,POST
# 请求参数:GET无, POST ,title, category_id,digest,index_image,content
# 返回值:GET请求,user_news_release.html, data分类列表字段数据, POST,errno,errmsg
@user_blue.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    """
    1.判断请求方式是否时GET
    2.如果是GET,携带参数渲染页面
    3.获取post请求参数
    4.校验参数
    5.上传图片
    6.判断图片是否上传成功
    7.创建新闻对象,设置新闻属性
    8.保存新闻到数据库中
    9.返回响应
    :return:
    """
    # 1.判断请求方式是否时GET
    if request.method == "GET":
        try:
            categoles = Category.query.all()
            categoles.pop(0)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="获取分类失败")
        # 2.如果是GET,携带参数渲染页面
        return render_template("news/user_news_release.html", categoles=categoles)
    # 3.获取post请求参数
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")

    # 4.校验参数
    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    # 5.上传图片
    try:
        image_name = image_storage(index_image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="七牛云异常")
    # 6.判断图片是否上传成功
    if not image_name:
        return jsonify(errno=RET.NODATA, errmsg="图片上传失败")
    # 7.创建新闻对象,设置新闻属性
    news = News()
    news.title = title
    news.source = g.user.nick_name
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.category_id = category_id
    news.user_id = g.user.id
    news.status = 1
    # 8.保存新闻到数据库中
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="新闻发布失败")
    # 9.返回响应
    return jsonify(errno=RET.OK, errmsg="新闻发布成功")


# 功能:获取我的收藏新闻
# 请求路径: /user/ collection
# 请求方式:GET
# 请求参数:p(页数)
# 返回值: user_collection.html页面
@user_blue.route('/collection')
@user_login_data
def collection():
    """
    1.获取参数
    2.参数类型转换
    3.分页查询
    4.获取到分页对象属性,总页数,当前页,当前页对象
    5.将当前也对象列表,转成字典列表
    6.渲染页面,携带数据
    :return:
    """
    # 1.获取参数
    page = request.args.get("p")
    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1
    # 3.分页查询
    try:
        paginate = g.user.collection_news.paginate(page, 2, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")
    # 4.获取到分页对象属性,总页数,当前页,当前页对象
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items
    # 5.将当前也对象列表,转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())
    # 6.渲染页面,携带数据
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": news_list,
    }
    return render_template("news/user_collection.html", data=data)


# 功能:修改密码
# 请求路径: /user/pass_info
# 请求方式:GET,POST
# 请求参数:GET无, POST有参数,old_password, new_password
# 返回值:GET请求: user_pass_info.html页面,data字典数据, POST请求: errno, errmsg
@user_blue.route('/pass_info', methods=["GET", "POST"])
@user_login_data
def pass_info():
    """
    1.获取参数
    2.参数类型转换
    3.分页查询
    4.获取到分页对象属性,总页数,当前页,当前页对象
    5.将当前也对象列表,转成字典列表
    6.渲染页面,携带数据
    :return:
    """
    if request.method == "GET":
        return render_template("news/user_pass_info.html")
    # 1.获取参数
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    # 2.校验参数
    if not all([old_password, new_password]):
        return jsonify(errno=RET.DBERR, errmsg="参数不全")
    # 3.判断旧密码是否正确
    if not g.user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR, errmsg="旧密码不正确")
    # 4.设置新密码
    g.user.password = new_password
    # 5.返回响应
    return jsonify(errno=RET.OK, errmsg="修改成功")


# 功能:图片上传
# 请求路径: /user/pic_info
# 请求方式:GET,POST
# 请求参数:无, POST有参数,avatar
# 返回值:GET请求: user_pci_info.html页面,data字典数据, POST请求: errno, errmsg,avatar_url
@user_blue.route('/pic_info', methods=["GET", "POST"])
@user_login_data
def pic_info():
    """
    1.获取参数
    2.校验参数
    3.调用工具类方法,上传图片
    4.判断图片是否上传成功
    5.修改用户图片
    6.返回响应,携带图片地址
    :return:
    """
    if request.method == "GET":
        return render_template("news/user_pic_info.html", user=g.user.to_dict())
    # 1.获取参数
    avatar = request.files.get("avatar")
    # 2.校验参数
    if not avatar:
        return jsonify(errno=RET.DBERR, errmsg="参数不全")
    # 3.调用工具类方法,上传图片
    try:
        image_name = image_storage(avatar.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="七牛云上传失败")

    # 4.判断图片是否上传成功
    if not image_name:
        return jsonify(errno=RET.NODATA, errmsg="上传图片失败")
    # 5.修改用户图片
    g.user.avatar_url = image_name

    # 6.返回响应,携带图片地址
    data = {
        "avatar_url": constants.QINIU_DOMIN_PREFIX + image_name
    }
    return jsonify(errno=RET.OK, errmsg="上传成功", data=data)


# 功能:设置获取用户基本信息
# 请求路径: /user/base_info
# 请求方式:GET,POST
# 请求参数:POST请求有参数,nick_name,signature,gender
# 返回值:errno,errmsg
@user_blue.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    """
    1.获取参数
    2.校验参数,为空检验
    3.修改用户信息
    4.返回响应
    :return:
    """
    if request.method == "GET":
        return render_template("news/user_base_info.html", user=g.user.to_dict())
    # 1.获取参数
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")
    # 2.校验参数,为空检验
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    if not gender in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.DATAERR, errmsg="性别异常")
    # 3.修改用户信息
    g.user.nick_name = nick_name
    g.user.signature = signature
    g.user.gender = gender
    # 4.返回响应
    return jsonify(errno=RET.OK, errmsg="修改成功")


# 请求路径: /user/info
# 请求方式:GET
# 请求参数:无
# 返回值: user.html页面,用户字典data数据
@user_blue.route('/info')
@user_login_data
def user_index():
    # 判断用户是否登陆
    if not g.user:
        return redirect("/")
    # 拼接数据返回页面
    data = {
        "user_info": g.user.to_dict()
    }
    return render_template("news/user.html", data=data)
