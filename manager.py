"""
1.数据库配置
2.redis配置
3.session配置,为后续登陆保持做铺垫
4.CSRFProtect配置
5.日志文件
6.数据库迁移

"""
from flask import current_app

from info import create_app, db ,models
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from info.models import User

app = create_app("develop")

# 创建Manager对象,管理app
manager = Manager(app)

# 关联db,app使用Migrate
Migrate(app, db)

# 给Migrate添加操作命令
manager.add_command("db", MigrateCommand)


# @manager.option()可以通过命令行的方法调用程序
# 参数1:表示参数名称,参数2:表示参数参数名描述信息,参数3:表示用来传递方法的形式参数中
@manager.option('-p', '--password', dest='password')
@manager.option('-u', '--username', dest='username')
def create_superuser(username,password):
    # 1.创建管理员对象
    admin = User()
    # 2.设置对象
    admin.nick_name = username
    admin.password_hash = password
    admin.mobile = username
    admin.is_admin = True
    try:
        db.session.add(admin)
        db.session.commit
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return "创建失败"

    # 3.保存到数据库
    return "创建成功"

if __name__ == "__main__":
    # print(app.url_map)
    manager.run()
