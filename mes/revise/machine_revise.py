import json
from mes.revise import *
from model import *


@bp.route('/machine_revise')
def machine_revise():
    return render_template('main/revise/machine_revise.html')


@bp.route("/ajax_revise_get_machine", methods=['POST'])
def ajax_revise_get_machine():
    data = request.get_data()
    data = json.loads(data)
    print('ajax_revise_get_machine')
    print(data)

    q_machine = MachineList.query.all()
    result = {}
    for machine in q_machine:
        result[machine.machine_code] = {'building': machine.building,
                                        'machine_name': machine.machine_name,
                                        'id': machine.id,
                                        'machine_code': machine.machine_code,
                                        'machine_type': machine.machine_type,
                                        'machine_location': machine.machine_location,
                                        'machine_brand': machine.machine_brand,
                                        'machine_no': machine.machine_no,
                                        'machine_tonnage': machine.machine_tonnage,
                                        }
    return jsonify(result)


@bp.route("/ajax_revise_machine", methods=['POST'])
def ajax_revise_machine():
    data = request.get_data()
    data = json.loads(data)
    print('ajax_revise_machine')
    print(data)

    revised = data['revised']
    original = data['original']
    event = data['event']

    q_machine = MachineList.query.filter(MachineList.id == original['id']).first()
    if event == 'opc_id':
        try:
            q_opc = MachineList.query.filter(MachineList.opc_id == revised['opc_id']).first()
        except Exception as e:
            return jsonify({'msg': str(e)}), 400
        else:
            if q_opc is not None:
                return jsonify({'msg': 'opc_id: {} 已存在'.format(revised['opc_id'])}), 400
        q_machine.opc_id = revised['opc_id']
    if event == 'ms_id':
        try:
            q_ms = MachineList.query.filter(MachineList.ms_id == revised['ms_id']).first()
        except Exception as e:
            return jsonify({'msg': str(e)}), 400
        else:
            if q_ms is not None:
                return jsonify({'msg': 'ms_id: {} 已存在'.format(revised['ms_id'])}), 400
        q_machine.ms_id = revised['ms_id']
    db_session.add(q_machine)
    db_session.commit()

    return jsonify({"msg": '修改成功'})