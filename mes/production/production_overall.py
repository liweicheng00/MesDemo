import datetime
import json
from flask import jsonify, render_template, request, session

from mes.production import bp
from model import *
# from sqlalchemy.event import listen
# from sqlalchemy.pool import Pool
#
#
# def my_on_connect(dbapi_con):
#     print('new', dbapi_con)
#
#
# listen(db_session, 'after_commit', my_on_connect)


@bp.route('/production_overall')
def production_overall():
    return render_template('main/production/production_overall_horizontal_v2.html')


def fun_machine_list(building):

    return


def fun_compare_schedule_actual_chart(machine_list, now, today, amount, chart_order):

    return


@bp.route('/ajax_get_machine_state', methods=['GET'])
def ajax_get_machine_state():
    # data = request.get_data()
    # data = json.loads(data)
    # print(data)
    q_amount = db_session.query(Amount, MachineList).join(MachineList, MachineList.id == Amount.machine_id).all()
    result = {}
    for amount, machine in q_amount:
        result[machine.machine_name] = {"machine_name": machine.machine_name,
                                        "QcTolCnt": amount.produce_amount,
                                        "machine_state": amount.state,
                                        "building": "A18"}

    return jsonify(result)


@bp.route('/ajax_get_machine_detail', methods=['POST'])
def ajax_get_machine_detail():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_machine = MachineList.query.filter(MachineList.machine_name == data['machine_name'],
                                         MachineList.building == data['building']).first()

    return jsonify({"tonnage": q_machine.machine_tonnage, "type": q_machine.machine_type, "brand": q_machine.machine_brand})


@bp.route('/ajax_get_machine_detail_schedule', methods=['POST'])
def ajax_get_machine_detail_schedule():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    today = datetime.date.today()
    q_machine = MachineList.query.filter(MachineList.machine_name == data['machine_name'],
                                         MachineList.building == data['building']).first()
    q_schedule = ProduceSchedule.query.filter(ProduceSchedule.date == today,
                                              ProduceSchedule.machine_id == q_machine.id).first()
    result = {}
    if q_schedule is None:
        return jsonify({'amount': '-', 'mold': '-', 'error': 'schedule is None.'})
    else:
        q_mold = MoldList.query.filter(MoldList.id == q_schedule.mold_id).first()
        result['amount'] = q_schedule.amount
        result['inj_product_name'] = q_schedule.product_name
        result['mold'] = q_mold.mold_number + ' ' + q_mold.mold_number_f
        result['cave'] = q_mold.cave_number

    return jsonify(result)

