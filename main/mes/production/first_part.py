import datetime
import json
from flask import (
    jsonify, render_template, request,session
)
from flask_login import current_user
from main.mes.production import bp
from main.model import *


@bp.route('/first_part_init')
def first_part_init():
    return render_template('main/production/first_part_init.html')


@bp.route('/ajax_get_init_list', methods=['GET'])
def ajax_get_init_list():
    # 用session方式讀取棟別
    try:
        building = session['init_building']
        q_init = FirstPartRecord.query.filter(FirstPartRecord.building == building,
                                              or_(FirstPartRecord.dimension_state.is_(None),
                                                  FirstPartRecord.examine_state.is_(None)))\
            .order_by(FirstPartRecord.send_time.desc()).limit(100).all()
    except:
        q_init = FirstPartRecord.query.filter(or_(FirstPartRecord.dimension_state.is_(None),
                                                  FirstPartRecord.examine_state.is_(None)))\
            .order_by(FirstPartRecord.send_time.desc()).limit(100).all()
    result = []
    for init in q_init:
        temp = {}
        q_pn = PNList.query.filter(PNList.id == init.pnlist_id).first()
        temp['id'] = init.id
        temp['send_time'] = init.send_time.strftime('%Y-%m-%d %H:%M:%S')
        temp['part_number'] = init.part_number
        temp['inj_product_name'] = q_pn.inj_product_name
        temp['mold_number_f'] = init.mold_number_f
        temp['machine_name'] = init.machine_name
        temp['type'] = init.type
        temp['dimension_state'] = init.dimension_state
        temp['examine_state'] = init.examine_state
        result.append(temp)
    return jsonify(result)


@bp.route('/ajax_get_done_init_list', methods=['GET'])
def ajax_get_done_init_list():
    # 用session方式讀取棟別
    try:
        building = session['init_building']
        q_init = FirstPartRecord.query.filter(FirstPartRecord.building == building,
                                              FirstPartRecord.dimension_state == 1,
                                              FirstPartRecord.examine_state == 1)\
            .order_by(FirstPartRecord.send_time.desc()).limit(100).all()
    except:
        q_init = FirstPartRecord.query.filter(FirstPartRecord.dimension_state == 1,
                                              FirstPartRecord.examine_state == 1)\
            .order_by(FirstPartRecord.send_time.desc()).limit(100).all()
    result = []
    for init in q_init:
        temp = {}
        q_pn = PNList.query.filter(PNList.id == init.pnlist_id).first()
        temp['id'] = init.id
        temp['send_time'] = init.send_time.strftime('%Y-%m-%d %H:%M:%S')
        temp['part_number'] = init.part_number
        temp['inj_product_name'] = q_pn.inj_product_name
        temp['mold_number_f'] = init.mold_number_f
        temp['machine_name'] = init.machine_name
        temp['type'] = init.type
        temp['dimension_state'] = init.dimension_state
        temp['examine_state'] = init.examine_state
        result.append(temp)
    return jsonify(result)


@bp.route('/ajax_upload_init_list', methods=['POST'])
def ajax_upload_init_list():
    # 用session方式讀取棟別c
    data = request.get_data()
    data = json.loads(data)
    print(data)
    send_time = datetime.datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S')
    part_number = data['part_number']
    mold_number = data['mold']
    building = data['building']
    session['init_building'] = building
    machine_name = data['machine_name']
    init_type = data['init_type']

    q_pn = PNList.query.filter(PNList.part_number == part_number).first()
    q_mold = MoldList.query.filter(MoldList.mold_number == mold_number).first()
    q_machine = MachineList.query.filter(MachineList.building == building,
                                         MachineList.machine_name == machine_name).first()
    q_material = PNMaterialList.query.filter(PNMaterialList.pnlist_id == q_pn.id).all()

    if len(q_material) > 1:
        material_id = None
        material_part_number = None
    else:
        material_id = q_material[0].material_id
        q_m = MaterialList.query.filter(MaterialList.id == material_id).first()
        material_id = q_m.id
        material_part_number = q_m.material_part_number
    new_init_record = FirstPartRecord(send_time=send_time,
                                      pnlist_id=q_pn.id,
                                      part_number=part_number,
                                      building=building,
                                      machine_id=q_machine.id,
                                      machine_name=machine_name,
                                      mold_id=q_mold.id,
                                      mold_number=q_mold.mold_number,
                                      mold_number_f=q_mold.mold_number_f,
                                      material_id=material_id,
                                      material_part_number=material_part_number,
                                      type=init_type)
    db_session.add(new_init_record)
    db_session.commit()
    return jsonify()


@bp.route('/first_part_list')
def first_part_list():
    return render_template('main/production/first_part_list.html')


@bp.route('/first_part_record')
def first_part_record():
    pre_error = request.args.get('error')
    print('pre_error:', pre_error)
    return render_template('main/production/first_part_record.html')


@bp.route('/ajax_get_init_form', methods=['POST'])
def ajax_get_init_form():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_init = FirstPartRecord.query.filter(FirstPartRecord.id == data['id']).first()
    result = q_init.to_dict()
    return jsonify(result)


@bp.route('/ajax_get_dimension_detail', methods=['POST'])
def ajax_get_dimension_detail():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_mold = MoldList.query.filter(MoldList.mold_number == data['mold_number']).first()
    mold_id = q_mold.id
    q_pn = PNList.query.filter(PNList.part_number == data['part_number']).first()
    pnlist_id = q_pn.id

    cave_number = q_mold.cave_number
    mold_number = q_mold.mold_number
    mold_number_f = q_mold.mold_number_f
    q_material = PNMaterialList.query.filter(PNMaterialList.pnlist_id == pnlist_id).all()
    if len(q_material) > 1:
        pass
    else:
        material_id = q_material[0].material_id
        q_m = MaterialList.query.filter(MaterialList.id == material_id).first()
        material_part_number = q_m.material_part_number

    q_dimension = Dimension.query.filter(Dimension.pnlist_id == pnlist_id)\
        .order_by(Dimension.dim).all()
    if q_dimension:
        q_dim_record = DimensionRecord.query.filter(DimensionRecord.first_part_id == data['first_part_id']).all()
        dim_record = {}
        if q_dim_record:
            for dim_re in q_dim_record:
                if dim_re.dimension_id not in dim_record.keys():
                    dim_record[dim_re.dimension_id] = {}
                dim_record[dim_re.dimension_id][dim_re.cave_number] = dim_re.measure_data
            print(dim_record)
        dimension = []
        for dim in q_dimension:
            temp = {}
            temp['dimension_id'] = dim.id
            temp['DIM'] = 'DIM' + str(dim.dim)
            temp['dim_name'] = dim.dim_name
            temp['lower_limit'] = dim.lower_limit
            temp['upper_limit'] = dim.upper_limit
            temp['measure_tool'] = dim.measure_tool
            if dim_record:
                for key in dim_record[temp['dimension_id']].keys():
                    temp['cave-'+str(key)] = dim_record[temp['dimension_id']][key]
            dimension.append(temp)
    else:
        dimension = None

    q_examine = ExamineRecord.query.filter(ExamineRecord.first_part_id == data['first_part_id']).all()
    if q_examine:
        examine = []
        for exam in q_examine:
            temp = exam.to_dict()
            examine.append(temp)
    else:
        examine = None

    result = {}
    # result['pnlist_id'] = pnlist_id
    result['inj_product_name'] = q_pn.inj_product_name
    result['mold_id'] = mold_id
    result['mold_number'] = mold_number
    result['mold_number_f'] = mold_number_f
    result['cave_number'] = cave_number
    # result['material_part_number'] = material_part_number
    # result['material_id'] = material_id
    result['dimension'] = dimension
    result['examine'] = examine

    return jsonify(result)


@bp.route('/ajax_upload_record_data', methods=['POST'])
def ajax_upload_record_data():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_init = FirstPartRecord.query.filter(FirstPartRecord.id == data['first_part_id']).first()
    if 'batch_number' in data['data']:
        q_init.batch_number = data['batch_number']
    if 'examine_dependency' in data['data']:
        q_init.examine_dependency = data['examine_dependency']
    if 'grn_no' in data['data']:
        q_init.grn_no = data['grn_no']

    db_session.add(q_init)
    db_session.commit()

    return jsonify()


@bp.route('/ajax_upload_dimension_data', methods=['POST'])
def ajax_upload_dimension_data():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    # todo: 判定NG

    q_init = FirstPartRecord.query.filter(FirstPartRecord.id == data['first_part_id']).first()
    dimension_state = q_init.dimension_state

    if dimension_state:
        # todo: 更新
        msg = '數據更新'
        pass
    else:
        for key in data['data'].keys():
            temp = key.split("-")
            new_dim_record = DimensionRecord(cave_number=int(temp[1]),
                                             first_part_id=data['first_part_id'],
                                             dimension_id=int(temp[2]),
                                             measure_data=float(data['data'][key]) if data['data'][key] else None,
                                             determination=None,
                                             ng=0)
            db_session.add(new_dim_record)
        q_init.dimension_state = 1
        if q_init.examine_state == 1:
            q_init.finish_time = datetime.datetime.now()
        db_session.add(q_init)
        db_session.commit()
        msg = '數據新增'

    return jsonify({'msg': msg})


@bp.route('/ajax_upload_examine_data', methods=['POST'])
def ajax_upload_examine_data():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    # todo: 判定NG
    q_init = FirstPartRecord.query.filter(FirstPartRecord.id == data['first_part_id']).first()
    examine_state = q_init.examine_state

    if examine_state:
        pass    # todo: 更新
    else:
        for key in data['data'].keys():
            temp = key.split("-")
            new_exam_record = ExamineRecord(first_part_id=data['first_part_id'],
                                            cave_number=int(temp[1]))
            try:
                new_exam_record.examine_1 = data['data'][key]['EXAMINE_1']
                new_exam_record.examine_2 = data['data'][key]['EXAMINE_2']
                new_exam_record.examine_3 = data['data'][key]['EXAMINE_3']
                new_exam_record.examine_4 = data['data'][key]['EXAMINE_4']
                new_exam_record.examine_5 = data['data'][key]['EXAMINE_5']
                new_exam_record.examine_6 = data['data'][key]['EXAMINE_6']
                new_exam_record.examine_7 = data['data'][key]['EXAMINE_7']
                new_exam_record.examine_8 = data['data'][key]['EXAMINE_8']
                new_exam_record.examine_9 = data['data'][key]['EXAMINE_9']
                new_exam_record.examine_10 = data['data'][key]['EXAMINE_10']
                new_exam_record.examine_11 = data['data'][key]['EXAMINE_11']
                new_exam_record.examine_12 = data['data'][key]['EXAMINE_12']
                new_exam_record.examine_13 = data['data'][key]['EXAMINE_13']
                new_exam_record.examine_14 = data['data'][key]['EXAMINE_14']
                new_exam_record.examine_15 = data['data'][key]['EXAMINE_15']
                new_exam_record.examine_16 = data['data'][key]['EXAMINE_16']
                new_exam_record.examine_17 = data['data'][key]['EXAMINE_17']
                new_exam_record.examine_18 = data['data'][key]['EXAMINE_18']
                new_exam_record.examine_19 = data['data'][key]['EXAMINE_19']
            except:
                return jsonify({'error': '外觀檢查未完成'})
            else:
                db_session.add(new_exam_record)
        q_init.examine_state = 1
        if q_init.dimension_state == 1:
            q_init.finish_time = datetime.datetime.now()
        db_session.add(q_init)
        db_session.commit()
    return jsonify()


@bp.route('/ajax_add_dimension', methods=['POST'])
def ajax_add_dimension():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    pnlist_id = data['pnlist_id']
    mold_id = data['mold_id']
    q_dim = Dimension.query.filter(Dimension.pnlist_id == pnlist_id).all()
    if q_dim:
        pass    # todo: update
    else:
        for key in data['DIM'].keys():
            dim = int(key[3:])
            new_dim = Dimension(pnlist_id=pnlist_id,
                                dim=dim,
                                dim_name=data['DIM'][key]['dim_name'],
                                lower_limit=data['DIM'][key]['lower_limit'],
                                upper_limit=data['DIM'][key]['upper_limit'],
                                measure_tool=data['DIM'][key]['measure_tool'])
            db_session.add(new_dim)
        db_session.commit()

    return jsonify()
