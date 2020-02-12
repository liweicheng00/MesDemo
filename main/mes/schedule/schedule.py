import json

from flask import (
    jsonify, render_template, request
)
from flask_principal import Permission, RoleNeed

from main.mes.schedule import bp
from main.model import *

admin_permission = Permission(RoleNeed('super'))
user_permission = Permission(RoleNeed('user'))


@bp.route('/import_schedule')
def import_schedule():
    return render_template('main/schedule/schedule.html')


@bp.route('/revise_schedule')
def revise_schedule():
    return render_template('main/schedule/schedule_revise.html')


@bp.route("/ajax_product_list", methods=['GET'])
def ajax_product_list():
    # todo: 加入id，但會造成眾多網頁更改
    q_product = ProductList.query.all()
    result = {}
    for product in q_product:
        if not (product.product_code in result.keys()):
            result[product.product_code] = []
        result[product.product_code].append(product.product_name)
    return jsonify(result)


@bp.route("/ajax_machine_list", methods=['POST'])
def ajax_machine_list():
    data = request.get_data()
    data = json.loads(data)
    if 'building' in data.keys():
        building = data['building']
        q_machine = MachineList.query.filter(MachineList.building == building).all()
        result = {}
        for machine in q_machine:
            if not (machine.machine_tonnage in result.keys()):
                result[machine.machine_tonnage] = []
            # print(machine.machine_name)
            result[machine.machine_tonnage].append(machine.machine_name)
        return jsonify(result)
    elif 'part_number' in data.keys():
        part_number = data['part_number']
        return jsonify()
    else:
        return jsonify()


@bp.route("/ajax_bom_list", methods=['POST'])
def ajax_bom_list():
    data = request.get_data()
    data = json.loads(data)
    product_name = data['product_name']
    # print(product_name)
    q_product = ProductList.query.filter(ProductList.product_name == product_name).first()
    # print(q_product)
    q_bom = q_product.bom if (q_product is not None) else []
    result = {}
    for bom in q_bom:
        result[bom.pn_list.inj_product_name] = bom.pn_list.part_number

    return jsonify(result)


@bp.route("/ajax_mold_list", methods=['POST'])
def ajax_mold_list():
    data = request.get_data()
    data = json.loads(data)
    if 'part_number' in data.keys():
        part_number = data['part_number']
    else:
        return jsonify()
    # print(part_number)
    q_pnlist = PNList.query.filter(PNList.part_number == part_number).first()

    q_mold_pn = q_pnlist.mold_pn_association
    result = {}
    for mold in q_mold_pn:
        result[mold.mold_list.mold_number] = mold.mold_list.mold_number_f

    return jsonify(result)


@bp.route("/ajax_upload_schedule_test", methods=['POST'])
def ajax_upload_schedule_test():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    date = data['date']
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    part_number = data['part_number']
    q_pnlist = PNList.query.filter(PNList.part_number == part_number).first()
    pnlist_id = q_pnlist.id

    if 'produce_order' in data.keys():
        produce_order = data['produce_order']
    else:
        produce_order = ''

    product_name = data['inj_product_name']
    machine_code = data['resourceId']
    q_machine = MachineList.query.filter(MachineList.machine_code == machine_code).first()
    machine_id = q_machine.id

    if data['mold_number']:
        mold_number = data['mold_number']
        q_mold = MoldList.query.filter(MoldList.mold_number == mold_number).first()
        mold_id = q_mold.id
    else:
        if data['mold']:
            data['mold'] = data['mold'].upper()
            q_mold = db_session.query(MoldPnAssociation.mold_id)\
                .join(MoldList, MoldList.id == MoldPnAssociation.mold_id)\
                .filter(MoldPnAssociation.pnlist_id == pnlist_id, MoldList.mold_number_f == data['mold']).first()
            print('mold_id', q_mold[0])
            mold_id = q_mold[0]
        else:
            return jsonify({'state': 1, 'error': ['請輸入模具'],
                            'date': datetime.datetime.strftime(date, '%Y-%m-%d'),
                            'part_number': part_number})

    amount = float(data['amount'])
    error = []
    success = []

    q_schedule = ProduceSchedule.query.filter(ProduceSchedule.date == date,
                                              ProduceSchedule.mold_id == mold_id,
                                              ).first()
    if q_schedule is not None:
        error.append(data['mold'] + '模具已使用')
        schedule_id = q_schedule.id
        return jsonify({'state': 1, 'error': error, 'schedule_id': schedule_id,
                        'date': datetime.datetime.strftime(date, '%Y-%m-%d'),
                        'part_number': part_number})
    else:
        q_schedule = ProduceSchedule.query.filter(ProduceSchedule.date == date,
                                                  ProduceSchedule.machine_id == machine_id,
                                                  ).first()
        if q_schedule is not None:
            new_schedule = ProduceSchedule(date=date, pnlist_id=pnlist_id, produce_order=produce_order,
                                           machine_id=machine_id, product_name=product_name, mold_id=mold_id,
                                           amount=amount)

            q_back = BackendDemand.query.filter(BackendDemand.part_number == part_number,
                                                BackendDemand.date == date).first()
            if q_back:
                q_back.scheduled_num = q_back.scheduled_num + 1 if q_back.scheduled_num is not None else 1
                db_session.add(q_back)
            else:
                new_backend = BackendDemand(date=date,
                                            product_name=product_name,
                                            part_number=part_number,
                                            schedule_num=1)
                db_session.add(new_backend)
            db_session.add(new_schedule)
            db_session.commit()
            success.append(machine_code[-3:] + '計畫已新增，機台重複使用')
        else:
            new_schedule = ProduceSchedule(date=date, pnlist_id=pnlist_id, produce_order=produce_order,
                                           machine_id=machine_id, product_name=product_name, mold_id=mold_id,
                                           amount=amount)
            q_back = BackendDemand.query.filter(BackendDemand.part_number == part_number,
                                                BackendDemand.date == date).first()
            if q_back:
                q_back.scheduled_num = q_back.scheduled_num + 1 if q_back.scheduled_num is not None else 1
                db_session.add(q_back)
            else:
                new_backend = BackendDemand(date=date,
                                            product_name=product_name,
                                            part_number=part_number,
                                            scheduled_num=1)
                db_session.add(new_backend)
            db_session.add(new_schedule)
            db_session.commit()
            success.append(machine_code[-3:] + '計畫已新增')
        print(success)
        schedule_id = new_schedule.id
        return jsonify({'state': 0, 'success': success, 'schedule_id': schedule_id,
                        'date': datetime.datetime.strftime(date, '%Y-%m-%d'),
                        'part_number': part_number})


@bp.route("/ajax_upload_schedule", methods=['POST'])
def ajax_upload_schedule():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    date = data['date']
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    part_number = data['part_number']
    q_pnlist = PNList.query.filter(PNList.part_number == part_number).first()
    pnlist_id = q_pnlist.id

    if 'produce_order' in data.keys():
        produce_order = data['produce_order']
    else:
        produce_order = ''

    product_name = data['product']
    machine = data['machine']
    if not machine:
        return jsonify({'state': 1, 'error': ['no machine']})
    error = []
    success = []
    for mach in machine:
        print(mach)
        building = mach['building']
        machine_name = mach['machine']
        q_machine = MachineList.query.filter(MachineList.building == building,
                                             MachineList.machine_name == machine_name).first()
        machine_id = q_machine.id

        mold_number = mach['mold']
        q_mold = MoldList.query.filter(MoldList.mold_number == mold_number).first()
        mold_id = q_mold.id

        amount = float(mach['amount'])
        q_schedule = ProduceSchedule.query.filter(ProduceSchedule.date == date,
                                                  ProduceSchedule.mold_id == mold_id,
                                                  ).first()
        if q_schedule is not None:
            error.append(mold_number + '模具已使用')
        else:
            q_schedule = ProduceSchedule.query.filter(ProduceSchedule.date == date,
                                                      ProduceSchedule.machine_id == machine_id,
                                                      ).first()
            if q_schedule is not None:
                new_schedule = ProduceSchedule(date=date, pnlist_id=pnlist_id, produce_order=produce_order,
                                               machine_id=machine_id, product_name=product_name, mold_id=mold_id,
                                               amount=amount)
                db_session.add(new_schedule)
                db_session.commit()
                success.append(machine_name + '計畫已新增，機台重複使用')
            else:
                new_schedule = ProduceSchedule(date=date, pnlist_id=pnlist_id, produce_order=produce_order,
                                               machine_id=machine_id, product_name=product_name, mold_id=mold_id,
                                               amount=amount)
                db_session.add(new_schedule)
                db_session.commit()
                success.append(machine_name + '計畫已新增')

    if error:
        return jsonify({'state': 1, 'error': error})
    else:
        return jsonify({'state': 0, 'success': success})


@bp.route("/ajax_get_schedule", methods=['GET', 'POST'])
def ajax_get_schedule():
    if request.method == 'POST':
        data = request.get_data()
        data = json.loads(data)
        print(data)
        if 'date' in data.keys():
            date = datetime.datetime.strptime(data['date'], "%Y-%m-%d")
        else:
            date = datetime.date.today() + datetime.timedelta(days=-3)

        if 'product_name' in data.keys():
            product_name = data['product_name']
            q_schedule = ProduceSchedule.query.filter(ProduceSchedule.date >= date,
                                                      ProduceSchedule.product_name == product_name). \
                order_by(ProduceSchedule.date.desc(), ProduceSchedule.machine_id).all()
        else:
            q_schedule = ProduceSchedule.query.filter(ProduceSchedule.date == date). \
                order_by(ProduceSchedule.date.desc(), ProduceSchedule.machine_id).all()
        if 'inj_product_name' in data.keys():
            inj_product_name = data['inj_product_name']
        else:
            inj_product_name = ''
    else:
        inj_product_name = ''
        q_schedule = ProduceSchedule.query.filter(ProduceSchedule.date == datetime.date.today()). \
            order_by(ProduceSchedule.date.desc(), ProduceSchedule.machine_id).all()
    result = []

    for schedule in q_schedule:
        temp = {}
        temp['schedule_id'] = schedule.id
        temp['date'] = str(schedule.date)
        temp['product_name'] = schedule.product_name
        temp['machine'] = schedule.machine_list.machine_name
        temp['mold'] = schedule.mold_list.mold_number
        temp['part_number'] = schedule.pn_list.part_number
        temp['inj_product_name'] = schedule.pn_list.inj_product_name
        temp['amount'] = schedule.amount
        # temp['color'] = schedule.pn_list.pn_material_list.material_list.color
        if inj_product_name == '':
            result.append(temp)
        else:
            if temp['inj_product_name'] == inj_product_name:
                result.append(temp)
            else:
                pass
    return jsonify(result)


@bp.route("/ajax_delete_schedule_test", methods=['POST'])
def ajax_delete_schedule_test():
    data = request.get_data()
    data = json.loads(data)
    print(data)

    q_schedule = ProduceSchedule.query.filter(ProduceSchedule.id == data['id'][17:]).first()

    if q_schedule is not None:
        q_back = BackendDemand.query.filter(BackendDemand.part_number == data['part_number'],
                                            BackendDemand.date == datetime.datetime.strptime(data['date'], '%Y-%m-%d')).first()
        if q_back:
            if q_back.scheduled_num is None:
                q_back.scheduled_num = 0
            else:
                if q_back.scheduled_num - 1 < 0:
                    q_back.scheduled_num = 0
                else:
                    q_back.scheduled_num = q_back.scheduled_num - 1

            db_session.add(q_back)

        db_session.delete(q_schedule)
        db_session.commit()
    else:
        error = 'The schedule is not founded. schedule id: ' + str(data['id'][17:])
        return jsonify({'error': error})

    return jsonify()


@bp.route("/ajax_delete_schedule", methods=['POST'])
def ajax_delete_schedule():
    data = request.get_data()
    data = json.loads(data)
    # print(data)
    for re in data:
        # print(re)
        q_schedule = ProduceSchedule.query.filter(ProduceSchedule.id == (re['schedule_id'])).first()
        db_session.delete(q_schedule)
        db_session.commit()

    return jsonify()


@bp.route("/ajax_revise_schedule_test", methods=['POST'])
def ajax_revise_schedule_test():
    data = request.get_data()
    data = json.loads(data)
    error = None
    print(data)
    # todo: 字串操作驗證
    mold_number = data['props']['mold_number'][:8]
    # mold_number = data['props']['mold_number'].split('N')
    try:
        mold = int(data['mold'][1:])
        # mold = int(data['mold'].split("F"))

    except:
        error = '模具輸入錯誤，data["mold_id] = "' + data['mold']
        return jsonify({'error': error})
    else:
        q_mold = MoldList.query.filter(MoldList.mold_number == mold_number + 'N' + str(mold - 1)).first()
        if q_mold is None:
            error = mold_number + 'N' + str(mold - 1)
            print(error)
            return jsonify({'error': error})
    q_schedule = ProduceSchedule.query.filter(ProduceSchedule.id == data['props']['id'][17:]).first()
    if q_schedule is not None:
        if q_mold is None:
            error = '模具輸入錯誤'
            print(error)
        else:
            mold_id = q_mold.id
            q_schedule.mold_id = mold_id
            db_session.add(q_schedule)
            db_session.commit()
        q_schedule.amount = data['amount']

        db_session.add(q_schedule)
        db_session.commit()
    else:
        error = 'The schedule is not founded. schedule id: ' + str(data['props']['id'][17:])
        return jsonify({'error': error})
    return jsonify({'error': error, 'mold': q_mold.mold_number_f, 'mold_number': q_mold.mold_number})


@bp.route("/ajax_revise_schedule", methods=['POST'])
def ajax_revise_schedule():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    revised = data['revised']
    original = data['original']
    q_schedule = ProduceSchedule.query.filter(ProduceSchedule.id == original['schedule_id']).first()
    q_schedule.amount = revised['amount']
    db_session.add(q_schedule)
    db_session.commit()

    return jsonify()
