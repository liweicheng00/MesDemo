import datetime
import json

from flask import (
    jsonify, render_template, request
)
from flask_principal import Permission, RoleNeed

from main.mes.production import bp
from main.model import *

admin_permission = Permission(RoleNeed('super'))
user_permission = Permission(RoleNeed('user'))


@bp.route('/daily_bad_report')
def daily_bad_report():
    return render_template('main/production/daily_bad_report.html')


@bp.route('/daily_bad_report_query')
def daily_bad_report_query():
    return render_template('main/production/daily_bad_report_query.html')


@bp.route("/ajax_bad_list", methods=['GET'])
def ajax_bad_list():
    q_bad = BadList.query.all()
    result = []
    for bad in q_bad:
        result.append(bad.bad_name)
    return jsonify(result)


@bp.route("/ajax_bad_amount", methods=['POST'])
def ajax_bad_amount():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    bad_name = data['bad_name']
    daily_report_id = data['form_no']
    q_bad = BadList.query.filter(BadList.bad_name == bad_name).first()
    bad_id = q_bad.id

    q_bad_record = BadRecord.query.filter(BadRecord.daily_report_id == daily_report_id,
                                          BadRecord.bad_id == bad_id).count()

    return jsonify(q_bad_record)


@bp.route("/ajax_time", methods=['POST'])
def ajax_time():
    work_class = ''
    time = datetime.datetime.now().time()
    A = datetime.time(7, 30, 0)
    B = datetime.time(11, 30, 0)
    C = datetime.time(15, 30, 0)
    D = datetime.time(19, 30, 0)
    E = datetime.time(23, 30, 0)
    F = datetime.time(3, 30, 0)
    if time.__ge__(A) and time.__lt__(B):
        work_class = 'A'
    elif time.__ge__(B) and time.__lt__(C):
        work_class = 'B'
    elif time.__ge__(C) and time.__lt__(D):
        work_class = 'C'
    elif time.__ge__(D) and time.__lt__(E):
        work_class = 'D'
    elif time.__ge__(E) or time.__lt__(F):
        work_class = 'E'
    elif time.__ge__(F):
        work_class = 'F'
    data = request.get_data()
    data = json.loads(data)
    form_no = data['form_no']
    q_daily_class = DailyClassReport.query.filter(DailyClassReport.daily_report_id == form_no).all()
    if not q_daily_class:
        print('q_daily_class is None')
        return jsonify({'error': 'q_daily_class is None'})

    result = {}
    for daily_class in q_daily_class:
        temp = {}
        temp['box_number'] = daily_class.box_number
        temp['bad_amount'] = daily_class.bad_amount
        temp['box_pics'] = daily_class.ps
        result[daily_class.work_class] = temp
    result['work_class'] = work_class
    return jsonify(result)


@bp.route("/ajax_anomaly_type_list", methods=['GET'])
def ajax_anomaly_type_list():
    q_anomaly_type = AnomalyTypeList.query.all()
    result = {}
    for types in q_anomaly_type:
        result[str(types.id)] = types.anomaly_type

    return jsonify(result)


@bp.route("/ajax_anomaly_list", methods=['POST'])
def ajax_anomaly_list():
    data = request.get_data()
    data = json.loads(data)
    type_id = data['type_id']
    q_anomaly_list = AnomalyList.query.filter(AnomalyList.anomaly_type_id == type_id)
    result = []
    for anomaly in q_anomaly_list:
        result.append(anomaly.anomaly_name)
    return jsonify(result)


@bp.route("/ajax_get_machine_schedule", methods=['POST'])
def ajax_get_machine_schedule():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    date = data['date']
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    building = data['building']
    machine = data['machine']
    # part_number = data['part_number']
    # worker = data['worker']
    # QC = data['QC']
    q_machine = MachineList.query.filter(MachineList.building == building,
                                         MachineList.machine_name == machine).first()
    machine_id = q_machine.id
    q_schedule = ProduceSchedule.query.filter(ProduceSchedule.date == date,
                                              ProduceSchedule.machine_id == machine_id).all()
    error = ''
    result = []
    if not q_schedule:
        error = '今日無排產'
        # q_schedule = ProduceSchedule.query.filter(ProduceSchedule.machine_id == machine_id)\
        #     .order_by(ProduceSchedule.date.desc()).first()
        # temp = {}
        # temp['part_number'] = q_schedule.pn_list.part_number
        # temp['mold'] = q_schedule.mold_list.mold_number_f
        # temp['mold_id'] = q_schedule.mold_id
        # temp['machine_id'] = q_schedule.machine_id
        # result.append(temp)
        return jsonify({'state': 1, 'error': error, 'data': result})
    else:
        for schedule in q_schedule:
            temp = {}
            if len(q_schedule) > 1:
                error = '請選擇模具'
            temp['part_number'] = schedule.pn_list.part_number
            temp['mold'] = schedule.mold_list.mold_number_f
            temp['mold_id'] = schedule.mold_id
            temp['machine_id'] = schedule.machine_id
            result.append(temp)

    return jsonify({'state': 0, 'error': error, 'data': result})


@bp.route("/ajax_add_daily_report", methods=['POST'])
def ajax_add_daily_report():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    try:
        date = data['date']
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        building = data['building']
        machine = data['machine']
        part_number = data['part_number']
        mold = data['mold']
    except Exception as e:
        error = 'Can not find key: ' + str(e) + ' in data.'
        print(error)
        return jsonify({'error': error})

    q_daily = DailyReport.query.filter(DailyReport.date == date, DailyReport.building == building,
                                       DailyReport.machine == machine, DailyReport.part_number == part_number,
                                       DailyReport.mold == mold).first()
    if q_daily is None:
        new_daily_report = DailyReport(date=date, building=building, machine=machine,
                                       part_number=part_number, produce_amount=0,
                                       bad_amount=0, bad_percent=0, record_state=0, mold=mold)
        db_session.add(new_daily_report)
        db_session.commit()
        q_daily = DailyReport.query.filter(DailyReport.date == date, DailyReport.building == building,
                                           DailyReport.machine == machine, DailyReport.part_number == part_number,
                                           DailyReport.mold == mold).first()
        daily_report_id = q_daily.id
        for temp in ['A', 'B', 'C', 'D', 'E', 'F']:
            new_daily_class_report = DailyClassReport(daily_report_id=daily_report_id, work_class=temp,
                                                      bad_amount=0, box_number=0, box_name='')
            db_session.add(new_daily_class_report)
        db_session.commit()
    else:
        return jsonify({'state': 0, 'msg': '日報表存在', 'form_no': q_daily.id})

    error = []
    if error:
        return jsonify({'state': 1, 'error': error})
    else:
        return jsonify({'state': 0, 'msg': '日報表"新建"成功', 'form_no': q_daily.id})


@bp.route("/ajax_query_daily_report", methods=['POST'])
def ajax_query_daily_report():
    data = request.get_data()
    data = json.loads(data)
    # print(data)
    try:
        date = data['date']
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        building = data['building']
        machine = data['machine']
        part_number = data['part_number']
        mold = data['mold']
    except Exception as e:
        error = 'Can not find key: ' + str(e) + ' in data.'
        print(error)
        return jsonify({'error': error})

    q_daily = DailyReport.query.filter(DailyReport.date == date, DailyReport.building == building,
                                       DailyReport.machine == machine, DailyReport.part_number == part_number,
                                       DailyReport.mold == mold).first()
    if q_daily is None:
        return jsonify({'state': 1, 'msg': '無紀錄'})
    else:
        return jsonify({'state': 0, 'msg': '日報表存在', 'form_no': q_daily.id})


@bp.route("/ajax_amount_upload", methods=['POST'])
def ajax_amount_upload():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    box_pics = data['box_pics']
    daily_report_id = data['form_no']
    produce_amount = float(data['amount_1']) + float(data['amount_2'])
    work_class = data['work_class'][0]
    box_number = data['box_number']
    q_daily = DailyReport.query.filter(DailyReport.id == daily_report_id).first()
    q_daily.produce_amount = produce_amount
    db_session.add(q_daily)
    db_session.commit()

    if q_daily.produce_amount != 0:
        q_daily.bad_percent = 100 * q_daily.bad_amount / q_daily.produce_amount
        q_daily.bad_ppm = 1000000 * q_daily.bad_amount / q_daily.produce_amount
    else:
        q_daily.bad_percent = 0

    q_daily_class = DailyClassReport.query.filter(DailyClassReport.daily_report_id == daily_report_id,
                                                  DailyClassReport.work_class == work_class).first()
    q_daily_class.box_number = box_number
    q_daily_class.ps = box_pics
    db_session.add(q_daily_class)
    db_session.commit()
    return jsonify()


@bp.route("/ajax_additional_amount", methods=['POST'])
def ajax_additional_amount():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    daily_report_id = data['form_no']

    if 'additional_amount' in data.keys():
        q_daily = DailyReport.query.filter(DailyReport.id == daily_report_id).first()
        print(q_daily.produce_amount)
        print(q_daily.additional_amount)
        if q_daily.additional_amount is None:
            q_daily.additional_amount = 0
        produce_amount = q_daily.produce_amount-q_daily.additional_amount
        q_daily.additional_amount = data['additional_amount']
        q_daily.produce_amount = produce_amount + float(data['additional_amount'])
        db_session.add(q_daily)
        db_session.commit()
    else:
        q_daily = DailyReport.query.filter(DailyReport.id == daily_report_id).first()
        return jsonify({"additional_amount": q_daily.additional_amount})
    return jsonify()


@bp.route("/ajax_bad_upload", methods=['POST'])
def ajax_bad_upload():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    bad_name = data['bad_type']
    daily_report_id = data['form_no']
    move = data['move']
    time = datetime.datetime.now().time()
    A = datetime.time(7, 30, 0)
    B = datetime.time(11, 30, 0)
    C = datetime.time(15, 30, 0)
    D = datetime.time(19, 30, 0)
    E = datetime.time(23, 30, 0)
    F = datetime.time(3, 30, 0)
    if time.__ge__(A) and time.__lt__(B):
        work_class = 'A'
    elif time.__ge__(B) and time.__lt__(C):
        work_class = 'B'
    elif time.__ge__(C) and time.__lt__(D):
        work_class = 'C'
    elif time.__ge__(D) and time.__lt__(E):
        work_class = 'D'
    elif time.__ge__(E) or time.__lt__(F):
        work_class = 'E'
    elif time.__ge__(F):
        work_class = 'F'
    time = datetime.datetime.now()
    print(time)
    if move == 'add':
        q_daily_class = DailyClassReport.query.filter(DailyClassReport.daily_report_id == daily_report_id,
                                                      DailyClassReport.work_class == work_class).first()
        daily_class_id = q_daily_class.id
        q_bad = BadList.query.filter(BadList.bad_name == bad_name).first()
        bad_id = q_bad.id

        new_bad_record = BadRecord(daily_report_id=daily_report_id, daily_class_report_id=daily_class_id,
                                   bad_id=bad_id, record_time=time)
        db_session.add(new_bad_record)
        db_session.commit()

        q_daily = DailyReport.query.filter(DailyReport.id == daily_report_id).first()
        # q_daily.bad_amount = q_daily.bad_amount+1
        q_daily.bad_amount = BadRecord.query.filter(BadRecord.daily_report_id == daily_report_id).count()
        if q_daily.produce_amount != 0:
            q_daily.bad_percent = 100 * q_daily.bad_amount / q_daily.produce_amount
            q_daily.bad_ppm = 1000000 * q_daily.bad_amount / q_daily.produce_amount
        else:
            q_daily.bad_percent = 0

        # q_daily_class.bad_amount = q_daily_class.bad_amount+1
        q_daily_class.bad_amount = BadRecord.query.filter(BadRecord.daily_report_id == daily_report_id,
                                                          BadRecord.daily_class_report_id == daily_class_id).count()

        db_session.add(q_daily)
        db_session.add(q_daily_class)
        db_session.commit()
    elif move == 'last_bad':
        q_bad = BadList.query.filter(BadList.bad_name == bad_name).first()
        bad_id = q_bad.id
        q_bad_record = BadRecord.query.filter(BadRecord.daily_report_id == daily_report_id,
                                              BadRecord.bad_id == bad_id).order_by(BadRecord.record_time.desc()).first()
        result = {}
        result['bad_name'] = q_bad_record.bad_list.bad_name
        result['record_time'] = str(q_bad_record.record_time.time())
        return jsonify(result)

    elif move == 'minus':
        q_bad = BadList.query.filter(BadList.bad_name == bad_name).first()
        bad_id = q_bad.id
        q_bad_record = BadRecord.query.filter(BadRecord.daily_report_id == daily_report_id,
                                              BadRecord.bad_id == bad_id).order_by(BadRecord.record_time.desc()).first()
        print(q_bad_record.id)
        print(q_bad_record.record_time)
        db_session.delete(q_bad_record)
        db_session.commit()

        q_daily = DailyReport.query.filter(DailyReport.id == daily_report_id).first()
        # q_daily.bad_amount = q_daily.bad_amount - 1
        q_daily.bad_amount = BadRecord.query.filter(BadRecord.daily_report_id == daily_report_id).count()

        if q_daily.produce_amount != 0:
            q_daily.bad_percent = 100 * q_daily.bad_amount / q_daily.produce_amount
            q_daily.bad_ppm = 1000000 * q_daily.bad_amount / q_daily.produce_amount
        else:
            q_daily.bad_percent = 0

        q_daily_class = DailyClassReport.query.filter(DailyClassReport.daily_report_id == daily_report_id,
                                                      DailyClassReport.work_class == work_class).first()
        daily_class_id = q_daily_class.id
        # q_daily_class.bad_amount = q_daily_class.bad_amount - 1
        q_daily_class.bad_amount = BadRecord.query.filter(BadRecord.daily_report_id == daily_report_id,
                                                          BadRecord.daily_class_report_id == daily_class_id).count()
        db_session.add(q_daily)
        db_session.add(q_daily_class)
        db_session.commit()
    return jsonify()


@bp.route("/ajax_anomaly_upload", methods=['POST'])
def ajax_anomaly_upload():
    data = request.get_data()
    data = json.loads(data)
    print(data)

    daily_report_id = data['form_no']
    anomaly_type_id = data['anomaly_type']
    anomaly_msg = data['anomaly_msg']
    q_anomaly = AnomalyList.query.filter(AnomalyList.anomaly_type_id == anomaly_type_id,
                                         AnomalyList.anomaly_name == anomaly_msg).first()
    anomaly_id = q_anomaly.id
    date = data['date']
    time_range = data['time']
    lost_time = data['lost_time']
    if datetime.datetime.strptime(time_range[0:8], '%H:%M:%S') <= datetime.datetime.strptime(time_range[11:19], '%H:%M:%S'):
        end_time = date + ' ' + time_range[11:19]
    else:
        end_time = datetime.datetime.strftime(datetime.datetime.strptime(date, '%Y-%m-%d') + datetime.timedelta(days=1), '%Y-%m-%d')\
                   + ' ' + time_range[11:19]
    begin_time = date + ' ' + time_range[0:8]
    begin_time = datetime.datetime.strptime(begin_time, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    if data['responsible']:
        responsible = data['responsible']
    else:
        responsible = None
    if data['improve']:
        improve = data['improve']
    else:
        improve = None
    new_anomaly_record = AnomalyRecord(daily_report_id=daily_report_id, anomaly_id=anomaly_id,
                                       begin_time=begin_time, end_time=end_time, lost_time=lost_time,
                                       improve=improve, responsible=responsible)
    db_session.add(new_anomaly_record)

    q_daily = DailyReport.query.filter(DailyReport.id == daily_report_id).first()
    if q_daily.lost_time is None:
        q_daily.lost_time = 0
    q_daily.lost_time = q_daily.lost_time + round(float(lost_time), 2)
    db_session.add(q_daily)
    db_session.commit()
    return jsonify()


@bp.route("/ajax_delete_anomaly_record", methods=['POST'])
def ajax_delete_anomaly_record():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    error = []
    for dta in data:
        q_anomaly_record = AnomalyRecord.query.filter(AnomalyRecord.id == dta['id']).first()
        q_daily = DailyReport.query.filter(DailyReport.id == q_anomaly_record.daily_report_id).first()
        if q_anomaly_record is None:
            error.append('資料不存在')
            return jsonify({'state': 1, 'error': error})
            pass
        else:
            q_daily.lost_time = q_daily.lost_time-q_anomaly_record.lost_time
            db_session.delete(q_anomaly_record)
            db_session.commit()

    return jsonify({'state': 0, 'error': error})


@bp.route("/ajax_daily_report", methods=['POST'])
def ajax_daily_report():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    daily_report_id = data['form_no']
    daily = {}
    q_daily_report = DailyReport.query.filter(DailyReport.id == daily_report_id).first()
    daily['produce_amount'] = q_daily_report.produce_amount
    daily['bad_amount'] = q_daily_report.bad_amount
    daily['bad_percent'] = q_daily_report.bad_percent
    daily['bad_ppm'] = q_daily_report.bad_ppm
    daily['lost_time'] = q_daily_report.lost_time
    daily['real_cycle_time'] = q_daily_report.real_cycle_time

    q_bad_record = BadRecord.query.filter(BadRecord.daily_report_id == daily_report_id)\
        .order_by(BadRecord.record_time.desc()).all()
    b_statics = {}
    b_record = []
    for bad_record in q_bad_record:
        if not (bad_record.bad_list.bad_name in b_statics.keys()):
            b_statics[bad_record.bad_list.bad_name] = 0
        b_statics[bad_record.bad_list.bad_name] = b_statics[bad_record.bad_list.bad_name] + 1
        temp = {}
        temp['bad_name'] = bad_record.bad_list.bad_name
        temp['record_time'] = bad_record.record_time.strftime('%Y-%m-%d %H:%M:%S')
        b_record.append(temp)

    q_anomaly_record = AnomalyRecord.query.filter(AnomalyRecord.daily_report_id == daily_report_id).all()
    a_record = []
    for anomaly_record in q_anomaly_record:
        temp = {}
        temp['id'] = anomaly_record.id
        temp['anomaly_type'] = anomaly_record.anomaly_list.anomaly_type_list.anomaly_type
        temp['anomaly_name'] = anomaly_record.anomaly_list.anomaly_name
        temp['begin_time'] = anomaly_record.begin_time.strftime('%Y-%m-%d %H:%M:%S')
        temp['end_time'] = anomaly_record.end_time.strftime('%Y-%m-%d %H:%M:%S')
        temp['lost_time'] = anomaly_record.lost_time
        temp['responsible'] = anomaly_record.responsible
        temp['finish_date'] = anomaly_record.finish_date
        a_record.append(temp)

    return jsonify({'a': daily, 'b': b_statics, 'c': b_record, 'd': a_record})


@bp.route("/ajax_real_cycle_time", methods=['POST'])
def ajax_real_cycle_time():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    daily_report_id = data['form_no']
    real_cycle_time = data['real_cycle_time']
    q_daily_report = DailyReport.query.filter(DailyReport.id == daily_report_id).first()
    q_daily_report.real_cycle_time = real_cycle_time
    db_session.add(q_daily_report)
    db_session.commit()
    return jsonify({})
