from flask import abort, current_app, g, session, json, request
from info import db
from info.models import News, User, Comment, CommentLike
from info.modules.news import news_blue
from flask import render_template, jsonify

from info.utils.common import user_login_data
from info.utils.response_code import RET


# 功能:点赞
# 请求路径: /news/comment_like
# 请求方式: POST
# 请求参数:news_id,comment_id,action,g.user
# 返回值: errno,errmsg
@news_blue.route('/comment_like',methods=["POST"])
@user_login_data
def comment_like():
    """
    1.判断用户是否登陆
    2.获取参数
    3.校验参数
    4.校验操作类型
    5.通过评论编号,取出评论对象
    6.判断评论对象是否存在
    7.根据操作类型,点赞,或者取消点赞
    8.返回响应
    :return:
    """
    # 1.判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.DBERR, errmsg="用户未登陆")
    # 2.获取参数
    comment_id = request.json.get("comment_id")
    action = request.json.get("action")
    # 3.校验参数
    if not all([comment_id, action]):
        return jsonify(RET.NODATA, errmsg="参数不全")
    # 4.校验操作类型
    if not action in ["add", "remove"]:
        return jsonify(RET.PARAMERR, msg="操作类型错误")
    # 5.通过评论编号,取出评论对象
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="评论获取失败")
    # 6.判断评论对象是否存在
    if not comment:
        return jsonify(errno=RET.DBERR, errmsg="评论对象不存在")
    # 7.根据操作类型,点赞,或者取消点赞
    try:
        if action == "add":
            # 判断用户是否点过赞
            comments_like = CommentLike.query.filter(CommentLike.comment_id == comment_id,CommentLike.user_id == g.user.id).first()
            if not comment_like:
                # 创建点赞对象,设置属性
                comments_like = CommentLike()
                comments_like.comment_id = comment_id
                comments_like.user_id = g.user.id
                # 添加到数据库
                db.session.add(comments_like)
                db.session.commit()
                # 更新评论的点赞的数量
                comment.like_count += 1
        else:
            # 判断用户是否点过赞
            comment_likes = CommentLike.query.filter(CommentLike.comment_id == comment_id,CommentLike.user_id == g.user.id).first()
            if comment_likes:
                # 移除点赞对象
                db.session.remove(comment_likes)

                # 更新点赞数量
                comment.like_count -=1
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作失败")
    # 8.返回响应
    return jsonify(errno=RET.OK,errmsg="操作成功")


# 功能:新闻评论
# 请求路径: /news/news_comment
# 请求方式: POST
# 请求参数:news_id,comment,parent_id, g.user
# 返回值: errno,errmsg,评论字典

@news_blue.route('/news_comment', methods=["POST"])
@user_login_data
def mews_comment():
    """
    1.判断用户是否登陆
    2.获取参数
    3.校验参数.为空校验
    4.根据新闻编号,取出新闻
    5.判断新闻对象是否存在
    6.创建评论对象
    7.保存到数据库
    8.返回响应
    :return:
    """
    # 1.判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.DBERR, errmsg="用户未登陆")
    # 2.获取参数
    news_id = request.json.get("news_id")
    comments = request.json.get("comment")
    parent_id = request.json.get("parent_id")
    # 3.校验参数.为空校验
    if not all([news_id, comments]):
        return jsonify(errno=RET.DBERR, errmsg="参数不全")
    # 4.根据新闻编号,取出新闻
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")
    # 5.判断新闻对象是否存在
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")
    # 6.创建评论对象
    comment = Comment()
    comment.user_id = g.user.id
    comment.news_id = news_id
    comment.content = comments
    if parent_id:
        comment.parent_id = parent_id
    # 7.保存到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="评论失败")

    # 8.返回响应
    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())


# 功能:收藏&取消收藏
# 请求路径: /news/news_collect
# 请求方式: POST
# 请求参数:news_id,action, g.user
# 返回值: errno,errmsg
@news_blue.route('/news_collect', methods=["POST"])
@user_login_data
def news_collect():
    """
    1.判断用户是否登陆
    2.获取参数
    3.校验参数
    4.判断操作类型
    5.根枯新闻编号取出新闻对象
    6.判断新闻对象是否存在
    7.根据操作类型,收藏或者取消收藏
    8.返回响应
    :return:
    """
    # 1.判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登陆")
    # 2.获取参数
    # request.data可以获取未经处理过的原始数据，如果数据格式是json的，则取得的是json字符串，排序和请求参数一致
    json_data = request.data
    dict_data = json.loads(json_data)
    news_id = dict_data.get("news_id")
    action = dict_data.get("action")
    # 3.校验参数
    if not all([news_id, action]):
        return jsonify(errno=RET.DBERR, errmsg="参数不全")
    # 4.判断操作类型
    if not action in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.DATAERR, errmsg="操作类型有误")
    # 5.根枯新闻编号取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")

    # 6.判断新闻对象是否存在
    if not news:
        return jsonify(errno=RET.DBERR, errmsg="新闻对象不存在")
    # 7.根据操作类型,收藏或者取消收藏
    try:
        if action == "collect":
            # 判断是否收藏过该新闻
            if not news in g.user.collection_news:
                g.user.collection_news.append(news)
        else:
            if news in g.user.collection_news:
                g.user.collection_news.remove(news)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作失败")
    # 8.返回响应
    return jsonify(errno=RET.OK, errmsg="操作成功")


# 功能: 获取新闻详细信息
# 请求路径: /news/<int:news_id>
# 请求方式: GET
# 请求参数:news_id
# 返回值: detail.html页面, 用户data字典数据

@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    # 根据传入的新闻编号,获取新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")
    # 判断新闻是否存在
    if not news:
        abort(404)

    # 查询热门新闻数据
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(8).all()
    except Exception as e:
        current_app.logger.error(e)

    # 将新闻列表转换为字典列表
    click_news_list = []
    for new in news_list:
        click_news_list.append(new.to_dict())

    # 查询当前用户,是否有收藏新闻
    is_collected = False
    if g.user and news in g.user.collection_news:
        is_collected = True

    # 查询所有的评论
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取评论失败")
    try:
        # 获取用户的所有点赞对象
        comment_likes = []
        if g.user:
            comment_likes = g.user.comment_likes

        # 获取用户所有点赞过的评论编号
        comment_ids = []
        for comment_like in comment_likes:
            comment_ids.append(comment_like.comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR ,errmsg="获取点赞数据失败")

    # 将评论对象列表转成字典列表
    comments_list = []
    for comment in comments:
        com_dict = comment.to_dict()
        com_dict["is_like"] = False

        # 判断当前用户,是否对该评论点过赞
        if g.user and comment.id in comment_ids:
            com_dict["is_like"] = True

        comments_list.append(com_dict)

    # 判断当前用户,是否由关注当前新闻的作者
    is_followed = False
    if g.user and news.user:
        if g.user in news.user.followers:
            is_followed = True



    # 携带数据渲染页面
    data = {
        "news": news.to_dict(),
        "click_news_list": click_news_list,
        "user_info": g.user.to_dict() if g.user else "",
        "is_collected": is_collected,
        "comments": comments_list,
        "is_followed":is_followed
    }
    return render_template("news/detail.html", data=data)
