"""
# 认证蓝图，包括注册、登录和注销视图
#
"""
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')     # 建立一个名为auth的蓝图，url_prefix会添加到所有与该蓝图关联的URL前面


# @bp.route关联了URL/register和register视图函数，当flask收到一个指向/auth/register的请求时就会调用register视图函数并把其返回值作为响应
@bp.route('/register', methods=('GET', 'POST'))          # 访问/auth/register URL时，register视图函数返回一个HTML页面
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:                              # 未提交用户名
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(                              # 按照提交的用户名在数据库的user表中查找id
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',     # 查询不到用户才可以注册
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))     # url_for()函数根据登录视图的名称生成相应的URL，redirect()函数为生成的URL生成一个重定向响应，及跳转到url_for()生成的URL，即注册完成后自动跳转到登录页，函数退出不再执行下一个return

        flash(error)

    return render_template('auth/register.html')       # 检查表单缺少信息后，重新返回注册页面，render_template()会渲染一个包含HTML的模板，条件是上一个return没有执行


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()                                                   # fetchone()函数返回一个记录行

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):       # check_password_hash()以相同的方式哈希提交的密码比较哈希值
            error = 'Incorrect password.'

        if error is None:
            session.clear()                                           # session是一个dict，用于存储横跨请求的值，当验证成功后，用户的ID会被存储于一个新的会话中，会话数据被存储到一个向浏览器发送的cookie中，在后续的请求中，浏览器会返回它
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# 注册一个在视图函数之前运行的函数，不论其URL是什么
@bp.before_app_request
def load_logged_in_user():                    # 检查用户ID是否已经存储在session中，并从数据库中获取用户数据，然后存储在g.user中
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


# 注销的时候需要把用户ID从session中移除，然后load_logged_in_user就不会在后继请求中载入用户了
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# 用户在登录以后才能创建、编辑和删除博客帖子，在每个视图中都可以使用装饰器来完成工作
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
