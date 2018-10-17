from flask import abort
from flask import current_app

from info.models import News
from info.modules.news import news_blue
from flask import render_template, jsonify
from info.utils.response_code import RET


# 功能: 获取新闻详细信息
# 请求路径: /news/<int:news_id>
# 请求方式: GET
# 请求参数:news_id
# 返回值: detail.html页面, 用户data字典数据


@news_blue.route('/<int:news_id>')
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
    data = {
        "news": news.to_dict(),
        "click_news_list": click_news_list,
    }
    return render_template("news/detail.html", data=data)