from flask import (
    jsonify, render_template
)

from mes.schedule import bp
from model import *


@bp.route('/schedule_overall')
def schedule_overall():
    return render_template('main/schedule/schedule_v1.html')


@bp.route("/ajax_machine_resource", methods=['GET'])
def ajax_machine_resource():
    # q_schedule = ProduceSchedule.query.filter(ProduceSchedule.date >= datetime.date.today()).all()
    # q_machine = MachineList.query.filter(MachineList.machine_tonnage == '450T').all()
    q_machine = MachineList.query.filter().all()

    result = []
    for machine in q_machine:
        temp = {}
        temp['id'] = machine.machine_code
        temp['building'] = machine.building

        temp['machine_tonnage'] = machine.machine_tonnage
        temp['machine_name'] = machine.machine_name
        result.append(temp)
    return jsonify(result)


@bp.route("/ajax_schedule_resource", methods=['GET'])
def ajax_schedule_resource():
    q_schedule = ProduceSchedule.query.all()
    # start = request.args.get('start')
    # end = request.args.get('end')
    # start = datetime.datetime.strptime(start[:10], "%Y-%m-%d")
    # end = datetime.datetime.strptime(end[:10], "%Y-%m-%d")
    # q_schedule = ProduceSchedule.query.filter(ProduceSchedule.date >= start, ProduceSchedule.date <= end).all()
    result = []

    for schedule in q_schedule:
        temp = {}
        temp['title'] = schedule.pn_list.inj_product_name + "-" + schedule.mold_list.mold_number_f + "-" + str(
            schedule.amount)[:-2]
        temp['allDay'] = 1
        temp['start'] = str(schedule.date)
        temp['resourceId'] = schedule.machine_list.machine_code
        temp['id'] = temp['resourceId'] + '-' + schedule.date.strftime('%y%m%d') + '-' + str(schedule.id)
        temp['extendedProps'] = {'inj_product_name': schedule.pn_list.inj_product_name,
                                 'part_number': schedule.pn_list.part_number,
                                 'mold': schedule.mold_list.mold_number_f,
                                 'mold_number': schedule.mold_list.mold_number,
                                 'date': str(schedule.date),
                                 'amount': str(schedule.amount)[:-2],
                                 "id": temp['id'],
                                 "resourceId": temp['resourceId'],
                                 "produce_order": schedule.produce_order}
        result.append(temp)
    return jsonify(result)
