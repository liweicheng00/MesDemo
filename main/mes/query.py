import json
from flask import jsonify, request
from flask_login import login_required, current_user
from main.mes import *
from main.model import *
import datetime


'''把所有基礎選項功能放在這邊'''
@bp.route("/ajax_building", methods=['GET'])
@login_required
# @auth_manager
def ajax_building():
    print(request.args.get('warehouse'))
    if request.args.get('warehouse'):
        q_building = BuildingList.query\
            .filter(BuildingList.warehouse == 1, BuildingList.available == 1).all()
        result = []
        for q in q_building:
            temp = {}
            temp['id'] = q.id
            temp['building'] = q.building
            temp['warehouse'] = q.warehouse
            temp['available'] = q.available
            result.append(temp)
        return jsonify(result)
    q_building = BuildingList.query.all()
    result = []
    for q in q_building:
        temp = {}
        temp['id'] = q.id
        temp['building'] = q.building
        temp['warehouse'] = q.warehouse
        temp['available'] = q.available
        result.append(temp)
    return jsonify(result)


@bp.route("/ajax_position", methods=["POST"])
# @auth_manager
def ajax_position():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_position = db_session.query(MachineList.machine_location).filter(MachineList.building == data['building']).order_by(MachineList.machine_location).distinct()
    result = []
    for q in q_position:
        result.append(q[0])
    return jsonify(result)


@bp.route("/ajax_machine", methods=['POST'])
@login_required
# @auth_manager
def ajax_machine():
    data = request.get_data()
    data = json.loads(data)
    print(data)

    if 'building' in data.keys():
        building = data['building']
        q_machine = MachineList.query.filter(MachineList.building == building).order_by(MachineList.machine_name).all()
        result = {}
        for machine in q_machine:
            if not (machine.machine_tonnage in result.keys()):
                result[machine.machine_tonnage] = []
            result[machine.machine_tonnage].append({'machine_name': machine.machine_name,
                                                    'id': machine.id,
                                                    'machine_code': machine.machine_code,
                                                    'injection_number': machine.injection_number})
        return jsonify(result)
    elif 'part_number' in data.keys():
        return jsonify()
    elif 'machine_code' in data.keys():
        q_machine = MachineList.query.filter(MachineList.machine_code == data['machine_code']).first()
        return jsonify(q_machine.to_dict())
    elif 'machine_id' in data.keys():
        q_machine = MachineList.query.filter(MachineList.id == data['machine_id']).first()
        return jsonify(q_machine.to_dict())
    else:
        return jsonify({'msg': 'No building in post data.'}), 400


@bp.route("/ajax_machine_name", methods=['POST'])
@login_required
# @auth_manager
def ajax_machine_name():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q = MachineList.query.filter(MachineList.building == data['building']).order_by(MachineList.machine_name).all()
    result = []
    for m in q:
        if m.injection_number > 1:
            result.append(m.machine_name+'(1)')
            m.machine_name = m.machine_name+'(2)'
        if m.ms_id:
            m.machine_name = m.machine_name+'*'
        result.append(m.machine_name)
    return jsonify(result)


@bp.route("/ajax_product", methods=['GET'])
@login_required
# @auth_manager
def ajax_product():
    q_product = ProductList.query.all()
    result = {}
    for q in q_product:
        if q.product_code not in result.keys():
            result[q.product_code] = []
        result[q.product_code].append({
            'id': q.id,
            'honhai_pn': q.honhai_pn,
            'product_code': q.product_code,
            'product_name': q.product_name
        })

    return jsonify(result)


@bp.route("/ajax_class", methods=['GET'])
@login_required
# @auth_manager
def ajax_class():
    q_class = db_session.query(PNList.inj_product_class).distinct()
    result = {}
    for q in q_class:
        if q[0] is not None:
            result[q[0]] = ''
    return jsonify(result)


@bp.route("/ajax_mold", methods=['POST'])
@login_required
# @auth_manager
def ajax_mold():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    if 'pnlist_id' in data.keys():
        pnlist_id = data['pnlist_id']
        q_mold_pn = MoldPnAssociation.query.filter(MoldPnAssociation.pnlist_id == pnlist_id).all()
        result = {}
        for mold in q_mold_pn:
            result[mold.mold_list.mold_number] = mold.mold_list.mold_number_f
        return jsonify(result)
    if 'part_number' in data.keys():
        q_pnlist = PNList.query.filter(PNList.part_number == data['part_number']).first()

        q_mold_pn = q_pnlist.mold_pn_association
        result = {}
        for mold in q_mold_pn:
            result[mold.mold_list.mold_number] = mold.mold_list.mold_number_f

        return jsonify(result)

    q_mold = MoldList.query.order_by(MoldList.mold_number).all()
    result = {}
    for q in q_mold:

        mold_no = q.mold_number.split('N')[0]
        if mold_no in result:
            result[mold_no].append(q.to_dict())
        else:
            result[mold_no] = []
            result[mold_no].append(q.to_dict())
    return jsonify(result)


@bp.route("/ajax_bom", methods=['POST'])
@login_required
def ajax_bom():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    result = {}
    if 'product_name' in data.keys():
        product_name = data['product_name']
        q_product = ProductList.query.filter(ProductList.product_name == product_name).first()
        q_bom = q_product.bom if (q_product is not None) else []
        for bom in q_bom:
            result[bom.pn_list.part_number] = {'inj_product_name': bom.pn_list.inj_product_name,
                                               'part_number': bom.pn_list.part_number,
                                               'id': bom.pn_list.id,
                                               'product_name_en': bom.pn_list.product_name_en,
                                               'std_produce': bom.pn_list.std_produce,
                                               'std_cycle_time': bom.pn_list.std_cycle_time,
                                               'piece': bom.pn_list.piece,
                                               'available': bom.available,
                                               'ps': bom.pn_list.ps}
        return jsonify(result)
    elif 'inj_product_class' in data.keys():
        inj_product_class = data['inj_product_class']
        q_pnlist = PNList.query.filter(PNList.inj_product_class == inj_product_class).all()
        for bom in q_pnlist:
            result[bom.pn_list.part_number] = {'inj_product_name': bom.pn_list.inj_product_name,
                                               'part_number': bom.pn_list.part_number,
                                               'id': bom.pn_list.id,
                                               'product_name_en': bom.pn_list.product_name_en,
                                               'std_produce': bom.pn_list.std_produce,
                                               'std_cycle_time': bom.pn_list.std_cycle_time,
                                               'piece': bom.pn_list.piece,
                                               'inj_product_class': bom.pn_list.inj_product_class,
                                               'ps': bom.pn_list.ps,
                                               'produce_order_code': bom.pn_list.produce_order_code,
                                               'yield_rate': bom.pn_list.yield_rate}
        return jsonify(result)
    elif 'material_part_number' in data.keys():
        material_id = []
        for material in data['material_part_number']:
            q_material = MaterialList.query.filter(
                MaterialList.material_part_number == material).first()
            if q_material:
                material_id.append(q_material.id)

        q_m1 = db_session.query(PNMaterialList.pnlist_id).filter(PNMaterialList.material_id == material_id[0]).all()
        m1_set = set()
        for q in q_m1:
            m1_set.add(q[0])
        if len(material_id) >1:
            q_m2 = db_session.query(PNMaterialList.pnlist_id).filter(PNMaterialList.material_id == material_id[1]).all()
            m2_set = set()
            for q in q_m2:
                m2_set.add(q[0])

            pn_set = m1_set & m2_set
        else:
            pn_set = m1_set
        for pn in pn_set:
            q_pn = PNList.query.filter(PNList.id == pn).first()
            result[q_pn.part_number] = q_pn.to_dict()

        # q_material = MaterialList.query.filter(MaterialList.material_part_number == data['material_part_number']).first()
        # boms = q_material.pn_material_list
        # for bom in boms:
        #     result[bom.pn_list.part_number] = {'inj_product_name': bom.pn_list.inj_product_name,
        #                                        'part_number': bom.pn_list.part_number,
        #                                        'id': bom.pn_list.id,
        #                                        'product_name_en': bom.pn_list.product_name_en,
        #                                        'std_produce': bom.pn_list.std_produce,
        #                                        'std_cycle_time': bom.pn_list.std_cycle_time,
        #                                        'piece': bom.pn_list.piece,
        #                                        'inj_product_class': bom.pn_list.inj_product_class,
        #                                        'ps': bom.pn_list.ps,
        #                                        'produce_order_code': bom.pn_list.produce_order_code,
        #                                        'yield_rate': bom.pn_list.yield_rate}
        return jsonify(result)
    else:
        return jsonify({'msg': 'No product in post data.'}), 400


@bp.route("/ajax_bad", methods=['GET', 'POST'])
@login_required
def ajax_bad():
    q_bad = BadList.query.all()
    bad_list = []
    for bad in q_bad:
        temp = {}
        temp['bad_name'] = bad.bad_name
        temp['bad_code'] = bad.bad_code
        temp['id'] = bad.id
        bad_list.append(temp)

    return jsonify(bad_list)


@bp.route("/ajax_user", methods=['GET'])
@login_required
def ajax_user():
    user = {"username": current_user.username,
            "name": current_user.name}
    return jsonify(user)


@bp.route("/ajax_time", methods=['GET'])
@login_required
def ajax_time():
    work_class = ''
    time = datetime.datetime.now().time()
    A = datetime.time(7, 40, 0)
    B = datetime.time(11, 40, 0)
    C = datetime.time(15, 40, 0)
    D = datetime.time(19, 40, 0)
    E = datetime.time(23, 40, 0)
    F = datetime.time(3, 40, 0)
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
    midnight = datetime.time(0, 0, 0)
    if time.__ge__(A) and time.__lt__(D):
        day_time = '白班'
    else:
        day_time = '夜班'
    if time.__ge__(midnight) and time.__lt__(A):
        next_day = True
        system_day = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
    else:
        next_day = False
        system_day = datetime.datetime.now().strftime('%Y-%m-%d')

    result = {}
    result['work_class'] = work_class
    result['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result['next_day'] = next_day
    result['day_time'] = day_time
    result['system_day'] = system_day
    return jsonify(result)


@bp.route("/ajax_material", methods=['GET', 'POST'])
@login_required
def ajax_material():
    if request.method == 'GET':
        q_material = MaterialList.query.all()
        result = {}
        for material in q_material:
            result[material.material_part_number] = material.to_dict()
        return jsonify(result)
    else:
        data = request.get_data()
        data = json.loads(data)
        print(data)
        if 'material_part_number' in data:
            q_material = MaterialList.query.filter(MaterialList.material_part_number == data['material_part_number']).first()
            if q_material is not None:
                result = q_material.to_dict()
            else:
                result = None
            return jsonify(result)
        elif 'pnlist_id' in data:
            # todo: 雙色
            q_m = PNMaterialList.query.filter(PNMaterialList.pnlist_id == data['pnlist_id']).all()
            result =[]
            for q in q_m:
                result.append(q.material_list.to_dict())
            return jsonify(result)
        else:
            return jsonify({"msg": '沒有查詢條件'}), 400


@bp.route("/ajax_schedule", methods=['POST'])
@login_required
def ajax_schedule():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    machine_code = data['machine_code']
    q_machine = MachineList.query.filter(MachineList.machine_code == machine_code).first()
    system_day = data['system_day']
    q_schedule = ProduceSchedule.query.filter(ProduceSchedule.machine_id == q_machine.id,
                                              ProduceSchedule.system_day == datetime.datetime.strptime(system_day, "%Y-%m-%d")).all()
    result = []
    for sch in q_schedule:
        temp = {}
        temp['pnlist_id'] = sch.pn_list.id
        temp['part_number'] = sch.pn_list.part_number
        temp['inj_product_name'] = sch.pn_list.inj_product_name
        result.append(temp)
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


@bp.route("/ajax_anomaly_type_list", methods=['GET'])
def ajax_anomaly_type_list():
    q_anomaly_type = AnomalyTypeList.query.all()
    result = {}
    for types in q_anomaly_type:
        result[str(types.id)] = types.anomaly_type

    return jsonify(result)




