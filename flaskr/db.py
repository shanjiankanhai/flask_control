"""
# 定义和操作数据库
"""
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


# 连接数据库
def get_db():
    if 'db' not in g:                                          # g为一个特殊对象，独立于每一个请求，存储多个函数可能要用的数据
        g.db = sqlite3.connect(                                # sqlite3.connect()建立一个数据库连接，并指向g.db
            current_app.config['DATABASE'],                    # current_app是另一个特殊对象，只想处理请求的Flask应用，当应用创建后，在处理一个请求时，get_db会被调用
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row                         # sqlite3.Row告诉连接返回类似字典的行

    return g.db


# 检查g.db来确定连接是否已经建立；如果连接已经建立，那么就关闭连接
def close_db(e=None):
    db = g.pop('db', None)                       # 从对象g中抛出db并返回给变量，抛出的g.db为一个数据库连接

    if db is not None:
        db.close()


# 初始化数据库
def init_db():
    db = get_db()                                 # 返回一个数据库连接，用于执行文件中的命令

    with current_app.open_resource('schema.sql') as f:     # open_resource()函数打开一个文件，该文件名相对于flaskr包
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')                            # 定义一个名为init-db的命令行，它调用init_db函数，并为用户显示一个成功的消息
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


# 初始化管理员账户表单
def init_administrator():
    db = get_db()

    with current_app.open_resource('schema_administrator') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-administrator')                # 添加一个初始化管理员的命令
@with_appcontext
def init_administrator_command():
    init_administrator()
    click.echo("Initialized the administrator")


# 把应用作为参数，在函数中注册
def init_app(app):
    app.teardown_appcontext(close_db)                       # 告诉Flask在返回响应后进行清理的时候调用此函数
    app.cli.add_command(init_db_command)                    # 添加一个新的可以与Flask一起工作的命令
    app.cli.add_command(init_administrator_command)         #
