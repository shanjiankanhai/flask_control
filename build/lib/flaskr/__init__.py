""""
# 包含应用工厂
# 告诉Python flaskr文件夹应当视作一个包
"""
import os

from flask import Flask


# 应用工厂函数
def create_app(test_config=None):
    # create and configure the app                                     # 创建flask实例（对象）__name__是当前Python模块的名称
    app = Flask(__name__, instance_relative_config=True)               # instance_relative_config=True告诉应用配置文件是相对于instance folder的相对路径
    app.config.from_mapping(                                           # 设置一个应用的缺省配置
        SECRET_KEY='dev',                                              # 保证数据安全
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),     # 数据文件存放路径
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)                # 使用config.py中的值来重载缺省配置
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)                                   # 确保app.instance_path存在
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    @app.route('/')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)                    # 导入并注册蓝图auth

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')             # 关联端点名称'index'和/ URL,是url_for()函数返回生成同样的/ URL

    return app
