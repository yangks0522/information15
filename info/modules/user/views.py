from flask import current_app
from flask import g, jsonify
from flask import redirect
from flask import render_template
from flask import request

from info import constants
from info.utils.image_storage import image_storage
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import user_blue


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
    if not all([old_password,new_password]):
        return jsonify(errno=RET.DBERR,errmsg="参数不全")
    # 3.判断旧密码是否正确
    if not g.user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR,errmsg="旧密码不正确")
    # 4.设置新密码
    g.user.password = new_password
    # 5.返回响应
    return jsonify(errno=RET.OK,errmsg="修改成功")

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
