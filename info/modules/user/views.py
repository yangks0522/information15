from flask import g, jsonify
from flask import redirect
from flask import render_template
from flask import request

from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import user_blue


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
    return jsonify(errno=RET.OK,errmsg="修改成功")


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
