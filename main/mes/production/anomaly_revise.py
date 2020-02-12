import json
from flask import (
    jsonify, render_template, request
)
from flask_principal import Permission, RoleNeed

from main.mes.production import bp
from main.model import *
admin_permission = Permission(RoleNeed('super'))
user_permission = Permission(RoleNeed('user'))


@bp.route('/anomaly_revise')
def anomaly_revise():
    return render_template('main/production/anomaly_revise.html')


@bp.route("/ajax_revise_get_anomaly", methods=['GET'])
def ajax_revise_get_anomaly():
    q_anomaly = db_session.query(AnomalyList.anomaly_name, AnomalyList.anomaly_code,
                                 AnomalyTypeList.anomaly_type, AnomalyTypeList.anomaly_type_code)\
        .join(AnomalyTypeList, AnomalyList.anomaly_type_id == AnomalyTypeList.id).order_by(AnomalyList.anomaly_code).all()
    anomaly_list = []
    for anomaly in q_anomaly:
        temp = {}
        temp['anomaly_type'] = anomaly[2]
        temp['anomaly_type_code'] = anomaly[3]
        temp['anomaly_name'] = anomaly[0]
        temp['anomaly_code'] = anomaly[1]

        anomaly_list.append(temp)

    return jsonify(anomaly_list)


@bp.route("/ajax_revise_anomaly", methods=['POST'])
def ajax_revise_anomaly():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    revised = data['revised']
    original = data['original']
    q_anomaly = AnomalyList.query.filter(AnomalyList.anomaly_name == original['anomaly_name'],
                                         AnomalyList.anomaly_code == original['anomaly_code']).first()
    error = []
    if q_anomaly is None:
        error.append('數據異常')
        return jsonify({'state': 1, 'error': error})
        pass
    else:
        q_anomaly.anomaly_name = revised['anomaly_name']
        # q_anomaly.anomaly_code = revised['anomaly_code']
        db_session.add(q_anomaly)
        db_session.commit()

    return jsonify({'state': 0, 'error': error})


@bp.route("/ajax_add_anomaly", methods=['POST'])
def ajax_add_anomaly():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_anomaly = AnomalyList.query.filter(AnomalyList.anomaly_type_id == data['anomaly_type'])\
        .order_by(AnomalyList.anomaly_code.desc()).first()
    anomaly_code = q_anomaly.anomaly_code[:3]+str(int(q_anomaly.anomaly_code[3:])+1)
    new_anomaly = AnomalyList(anomaly_type_id=data['anomaly_type'], anomaly_name=data['anomaly_name'],
                              anomaly_code=anomaly_code)
    db_session.add(new_anomaly)
    db_session.commit()
    return jsonify({})


@bp.route("/ajax_delete_anomaly", methods=['POST'])
def ajax_delete_anomaly():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    error = []
    for dta in data:
        q_anomaly = AnomalyList.query.filter(AnomalyList.anomaly_code == dta['anomaly_code']).first()
        if q_anomaly is None:
            error.append('資料不存在')
            return jsonify({'state': 1, 'error': error})
            pass
        else:
            db_session.delete(q_anomaly)
            db_session.commit()

    return jsonify({'state': 0, 'error': error})

