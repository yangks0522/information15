from flask import session, jsonify
from info import redis_store
from info.models import User, News
from info.utils.response_code import RET
from . import index_blue
from flask import render_template, current_app


@index_blue.route("/")
def hello_world():
    # 获取用户的编号,从session
    user_id = session.get("user_id")
    # 判断用户是否存在
    user = None
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)

    # 根据数据库,根据点击量查询十条新闻
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR ,errmsg="查询新闻异常")
    # 将新闻列表转换为字典列表
    click_news_list = []
    for news in news_list:
        click_news_list.append(news.to_dict())


    # 将用户的信息转成字典
    dict_data = {
        # 如果user存在,返回左边,否则返回右边
        "user_info": user.to_dict() if user else "",
        "click_news_list":click_news_list,
    }

    return render_template("news/index.html", data=dict_data)


# 只需要写对应的接口,返回一张图片即可
# 解决:current_app.send_static_file,自动static文件夹中寻找指定的资源
@index_blue.route('/favicon.ico')
def web_logo():
    return current_app.send_static_file("news/favicon.ico")
