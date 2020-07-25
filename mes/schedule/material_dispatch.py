from flask import (
    jsonify, render_template, request
)
from flask_principal import Permission, RoleNeed

from mes.schedule import bp
from model import *
import json
import datetime

admin_permission = Permission(RoleNeed('super'))
user_permission = Permission(RoleNeed('user'))


@bp.route('/material_dispatch')
def material_dispatch():
    return render_template('main/schedule/material_dispatch.html')


@bp.route("/ajax_get_schedule_demand", methods=['POST'])
def ajax_get_schedule_demand():
    # todo:每日自動執行
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_sub0 = db_session.query(MachineList.id).filter(MachineList.building == data['building']).subquery()
    q_sub = db_session \
        .query(ProduceSchedule.pnlist_id,
               func.sum(ProduceSchedule.amount)) \
        .filter(ProduceSchedule.date == datetime.datetime.strptime(data['date'], '%Y-%m-%d'),
                ProduceSchedule.machine_id.in_(q_sub0)) \
        .group_by(ProduceSchedule.pnlist_id) \
        .order_by(ProduceSchedule.pnlist_id) \
        .subquery('t2')
    q_schedule = db_session.query(q_sub,
                                  PNList.part_number,
                                  PNList.inj_product_name,
                                  PNMaterialList.material_id,
                                  PNMaterialList.material_weight,
                                  MaterialList.material_part_number,
                                  MaterialList.color,
                                  MaterialList.material_spec,
                                  MaterialList.color_number) \
        .join(PNList, PNList.id == q_sub.c.pnlist_id) \
        .outerjoin(PNMaterialList, PNMaterialList.pnlist_id == PNList.id) \
        .join(MaterialList, MaterialList.id == PNMaterialList.material_id)
    result = []
    # todo: 相同原料相加
    for sch in q_schedule:
        temp = {}
        temp['date'] = data['date']
        temp['building'] = data['building']
        temp['pnlist_id'] = sch[0]
        temp['amount'] = float(sch[1])
        temp['part_number'] = sch[2]
        temp['inj_product_name'] = sch[3]
        temp['material_id'] = sch[4]
        temp['material_weight'] = float(sch[5])
        temp['material_part_number'] = sch[6]
        temp['color'] = sch[7]
        temp['material_spec'] = sch[8]
        temp['color_number'] = sch[9]
        temp['demand_weight'] = round(temp['amount'] * temp['material_weight'] / 1000, 0)

        # 剩餘原料
        # print(datetime.datetime.now().date() + datetime.timedelta(days=-1))
        q_m_check = MaterialCheck.query.filter(MaterialCheck.material_id == temp['material_id'],
                                               MaterialCheck.date ==
                                               datetime.datetime.now().date() + datetime.timedelta(days=-1)).first()
        if q_m_check is None:
            temp['remain_weight'] = "昨日無數據"
            temp['dispatch_weight'] = ''
            # temp['remain_weight'] = 50
            # temp['dispatch_weight'] = temp['demand_weight'] - temp['remain_weight']

        else:
            temp['remain_weight'] = q_m_check.total
            temp['dispatch_weight'] = temp['demand_weight'] - temp['remain_weight']
            if temp['dispatch_weight'] < 0:
                temp['dispatch_weight'] = 0

        q_m_dispatch = MaterialDispatch.query.filter(
            MaterialDispatch.date == datetime.datetime.strptime(data['date'], '%Y-%m-%d'),
            MaterialDispatch.material_id == temp['material_id'],
            MaterialDispatch.pnlist_id == temp['pnlist_id'],
            MaterialDispatch.building == data['building']).first()

        if q_m_dispatch:
            if q_m_dispatch.state == 1:
                temp['state'] = 2  # 不可發料，不可退回
            else:
                temp['state'] = 1  # 不可發料
                temp['dispatch_weight'] = q_m_dispatch.get_weight
        else:
            temp['state'] = 0   # 不可退回

        result.append(temp)
    return jsonify(result)


@bp.route("/ajax_upload_material_dispatch", methods=['POST'])
def ajax_upload_material_dispatch():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    if data['remain_weight'] == '昨日無數據':
        data['remain_weight'] = 0

    q_m_dispatch = MaterialDispatch.query.filter(
        MaterialDispatch.date == datetime.datetime.strptime(data['date'], '%Y-%m-%d'),
        MaterialDispatch.material_id == data['material_id'],
        MaterialDispatch.pnlist_id == data['pnlist_id'],
        MaterialDispatch.building == data['building']).first()
    if q_m_dispatch:
        q_m_dispatch.demand_weight = data['demand_weight']
        q_m_dispatch.remain_weight = data['remain_weight']
        q_m_dispatch.dispatch_weight = data['dispatch_weight']
        db_session.add(q_m_dispatch)
        db_session.commit()
        message = '更新'
    else:
        q_m_dispatch = MaterialDispatch(date=datetime.datetime.strptime(data['date'], '%Y-%m-%d'),
                                        material_id=data['material_id'],
                                        building=data['building'],
                                        pnlist_id=data['pnlist_id'],
                                        demand_weight=data['demand_weight'],
                                        remain_weight=data['remain_weight'],
                                        dispatch_weight=data['dispatch_weight'],
                                        get_weight=data['dispatch_weight'],
                                        state=0)
        db_session.add(q_m_dispatch)
        db_session.commit()
        message = '新增'

    return jsonify({'message': message})


@bp.route("/ajax_retreat_material_dispatch", methods=['POST'])
def ajax_retreat_material_dispatch():
    data = request.get_data()
    data = json.loads(data)
    print(data)

    q_m_dispatch = MaterialDispatch.query.filter(
        MaterialDispatch.date == datetime.datetime.strptime(data['date'], '%Y-%m-%d'),
        MaterialDispatch.material_id == data['material_id'],
        MaterialDispatch.pnlist_id == data['pnlist_id'],
        MaterialDispatch.building == data['building']).first()
    if q_m_dispatch:
        db_session.delete(q_m_dispatch)
        db_session.commit()
        message = '刪除'
    else:
        message = 'Something wrong!'

    return jsonify({'message': message})


@bp.route('/material_dispatch_confirm')
def material_dispatch_confirm():
    return render_template('main/schedule/material_dispatch_confirm.html')


@bp.route("/ajax_get_material_dispatch", methods=['POST'])
def ajax_get_material_dispatch():
    data = request.get_data()
    data = json.loads(data)
    print(data)

    q_m_dispatch = db_session.query(MaterialDispatch, MaterialList)\
        .filter(MaterialDispatch.date == datetime.datetime.strptime(data['date'], '%Y-%m-%d'),
                MaterialDispatch.building == data['building'])\
        .join(MaterialList, MaterialList.id == MaterialDispatch.material_id).all()

    result = []
    for m in q_m_dispatch:
        temp = {}
        temp['date'] = data['date']
        temp['building'] = data['building']
        temp['material_part_number'] = m[1].material_part_number
        temp['material_spec'] = m[1].material_spec
        temp['demand_weight'] = m[0].demand_weight
        temp['remain_weight'] = m[0].remain_weight
        temp['dispatch_weight'] = m[0].dispatch_weight
        temp['get_weight'] = m[0].get_weight
        temp['material_id'] = m[0].material_id
        temp['pnlist_id'] = m[0].pnlist_id
        temp['state'] = m[0].state
        result.append(temp)
    return jsonify(result)


@bp.route("/ajax_check_material_dispatch", methods=['POST'])
def ajax_check_material_dispatch():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_m_dispatch = MaterialDispatch.query.filter(
        MaterialDispatch.date == datetime.datetime.strptime(data['date'], '%Y-%m-%d'),
        MaterialDispatch.material_id == data['material_id'],
        MaterialDispatch.pnlist_id == data['pnlist_id'],
        MaterialDispatch.building == data['building']).first()
    if q_m_dispatch:
        q_m_dispatch.get_weight = data['get_weight']
        q_m_dispatch.state = 1
        db_session.add(q_m_dispatch)
        db_session.commit()
        message = '確認發料'
    else:
        message = 'something wrong'
    return jsonify({'message': message})


@bp.route("/ajax_cancel_material_dispatch", methods=['POST'])
def ajax_cancel_material_dispatch():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_m_dispatch = MaterialDispatch.query.filter(
        MaterialDispatch.date == datetime.datetime.strptime(data['date'], '%Y-%m-%d'),
        MaterialDispatch.material_id == data['material_id'],
        MaterialDispatch.pnlist_id == data['pnlist_id'],
        MaterialDispatch.building == data['building']).first()
    if q_m_dispatch:
        q_m_dispatch.state = 0
        db_session.add(q_m_dispatch)
        db_session.commit()
        message = '取消發料'
    else:
        message = 'something wrong'
    return jsonify({'message': message})


@bp.route('/material_check1')
def material_check1():
    return render_template('main/schedule/material_check.html')


@bp.route("/ajax_get_material_confirm", methods=['POST'])
def ajax_get_material_confirm():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_m_dispatch = MaterialDispatch.query.filter(
        MaterialDispatch.date == datetime.datetime.strptime(data['date'], '%Y-%m-%d'),
        MaterialDispatch.material_id == data['material_id'],
        MaterialDispatch.pnlist_id == data['pnlist_id'],
        MaterialDispatch.building == data['building']).first()
    if q_m_dispatch:
        q_m_dispatch.get_weight = data['get_weight']
        q_m_dispatch.state = 2
        db_session.add(q_m_dispatch)
        db_session.commit()
        message = '確認領料'
    else:
        message = 'something wrong'
    return jsonify({'message': message})


@bp.route("/ajax_cancel_material_confirm", methods=['POST'])
def ajax_cancel_material_confirm():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_m_dispatch = MaterialDispatch.query.filter(
        MaterialDispatch.date == datetime.datetime.strptime(data['date'], '%Y-%m-%d'),
        MaterialDispatch.material_id == data['material_id'],
        MaterialDispatch.pnlist_id == data['pnlist_id'],
        MaterialDispatch.building == data['building']).first()
    if q_m_dispatch:
        q_m_dispatch.get_weight = data['get_weight']
        q_m_dispatch.state = 1
        db_session.add(q_m_dispatch)
        db_session.commit()
        message = '取消領料'
    else:
        message = 'something wrong'
    return jsonify({'message': message})


@bp.route("/ajax_confirm_check_material", methods=['POST'])
def ajax_confirm_check_material():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_m_dispatch = MaterialDispatch.query.filter(
        MaterialDispatch.date == datetime.datetime.strptime(data['date'], '%Y-%m-%d'),
        MaterialDispatch.material_id == data['material_id'],
        MaterialDispatch.pnlist_id == data['pnlist_id'],
        MaterialDispatch.building == data['building']).first()
    if q_m_dispatch:
        q_m_dispatch.get_weight = data['get_weight']
        q_m_dispatch.state = 3
        db_session.add(q_m_dispatch)
        db_session.commit()
        message = '盤點確認'
    else:
        message = 'something wrong'
    return jsonify({'message': message})
