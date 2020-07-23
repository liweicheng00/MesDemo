from flask import (
    flash, redirect, url_for, current_app, session, abort
)
from flask_login import login_user, logout_user, login_required
from flask_principal import identity_changed, AnonymousIdentity, Identity
from werkzeug.security import check_password_hash, generate_password_hash
import json
from main.mes import *
from main.model import User, Role, AuthManager, db_session as db1


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
            error = 'Password is not the same.'
        elif User.query.filter_by(username=ID).first() is not None:
            error = 'User {} is already registered.'.format(ID)
            return redirect(url_for('frame.index1', error=error))

        if error is None:
            new_client = User(username=ID, password=generate_password_hash(pwd), name=name)
            db1.add(new_client)
            db1.commit()
            db1.remove()
            error = 'register success'
            return redirect(url_for('frame.index1', error=error))
        flash(error)
    return redirect(url_for('frame.index1', error=error))


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
    return render_template('main/framework/index.html', pre_error=pre_error, error=error)


@bp.route('/change_password', methods=('GET', 'POST'))
@login_required
# @admin_permission.require(http_exception=403)
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
    return redirect(url_for('frame.index1'))


@bp.route('/user_auth')
@login_required
def user_auth():

    return render_template('user_auth.html')


@bp.route('/ajax_getuser')
@login_required
# @admin_permission.require(http_exception=403)
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


@bp.route('/ajax_get_roles')
@login_required
def ajax_get_roles():
    roles = Role.query.order_by(Role.id).all()
    result = []
    for role in roles:
        temp = {}
        temp['id'] = role.id
        temp['role'] = role.role
        temp['chi_name'] = role.chi_name
        result.append(temp)
    return jsonify(result)


@bp.route('/ajax_updateuser', methods=['POST'])
@login_required
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


@bp.route('/route_auth')
@login_required
def route_auth():
    return render_template('route_auth_v1.html')


@bp.route("/ajax_add_role", methods=['POST'])
def ajax_add_role():
    data = request.get_data()
    data = json.loads(data)
    print('ajax_add_role')
    print(data)
    role = data['role']
    chi_name = data['chi_name']
    # for i in role:
    #     if i > u'\u4e00' or i < u'\u9fff':
    #         return jsonify({'msg': 'Role不能有中文'})
    new = Role(role=role, chi_name=chi_name)
    db1.add(new)
    db1.commit()
    return jsonify({'msg': '成功'})


@bp.route('/ajax_get_route')
@login_required
def ajax_get_route():
    print('ajax_get_route')
    q = AuthManager.query.order_by(AuthManager.page_url)\
        .filter(AuthManager.page_url == AuthManager.route_name).all()
    result = []
    for route in q:
        temp = route.to_dict()
        if temp['permission']:
            for role in temp['permission'].split(','):
                if role:
                    temp[role] = 1
        result.append(temp)
    return jsonify(result)


@bp.route('/ajax_get_page_route', methods=['POST'])
@login_required
def ajax_get_page_route():
    data = request.get_data()
    data = json.loads(data)
    print('ajax_get_page_route')
    print(data)
    q = AuthManager.query.order_by(AuthManager.page_url)\
        .filter(AuthManager.page_url == data['page_url'], AuthManager.page_url != AuthManager.route_name).all()
    result = []
    for route in q:
        temp = route.to_dict()
        if temp['permission']:
            for role in temp['permission'].split(','):
                if role:
                    temp[role] = 1
        result.append(temp)
    return jsonify(result)


@bp.route("/ajax_update_permission", methods=['POST'])
def ajax_update_permission():
    data = request.get_data()
    data = json.loads(data)
    print('ajax_update_permission')
    print(data)
    # if data['permission']:
    #     for per in data['permission'].split(','):
    #         q_role = Role.query.filter(Role.role == per).first()
    #         if not q_role:
    #             return jsonify({'msg': f"{per}角色不存在"}), 400
    q = AuthManager.query.filter(AuthManager.id == data['id']).first()
    if data['checked']:
        if q.permission:
            if data['field'] not in q.permission:
                q.permission = q.permission + ',' + data['field']
        else:
            q.permission = data['field']
    else:
        q.permission = q.permission.replace(data['field'], '')
        q.permission = q.permission.strip(',')

    db1.add(q)
    db1.commit()
    return jsonify({'mag': '成功'})


@bp.route('/ajax_update_route')
def ajax_update_route():
    print('ajax_update_route')
    all_routes = []
    for a in current_app.url_map.iter_rules():
        if str(a) not in \
                ['/static/<path:filename>', '/', '/frame', '/production', '/schedule', 'signing', 'revise', 'hello']:
            all_routes.append(str(a))
    # print("------")
    # print(len(all_routes))
    # print(len(set(all_routes)))
    #
    # all_routes.sort()
    # for r in all_routes:
    #     print(r)
    result = []
    for url in all_routes:
        q = AuthManager.query.filter(AuthManager.route_name == url).first()
        if not q:
            if url[:5] != '/ajax' or url[:4] == '/api':
                new = AuthManager(route_name=url, permission='', page_url=url)
            else:
                new = AuthManager(route_name=url, permission='')
            result.append(url)
            db1.add(new)
    db1.commit()
    return jsonify({'msg': f'成功，新增URL: {",".join(result)}'})


@bp.route('/ajax_special_delete')
def ajax_special_delete():
    data = request.args.get('data')
    q = AuthManager.query.filter(AuthManager.route_name == data).first()
    if q:
        db1.delete(q)
        db1.commit()
        return jsonify({"info": f'delete {data}'})

    else:
        return jsonify({"info": 'nothing'})