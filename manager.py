"""
1.数据库配置
2.redis配置
3.session配置,为后续登陆保持做铺垫
4.CSRFProtect配置
5.日志文件
6.数据库迁移

"""
from info import create_app, db ,models
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = create_app("develop")

# 创建Manager对象,管理app
manager = Manager(app)

# 关联db,app使用Migrate
Migrate(app, db)

# 给Migrate添加操作命令
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
