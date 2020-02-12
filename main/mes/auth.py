from flask import (
    flash, redirect, url_for, current_app, session, abort
)
from flask_login import login_user, logout_user, login_required
from flask_principal import identity_changed, AnonymousIdentity, Identity
from werkzeug.security import check_password_hash, generate_password_hash

from main.mes import *
from main.model import User, Role, db_session as db1


def next_is_valid(url):
    """確認重新定向url是否安全，暫時設定為true"""
    return True


@bp.route('/register', methods=('GET', 'POST'))
def register():
    error = None
    if request.method == 'POST':
        ID = request.form['ID']
        name = request.form['name']
        pwd = request.form['pwd']
        pwd_confirm = request.form['pwd_confirm']
        error = None
        if not ID:
            error = 'Username is required.'
        elif not pwd:
            error = 'Password is required.'
        elif not pwd == pwd_confirm:
            error = 'Password is the same.'
        elif User.query.filter_by(username=ID).first() is not None:
            error = 'User {} is already registered.'.format(ID)
            return redirect(url_for('auth.login', error=error))

        if error is None:
            new_client = User(username=ID, password=generate_password_hash(pwd), name=name)
            db1.add(new_client)
            db1.commit()
            db1.remove()
            error = 'register success'
            return redirect(url_for('auth.login', error=error))
        flash(error)
    return render_template('register.html', error=error)


@bp.route('/', methods=('GET', 'POST'))
def login():
    pre_error = request.args.get('error')
    print('pre_error:', pre_error)
    flash(pre_error)
    error = None
    if request.method == 'POST':
        username = request.form['ID']
        password = request.form['pwd']

        user = User.query.filter_by(username=username).first()

        if user is None:
            error = 'ID is not exist.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        print('error:', error)
        if error is None:
            identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
            # print(identity.provides)
            login_user(user)
            next = request.args.get('next')
            if not next_is_valid(next):
                return 'What do you want to do!'

            return redirect(next or url_for('frame.index1'))

        flash(error)
    return render_template('login.html', pre_error=pre_error, error=error)


@bp.route('/change_password', methods=('GET', 'POST'))
@login_required
@admin_permission.require(http_exception=403)
def change_password():
    error = None
    if request.method == 'POST':
        ID = request.form['ID']
        pwd = request.form['pwd']
        pwd_confirm = request.form['pwd_confirm']
        error = None
        if not ID:
            error = 'Username is required.'
        elif not pwd:
            error = 'Password is required.'
        elif not pwd == pwd_confirm:
            error = 'Password is the same.'

        if error is None:
            user = User.query.filter_by(username=ID).first()
            user.password = generate_password_hash(pwd)
            db1.add(user)
            db1.commit()
            db1.remove()
            error = 'revise success'
            # return redirect(url_for('auth.login', error=error))
        flash(error)
    return render_template('change_password.html', error=error)


@bp.route('/logout')
def logout():
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    return 'logged out <br> ' + '''<a href='/login'>login</a>'''


@bp.route('/user_auth')
@login_required
def user_auth():
    if not admin_permission.can():
        abort(403)
    return render_template('user_auth.html')


@bp.route('/ajax_getuser')
@login_required
@admin_permission.require(http_exception=403)
def ajax_getuser():
    users = User.query.order_by(User.id).all()
    result = []
    for user in users:
        user.role  # 沒這行找不到role
        user = user.to_dict()
        # print(user)
        temp = []
        if 'role' in user:
            for roles in user['role']:
                temp.append(roles.role)
                user['role'] = temp
        result.append(user)
    return jsonify(result)


@bp.route('/ajax_getrole')
@login_required
@admin_permission.require()
def ajax_getrole():
    roles = Role.query.order_by(Role.id).all()
    result = []
    for role in roles:
        temp = {}
        temp['id'] = role.id
        temp['role'] = role.role
        result.append(temp)
    return jsonify(result)


@bp.route('/ajax_updateuser', methods=['POST'])
@login_required
@admin_permission.require()
def ajax_updateuser():
    data = request.form.to_dict()
    data_role = data['role'].split(",")
    roles = []
    for role in data_role:
        temp = Role.query.filter_by(role=role).first()
        if temp is not None:
            roles.append(temp)
        else:
            return jsonify({'error': '角色不存在'})
    user = User.query.filter_by(id=data['id']).first()
    user.role = roles
    db1.add(user)
    db1.commit()
    db1.remove()
    return jsonify()  # Return json object to make ajax success.
