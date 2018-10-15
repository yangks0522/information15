
import random
import re

from flask import request, jsonify, current_app, make_response, json
from info import constants, redis_store
from info.libs.yuntongxun.sms import CCP
from info.modules.passport import passport_blue
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET


# 功能:发送短信验证码
# 请求路径: /passport/sms_code
# 请求方式: POST
# 请求参数: mobile, image_code,image_code_id
# 返回值: errno, errmsg
# mobile		手机号
# image_code	图片验证码内容
# image_code_id	图片验证码编号
@passport_blue.route('/sms_code', methods=["POST"])
def sms_code():
    """
    1.获取参数
    2.校验参数.为空校验
    3.校验手机号格式是否正确
    4.通过验证码编号取出redis中的图片验证码A
    5.判断验证码A是否过期
    6.删除,redis中的图片验证码
    7.判断验证码A和传入进来的图片验证码是否相等
    8.生成短信验证码
    9.发送短信验证码,调用ccp方法
    10.存储短信验证码到redis中
    11.返回发送状态
    :return:
    """
    # 1.获取参数
    # post请求 request.data
    json_data = request.data
    # 将json转成字典
    dict_data = json.loads(json_data)
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")
    # 2.校验参数.为空校验
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    # 3.校验手机号格式是否正确
    if not re.match("1[35789]\d{9}", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号格式错误")
    # 4.通过验证码编号取出redis中的图片验证码A
    try:
        redis_image_code = redis_store.get("image_code:%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取图片验证码异常")

    # 5.判断验证码A是否过期
    if not redis_image_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")
    # 6.删除,redis中的图片验证码
    try:
        redis_store.delete("image_code:%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="图片验证码操作异常")

    # 7.判断验证码A和传入进来的图片验证码是否相等
    if redis_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码填写错误")
    # 8.生成短信验证码
    sms_code = "%06d" % random.randint(0, 999999)
    # 9.发送短信验证码,调用ccp方法
    ccp = CCP()
    try:
        result = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="云通讯发送异常")
    if result == -1:
        return jsonify(errno=RET.DATAERR, errmsg="短信发送失败")

    # 10.存储短信验证码到redis中
    try:
        redis_store.set("sms_code:%s" % mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")
    # 11.返回发送状态
    return jsonify(errno=RET.OK, errmsg="发送成功")


# 获取返回.一张图片
# 请求路径: /passport/image_code
# 请求方式: GET
# 请求参数: cur_id, pre_id
# 返回值: 图片验证码
# image_data


@passport_blue.route('/image_code')
def image_code():
    """
    1.获取参数
    2.校验参数(为空校验)
    3.生成图片验证码
    4.保存图片验证码到redis
    5.判断是否由上个图片验证码编号,有则删除
    6.返回图片验证码即可
    :return:
    """
    # 1.获取参数
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")
    # 2.校验参数(为空校验)
    if not cur_id:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码编号不存在")
    # 3.生成图片验证码
    name, text, image_data = captcha.generate_captcha()
    try:
        # 4.保存图片验证码到redis constants验证码有效期
        redis_store.set("image_code:%s" % cur_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
        # 5.判断是否由上个图片验证码编号,有则删除
        if pre_id:
            redis_store.delete("image_code%s" % pre_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="图片验证码异常")

    # 6.返回图片验证码即可
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/jpg"
    return response
