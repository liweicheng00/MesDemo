from flask_socketio import SocketIO, emit
from main.mes.production.production_overall import fun_machine_list, fun_compare_schedule_actual_chart
import datetime
from main.model import *
from main.tictoc import *
from flask import jsonify, session


def init_socket(socket):
    @socket.on('connect')
    def connect():
        print('One socket connected.')

    @socket.on('disconnect')
    def disconnect():
        print('One socket disconnected!')

    @socket.on('my_event')
    def my_event(json):
        print(json)
        emit('my_event', 'my_event')

    @socket.on('get_machine_state')
    def get_machine_state(json):
        print(json['data'])
        t = tic()
        if 'machine_list' in session.keys():
            machine_list = session['machine_list']
        else:
            machine_list = fun_machine_list("A18")
            session['machine_list'] = machine_list
        now = datetime.datetime.now()
        if now.time() < datetime.time(7, 40, 0):
            tomorrow = datetime.datetime(now.year, now.month, now.day, 7, 40, 0)
            today = tomorrow + datetime.timedelta(days=-1)
        else:
            today = datetime.datetime(now.year, now.month, now.day, 7, 40, 0)
            tomorrow = today + datetime.timedelta(days=1)
        # todo: 加速這個查詢

        q_count = db_session.query(SpcRecord.MachineId, func.count('*').label('count')) \
            .filter(SpcRecord.TimeStemp >= str(today), SpcRecord.TimeStemp < str(tomorrow)) \
            .group_by(SpcRecord.MachineId)

        amount = {}
        # todo: 乘上模穴數
        for count in q_count:
            amount[count.MachineId] = count.count * 2

        result = []
        q_state = db_model2.query(InjParam.MachineId, InjParam.MachStateId, InjParam.CstAvgTime).all()
        state = {}
        for sta in q_state:
            state[sta[0]] = {'machine_conn_id': sta[0],
                             'machine_state': sta[1],
                             'CstAvgTime': sta[2]}
            if sta[0] in amount.keys():
                state[sta[0]]['QcTolCnt'] = amount[sta[0]]
            else:
                state[sta[0]]['QcTolCnt'] = 0

        for machine in machine_list.keys():
            temp = {}
            temp['building'] = machine_list[machine]['building']
            temp['machine_name'] = machine_list[machine]['machine_name']
            temp['machine_state'] = state[machine_list[machine]['machine_conn_id']]['machine_state'] if state.get(
                machine_list[machine]['machine_conn_id']) else 0
            temp['QcTolCnt'] = state[machine_list[machine]['machine_conn_id']]['QcTolCnt'] if state.get(
                machine_list[machine]['machine_conn_id']) else 0
            temp['CstAvgTime'] = state[machine_list[machine]['machine_conn_id']]['CstAvgTime'] if state.get(
                machine_list[machine]['machine_conn_id']) else 0
            temp['machine_id'] = machine_list[machine]['machine_oracle_id']
            result.append(temp)
        res = {'result': result, 'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        # 排圖表順序
        chart_order = ['A18CXJB12', 'A18CXJB13', 'A18CXJB14', 'A18CXJB15', 'A18CXJB16', 'A18CXJB17', 'A18CXJB18',
                       'A18CXJB19']  # 排圖表順序
        compare = fun_compare_schedule_actual_chart(machine_list, now, today, amount, chart_order)

        toc(t, 'compare')
        res['compare_schedule_actual'] = [compare]  # 使用array作為前端圖表v-for指令預留
        emit('get_machine_state', res, broadcast=True)

