import datetime

from flask import (
    jsonify, render_template, request
)
from flask_principal import Permission, RoleNeed

from mes.production import *
# from model import *

admin_permission = Permission(RoleNeed('super'))
user_permission = Permission(RoleNeed('user'))


@bp.route('/material_check')
def material_check():
    return render_template('main/production/material_check.html')


@bp.route('/material_check_query')
def material_check_query():
    return render_template('main/production/material_check_query.html')


@bp.route("/ajax_get_material", methods=['GET'])
def ajax_get_material():
    q_material = MaterialList.query.all()
    result = {}
    for material in q_material:
        temp = {}
        temp['material_type'] = material.material_type
        temp['color'] = material.color
        temp['material_vendor'] = material.material_vendor

        result[material.material_part_number] = temp
    return jsonify(result)


@bp.route("/ajax_material_check_upload", methods=['POST'])
def ajax_material_check_upload():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    date = data['date']
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    building = data['building']
    material_part_number = data['material_part_number']
    get_amount = data['get_amount']
    feeding_bucket = data['feeding_zone']
    dry_bucket = data['dry_bucket']
    material_bucket = data['material_bucket']
    total = data['total']
    error = ''
    q_material = MaterialList.query.filter(MaterialList.material_part_number == material_part_number).first()
    material_id = q_material.id
    q_check = MaterialCheck.query.filter(MaterialCheck.date == date, MaterialCheck.building == building,
                                         MaterialCheck.material_id == material_id).first()
    if q_check is None:
        new_check = MaterialCheck(date=date, building=building, material_id=material_id, get_amount=get_amount,
                                  feeding_bucket=feeding_bucket, dry_bucket=dry_bucket, material_bucket=material_bucket,
                                  total=total)
        db_session.add(new_check)
        db_session.commit()
    else:
        error = '原料已輸入'
        return jsonify({'state': 1, 'error': error})

    return jsonify({'state': 0})


@bp.route("/ajax_material_check", methods=['POST'])
def ajax_material_check():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    date = data['date']
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    if 'building' in data.keys():
        if 'material_part_number' in data.keys():
            building = data['building']
            q_m = MaterialList.query.filter(MaterialList.material_part_number == data['material_part_number']).first()

            q_check = MaterialCheck.query.filter(MaterialCheck.building == building,
                                                 MaterialCheck.date == date,
                                                 MaterialCheck.material_id == q_m.id).all()
        else:
            building = data['building']
            q_check = MaterialCheck.query.filter(MaterialCheck.building == building, MaterialCheck.date == date).all()

    else:
        q_check = MaterialCheck.query.filter(MaterialCheck.date == date).all()

    result = []
    for check in q_check:
        temp = {}
        temp['date'] = check.date.strftime('%Y-%m-%d')
        temp['building'] = check.building
        temp['material_part_number'] = check.material_list.material_part_number
        temp['get_amount'] = check.get_amount
        temp['feeding_bucket'] = check.feeding_bucket
        temp['dry_bucket'] = check.dry_bucket
        temp['material_bucket'] = check.material_bucket
        temp['total'] = check.total
        result.append(temp)
    return jsonify(result)

# todo: 原料盤點在相同原料，不同料號會有問題
# todo: 早班晚班
