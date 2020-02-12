import json
from flask import (jsonify, render_template, request, redirect, url_for, session)
from flask_principal import Permission, RoleNeed
from main.mes.schedule import bp
from main.model import *

admin_permission = Permission(RoleNeed('super'))
user_permission = Permission(RoleNeed('user'))


@bp.route("/ajax_get_available_bom", methods=['POST'])
def ajax_get_available_bom():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_product = ProductList.query.filter(ProductList.product_name == data['product_name']).first()
    product_id = q_product.id

    q_bom = db_session\
        .query(Bom.pnlist_id, PNList.inj_product_name, PNList.part_number, PNList.product_name_en,
                             PNList.std_produce, PNList.std_cycle_time, PNList.piece)\
        .join(PNList, Bom.pnlist_id == PNList.id)\
        .filter(Bom.product_id == product_id, Bom.available.is_(None)).all()

    bom_list = []
    for bom in q_bom:
        print(bom)
        temp = {}
        temp['inj_product_name'] = bom[1]
        temp['part_number'] = bom[2]
        temp['product_name_en'] = bom[3]
        temp['std_produce'] = bom[4]
        temp['std_cycle_time'] = bom[5]
        temp['piece'] = bom[6]
        bom_list.append(temp)

    return jsonify(bom_list)


@bp.route('/demand_input', methods=['GET', 'POST'])
def demand_input():
    if request.method == 'POST':
        result = json.loads(request.form['result'])
        if 'store_backend_demand' in request.form.keys():
            fun_store_demand(session['datas'])        # 儲存需求
        session['datas'] = ''
        session['result'] = result
        return redirect(url_for('schedule.schedule_auto'))
    else:
        return render_template('main/schedule/backend_demand.html')


@bp.route("/ajax_get_store_open_num", methods=['POST'])
def ajax_get_store_open_num():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    date = []
    for key in data.keys():
        date.append(datetime.datetime.strptime(data[key], '%Y-%m-%d'))
    q_back = BackendDemand.query.filter(BackendDemand.date.in_(date)).all()
    result = {}
    if q_back:
        for back in q_back:
            back.date = back.date.strftime('%Y-%m-%d')
            if back.date in result:
                result[back.date][back.part_number] = {'open_num': back.open_num,
                                                       'revise_amount': back.revise_amount,
                                                       'revise_open_num': back.revise_open_num,
                                                       'scheduled_num': back.scheduled_num}
            else:
                result[back.date] = {}
                result[back.date][back.part_number] = {'open_num': back.open_num,
                                                       'revise_amount': back.revise_amount,
                                                       'revise_open_num': back.revise_open_num,
                                                       'scheduled_num': back.scheduled_num}
        return jsonify(result)
    else:
        return jsonify()


@bp.route("/ajax_demand_upload", methods=['POST'])
def ajax_demand_upload():
    data = request.get_data()
    data = json.loads(data)
    print(fun_print_json(data))

    session['datas'] = data
    print('儲存SESSION')
    print(session['datas'])

    result = fun_select_machine(data)
    # result = fun_select_machine(data, auto_suggestion)
    return result


@bp.route('/schedule_auto', methods=['GET', 'POST'])
def schedule_auto():
    return render_template('main/schedule/schedule_auto_v1.html')


@bp.route("/ajax_get_result", methods=['GET'])
def ajax_get_result():
    result = session['result']
    fun_print_json(result)
    schedule = []
    id = 0
    mold_set = set()
    for sch in result['auto']:
        temp = {}
        temp['title'] = sch['product_name'] + '-' + sch['select_machine']['mold'] + '-' + str(sch['amount_per_machine'])
        temp['start'] = sch['date']
        temp['allDay'] = 1
        temp['resourceId'] = sch['select_machine']['machine_code']
        temp['id'] = id
        q_mold = MoldList.query.filter(MoldList.id == sch['mold_id']).first()
        temp['extendedProps'] = {
            'inj_product_name': sch['product_name'],
            'part_number': sch['part_number'],
            'mold': sch['select_machine']['mold'],
            'mold_id': sch['select_machine']['mold_id'],
            'mold_number': q_mold.mold_number,
            'date': sch['date'],
            'amount': sch['amount_per_machine'],
            'id':  id,
            'resourceId': sch['select_machine']['machine_code'],
            'produce_order': sch['produce_order']
        }
        mold_set.add(sch['select_machine']['mold_id'])
        fun_print_json(temp)
        schedule.append(temp)
        id = id + 1

    manual = []
    id = 0
    for sch in result['manual']:
        temp = {}
        temp['title'] = sch['product_name'] + '-' + '?' + '-' + str(sch['amount_per_machine'])
        temp['start'] = sch['date']
        temp['allDay'] = 1
        temp['resourceId'] = ''
        temp['id'] = str(id) + 'm'
        temp['backgroundColor'] = '#d8004a'
        temp['borderColor'] = '#d8004a'
        temp['extendedProps'] = {
            'inj_product_name': sch['product_name'],
            'part_number': sch['part_number'],
            'mold': '',
            'mold_number': '',
            'date': sch['date'],
            'amount': sch['amount_per_machine'],
            'id': str(id) + 'm',
            'resourceId': '',
            'produce_order': sch['produce_order'],
            'mold_set': list(mold_set)
        }
        manual.append(temp)
        id = id+1
    return jsonify({'result': result, 'schedule': schedule, 'manual': manual})


def fun_store_demand(data):
    fun_print_json(data)
    for key in data:
        for d in data[key]['product_amount']:
            if data[key]['product_amount'][d]:
                for pn in data[key]['open_data'][d]:
                    q_backend = BackendDemand.query.filter(
                        BackendDemand.date == datetime.datetime.strptime(data[key]['dates'][d], "%Y-%m-%d"),
                        BackendDemand.part_number == pn).first()
                    if q_backend is not None:
                        q_backend.demand_amount = data[key]['open_data'][d][pn]['demand_amount']
                        q_backend.open_num = data[key]['open_data'][d][pn]['open_num']
                        q_backend.revise_amount = data[key]['open_data'][d][pn]['revise_amount']
                        q_backend.revise_open_num = data[key]['open_data'][d][pn]['revise_open_num']
                        q_backend.state = 0
                        db_session.add(q_backend)
                    else:
                        new_backend = BackendDemand(date=datetime.datetime.strptime(data[key]['dates'][d], "%Y-%m-%d"),
                                                    product_name=data[key]['open_data'][d][pn]['inj_product_name'],
                                                    part_number=pn,
                                                    demand_amount=data[key]['open_data'][d][pn]['demand_amount'],
                                                    open_num=data[key]['open_data'][d][pn]['open_num'],
                                                    revise_amount=data[key]['open_data'][d][pn]['revise_amount'],
                                                    revise_open_num=data[key]['open_data'][d][pn]['revise_open_num'],
                                                    state=0)
                        db_session.add(new_backend)
    db_session.commit()


def fun_select_machine(data):
    log = []
    schedule = {'auto': [], 'manual': []}
    for key in data:
        print(key)
        for d in data[key]['open_data']:
            machine_set = set()
            if d != "keys" and data[key]['open_data'][d]:
                for pn in data[key]['open_data'][d]:
                    if 'revise_open_num' in data[key]['open_data'][d][pn].keys():
                        if data[key]['open_data'][d][pn]['revise_open_num']:
                            revise_open_num = data[key]['open_data'][d][pn]['revise_open_num']
                            part_number = pn
                            pnlist_id = PNList.query.filter(PNList.part_number == part_number).first().id
                            date = data[key]['dates'][d]

                            machine_list = fun_get_used_machine_list(part_number)
                            # 自動選擇機台模具
                            select_machine = fun_auto_select_machine(
                                revise_open_num, machine_list, date, machine_set, data[key]['auto_suggestion'])

                            # 製作排產格式
                            """需要有 date, pnlist_id, produce_order, machine_id, product_name, mold_id, amount"""
                            for sel in select_machine:
                                temp = {}
                                temp['date'] = data[key]['dates'][d]
                                temp['pnlist_id'] = pnlist_id
                                temp['part_number'] = part_number
                                temp['produce_order'] = ''  # todo: 製作自動工令fun
                                temp['machine_id'] = sel['machine_id']
                                machine_set.add(sel['machine_id'])
                                temp['product_name'] = data[key]['open_data'][d][pn]['bom']['inj_product_name']
                                temp['mold_id'] = sel['mold_id']
                                temp['select_machine'] = sel
                                temp['amount'] = data[key]['open_data'][d][pn]['revise_amount']
                                temp['amount_per_machine'] = data[key]['open_data'][d][pn]['bom']['std_produce']
                                temp['code'] = '1'
                                temp['ps'] = '自動排產'
                                schedule['auto'].append(temp)

                            if revise_open_num <= len(select_machine):
                                pass
                            else:
                                # 製作手動排產
                                manual_sch_num = revise_open_num - len(select_machine)
                                temp = {}
                                temp['date'] = data[key]['dates'][d]
                                temp['pnlist_id'] = pnlist_id
                                temp['part_number'] = part_number
                                temp['produce_order'] = ''  # todo: 製作自動工令fun
                                temp['machine_id'] = ''
                                temp['product_name'] = data[key]['open_data'][d][pn]['bom']['inj_product_name']
                                temp['mold_id'] = ''
                                temp['select_machine'] = ''
                                temp['amount'] = data[key]['open_data'][d][pn]['revise_amount']
                                temp['amount_per_machine'] = data[key]['open_data'][d][pn]['bom']['std_produce']
                                temp['code'] = '2'
                                temp['ps'] = '手動排產'
                                for i in range(manual_sch_num):
                                    schedule['manual'].append(temp)
                        else:
                            log.append('pn can not be scheduled, '+str(pn))
            else:
                log.append('day is False or d = keys, ' + d)
    # fun_print_json(schedule)
    # fun_print_json(log)

    return jsonify({'error': log, 'auto_schedule': schedule, 'data': data})


def fun_auto_select_machine(revise_open_num, machine_list, date, machine_set, auto_suggestion=0):

    print('machine_list', len(machine_list))
    available_machine = fun_machine_list_check(machine_list, date)
    test_machine_list_check(available_machine)
    # 檢查機台是否已被排產
    for mach in available_machine[0:]:
        if mach['machine_id'] in machine_set:
            available_machine.remove(mach)

    if revise_open_num <= len(available_machine):
        select_machine = available_machine[:revise_open_num]

    else:
        if auto_suggestion:
            # todo: 隨機挑選機台模具，加標示
            print('revise_open_num > len(machine_list)')
            print('挑選', revise_open_num-len(available_machine), '台成型機')
            select_machine = available_machine
            pass
        else:
            select_machine = available_machine
    return select_machine


def fun_get_used_machine_list(part_number):
    machine_list = []
    try:
        subq_t2 = db_session.query(func.max(DailyReport.date).label('maxdate'),
                                   DailyReport.building,
                                   DailyReport.machine,
                                   DailyReport.mold) \
            .group_by(DailyReport.building, DailyReport.machine, DailyReport.mold) \
            .filter(DailyReport.part_number == part_number) \
            .order_by(func.max(DailyReport.date).desc()) \
            .subquery('t2')
        q_daily = db_session.query(subq_t2,
                                   MachineList.id,
                                   MachineList.machine_state,
                                   MachineList.machine_code,
                                   DailyReport.bad_ppm,
                                   DailyReport.produce_amount) \
            .join(DailyReport, and_(DailyReport.date == subq_t2.c.maxdate,
                                    DailyReport.building == subq_t2.c.building,
                                    DailyReport.machine == subq_t2.c.machine,
                                    DailyReport.mold == subq_t2.c.mold)) \
            .join(MachineList, and_(MachineList.building == subq_t2.c.building,
                                    MachineList.machine_name == subq_t2.c.machine)) \
            .order_by(subq_t2.c.maxdate.desc(), DailyReport.bad_ppm.asc()) \
            .all()
    except:
        return False
    else:
        pass
    for q in q_daily:
        q_mold = db_session.query(MoldPnAssociation.mold_id,
                                  MoldList.mold_number_f,
                                  MoldList.mold_state,
                                  MoldPnAssociation.pnlist_id,
                                  PNList.part_number) \
            .join(MoldList, MoldList.id == MoldPnAssociation.mold_id) \
            .join(PNList, PNList.id == MoldPnAssociation.pnlist_id) \
            .filter(PNList.part_number == part_number, MoldList.mold_number_f == q[3]) \
            .all()
        assert len(q_mold) == 1, '模具查詢異常'
        temp = {}
        temp['part_number'] = part_number
        temp['used_date'] = q[0]
        temp['building'] = q[1]
        temp['machine_name'] = q[2]
        temp['mold'] = q[3]
        temp['machine_id'] = q[4]
        temp['machine_state'] = q[5]
        temp['machine_code'] = q[6]
        temp['bad_ppm'] = q[7]
        temp['mold_id'] = q_mold[0][0]
        temp['mold_state'] = q_mold[0][2]
        temp['code'] = '0'
        temp['ps'] = '歷史模具'
        machine_list.append(temp)
    machine_set = set()
    for sel in machine_list[0:]:
        if sel['machine_name'] not in machine_set:
            machine_set.add(sel['machine_name'])
        else:
            machine_list.remove(sel)
            print('機台重複', sel['machine_name'])
            continue
    return machine_list


def fun_machine_list_check(machine_list, date):
    ng_mold = []
    mold_set = set()
    machine_set = set()
    if machine_list is None:
        return []

    for sel in machine_list[0:]:
        sel['date'] = date
        # step1:今日有無其他料號使用
        q_daily = ProduceSchedule.query.filter(
            ProduceSchedule.date == datetime.datetime.strptime(sel['date'], "%Y-%m-%d"),
            ProduceSchedule.machine_id == sel['machine_id']).first()
        if q_daily is not None:
            machine_list.remove(sel)
            mold_set.add(sel['mold_id'])
            print('機台已排產:', sel['machine_name'], sel['date'])
            continue

        q_daily = ProduceSchedule.query.filter(
            ProduceSchedule.date == datetime.datetime.strptime(sel['date'], "%Y-%m-%d"),
            ProduceSchedule.mold_id == sel['mold_id']).first()
        if q_daily is not None:
            machine_list.remove(sel)
            ng_mold.append(sel)
            mold_set.add(sel['mold_id'])
            print('模具已排產:', sel['machine_name'], sel['mold'], sel['date'])
            continue

        # step2:檢查有無重複
        if sel['machine_name'] not in machine_set:
            machine_set.add(sel['machine_name'])
            # step3:todo:檢查機台狀態
            if sel['machine_state']:
                pass
            else:
                # todo:機台異常無法使用
                # machine_list.remove(sel)
                pass
        else:
            machine_list.remove(sel)
            print('機台重複', sel['machine_name'], sel['date'])
            continue
        if sel['mold_id'] not in mold_set:
            mold_set.add(sel['mold_id'])
            # step3:todo:檢查模具狀態
            if sel['mold_state']:
                pass
            else:
                # todo:模具異常無法使用
                # machine_list.remove(sel)
                # ng_mold.append(sel)
                pass
        else:
            machine_list.remove(sel)
            ng_mold.append(sel)
            print('模具重複', sel['machine_name'], sel['mold'], sel['date'])
            continue

    # step4: 處理NG模具，重複的機檯後面再處裡
    print('ng_mold', len(ng_mold), '個')
    if ng_mold:
        for mold in ng_mold:
            print('模具重新選擇', mold['machine_name'], mold['mold'], mold['date'])
        q_pn = PNList.query.filter(PNList.part_number == ng_mold[0]['part_number']).first()
        q_mold_pn_association = q_pn.mold_pn_association
        print('q_mold', len(q_mold_pn_association))
        for sel in ng_mold:
            for mold_pn in q_mold_pn_association:
                print('mold_id', mold_pn.mold_id)
                if mold_pn.mold_id not in mold_set:
                    # todo:模具狀態
                    mold_set.add(mold_pn.mold_id)
                    sel['mold_id'] = mold_pn.mold_id
                    sel['mold'] = MoldList.query.filter(MoldList.id == mold_pn.mold_id).first().mold_number_f
                    break
            sel['ps'] = '自動選擇模具'
            sel['code'] = '1'
            machine_list.append(sel)
    return machine_list


def test_machine_list_check(machine_list):
    for mach in machine_list:
        # step1: 當日此機台、模具沒有使用
        q_daily = ProduceSchedule.query.filter(
            ProduceSchedule.date == datetime.datetime.strptime(mach['date'], "%Y-%m-%d"),
            ProduceSchedule.machine_id == mach['machine_id']).first()
        assert q_daily is None, '測試: 機台已使用  machine_id: ' + str(mach['machine_id'])
        q_daily = ProduceSchedule.query.filter(
            ProduceSchedule.date == datetime.datetime.strptime(mach['date'], "%Y-%m-%d"),
            ProduceSchedule.mold_id == mach['mold_id']).first()
        assert q_daily is None, '測試: 模具已使用  mold_id: ' + str(mach['mold_id'])

        # todo: step2: 檢查機台、模具無異常

    return True


def fun_print_json(data, tab=0):
    i = ''
    i = i.join(['  ' for e in range(tab)])
    tab = tab + 1
    if isinstance(data, dict):
        for key in data:
            if not isinstance(data[key], dict):
                print(i, key, ':', data[key])
            else:
                print(i, key, ':')
                fun_print_json(data[key], tab)
    elif isinstance(data, list):
        for a in data:
            fun_print_json(a, tab)
    else:
        print(i, data)
    return True
