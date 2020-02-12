import time
import json
import datetime

from flask import (
    jsonify, render_template, request
)
from flask_principal import Permission, RoleNeed

from main.mes.production import bp
from main.model2 import *
from main.model2 import db_session as db_model2
from main.model1 import *
from main.model1 import db_session as db_model1

admin_permission = Permission(RoleNeed('super'))
user_permission = Permission(RoleNeed('user'))


@bp.route('/alm_monitor', methods=['GET'])
def alm_monitor():

    return render_template('main/production/Alm_monitor.html')


@bp.route("/ajax_alm", methods=['GET', 'POST'])
def ajax_alm():
    data = request.form.to_dict()
    # print(data['37846573480'])
    # 避免資料庫內有不合理的時間
    few_time_later = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 60 * 5))
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    if data['time'] == '':
        data['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 60 * 300))
    alarms = AlmRecord.query.filter(AlmRecord.AlmTime >= data['time'],
                                    AlmRecord.AlmTime <= few_time_later).all()  # 十分鐘內警報
    states = InjParam.query.all()
    sta = []
    for state in states:
        state = state.to_dict()
        sta.append(state)
    alm = []
    for alarm in alarms:
        alarm = alarm.to_dict()
        alarm['AlmTime'] = str(alarm['AlmTime'])  # 更改時間格式
        alm.append(alarm)
    result = {'alm': alm, 'state': sta, 'update_time': now_time}
    return jsonify(result)


@bp.route('/bf_end_monitor_index')
def bf_end_monitor_index():
    return render_template('main/production/ctMonitor_index.html')


@bp.route('/bf_end_monitor', methods=['GET'])
def bf_end_monitor():
    return render_template('main/production/ctMonitoring_revise.html', id1='B12')


@bp.route("/ajax_bf_end", methods=['GET', 'POST'])
def ajax_bf_end():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    data['BeginTime'] = int(data['BeginTime'])
    now = datetime.datetime.now()
    q_alm = db_model2.query(AlmRecord.MachineId, AlmRecord.AlmTime, AlmRecord.AlmMsg)\
        .filter(AlmRecord.MachineId == data['machineid'],
                AlmRecord.AlmTime > now + datetime.timedelta(seconds=data['BeginTime']))\
        .order_by(AlmRecord.AlmTime.desc()).all()

    Alm = []
    for alm in q_alm:
        Alm.append([str(alm.AlmTime), alm.AlmMsg])

    q_mdy = db_model2.query(MdyRecord.MachineId, MdyRecord.MdyTime, MdyRecord.MdyAddr) \
        .filter(MdyRecord.MachineId == data['machineid'],
                MdyRecord.MdyTime >= now + datetime.timedelta(seconds=data['BeginTime'])) \
        .order_by(MdyRecord.MdyTime.desc()).all()
    Mdy = []
    for mdy in q_mdy:
        Mdy.append([str(mdy.MdyTime), mdy.MdyAddr])

    q_bf = db_model2.query(SpcRecord.MachineId, SpcRecord.TimeStemp, SpcRecord.BfInjEnd)\
        .filter(SpcRecord.MachineId == data['machineid'],
                SpcRecord.TimeStemp >= now + datetime.timedelta(seconds=data['BeginTime']))\
        .order_by(SpcRecord.TimeStemp.desc()).all()
    Data = []
    for bf in q_bf:
        Data.append([str(bf.TimeStemp), bf.BfInjEnd])

    q_state = db_model2.query(InjParam.MachStateId)\
        .filter(InjParam.MachineId == data['machineid']).first()
    State = [[q_state]]
    result = {'Alm': Alm, 'Data': Data, 'Mdy': Mdy, 'State': State}
    return jsonify(result)


@bp.route("/ajax_bf_end_var", methods=['GET', 'POST'])
def ajax_bf_end_var():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_var = BfInjEndMonitor.query.filter(BfInjEndMonitor.machineid == data['machineid']).first()
    Error = []
    Error.append([str(q_var.start_time), str(q_var.end_time), q_var.error, q_var.machineid, q_var.trend])
    return jsonify({'Error': Error})

