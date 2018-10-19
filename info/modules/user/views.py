from flask import g
from flask import redirect
from flask import render_template

from info.utils.common import user_login_data
from . import user_blue


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
