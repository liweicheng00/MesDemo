from flask import (
    render_template, abort
)
from flask_login import login_required, current_user
from flask_principal import Permission, RoleNeed

from main.mes.framework import bp

admin_permission = Permission(RoleNeed('super'))
user_permission = Permission(RoleNeed('user'))


@bp.route('/index1')
@login_required
def index1():
    user = current_user.username
    name = current_user.name
    return render_template('main/framework/index1.html', user=user, name=name)


@bp.route('/index2')
def index2():
    user = current_user.username
    name = current_user.name
    return render_template('main/framework/index2.html', user=user, name=name)


@bp.route('/index3')
# @admin_permission.require(http_exception=403)
def index3():
    user = current_user.username
    name = current_user.name
    return render_template('main/framework/index3.html', user=user, name=name)


@bp.errorhandler(403)
def no_permission(e):
    return render_template('no_authority.html')


# todo: 匿名帳號處理
@bp.route('/protected')
def protected():
    return 'is_active:{}'.format(current_user.is_active) + '<br>' \
           + 'is_anonymous:{}'.format(current_user.is_anonymous) + '<br>' \
           + 'is_active:{}'.format(current_user.is_active) + '<br>' \
           + 'is_authenticated:{}'.format(current_user.is_authenticated) + '<br>' \
           + 'Logged in as:{}'.format(current_user.username) + '<br>' \
           + 'Permission admin: {}'.format(admin_permission.can()) + '<br>' \
           + 'Permission user: {}'.format(user_permission.can())


@bp.route('/screen_size')
def screen_size():
    return render_template('main/framework/screen_size.html')


@bp.route('/cookies_view')
def cookies_view():
    return render_template('main/framework/cookie_view.html')


@bp.route('/hellosocket')
def hellosocket():
    return render_template('main/framework/hellosocket.html')