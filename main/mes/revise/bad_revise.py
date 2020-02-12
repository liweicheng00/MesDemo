import json
from flask import (
    jsonify, render_template, request
)
from flask_principal import Permission, RoleNeed

from main.mes.revise import bp
from main.model import *
admin_permission = Permission(RoleNeed('super'))
user_permission = Permission(RoleNeed('user'))


@bp.route('/bad_revise')
def bad_revise():
    return render_template('main/revise/bad_revise.html')


@bp.route("/ajax_revise_get_bad", methods=['GET'])
def ajax_revise_get_bad():
    q_bad = BadList.query.all()

    bad_list = []
    for bad in q_bad:
        temp = {}
        temp['bad_name'] = bad.bad_name
        temp['bad_code'] = bad.bad_code
        bad_list.append(temp)

    return jsonify(bad_list)


@bp.route("/ajax_revise_bad", methods=['POST'])
def ajax_revise_bad():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    revised = data['revised']
    original = data['original']
    q_bad = BadList.query.filter(BadList.bad_name == original['bad_name'], BadList.bad_code == original['bad_code']).first()
    error = []
    if q_bad is None:
        error.append('數據異常')
        return jsonify({'state': 1, 'error': error})
        pass
    else:
        q_bad.bad_name = revised['bad_name']
        q_bad.bad_code = revised['bad_code']
        db_session.add(q_bad)
        db_session.commit()

    return jsonify({'state': 0, 'error': error})


@bp.route("/ajax_add_bad", methods=['POST'])
def ajax_add_bad():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    new_bad = BadList(bad_name=data['bad_name'], bad_code=data['bad_code'])
    db_session.add(new_bad)
    db_session.commit()
    return jsonify({})


@bp.route("/ajax_delete_bad", methods=['POST'])
def ajax_delete_bad():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    error = []
    for dta in data:
        q_bad = BadList.query.filter(BadList.bad_name == dta['bad_name'], BadList.bad_code == dta['bad_code']).first()

        if q_bad is None:
            error.append('資料不存在')
            return jsonify({'state': 1, 'error': error})
            pass
        else:
            db_session.delete(q_bad)
            db_session.commit()

    return jsonify({'state': 0, 'error': error})

