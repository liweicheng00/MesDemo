import json
from flask import (
    jsonify, render_template, request
)
from flask_principal import Permission, RoleNeed

from mes.revise import bp
from model import *
admin_permission = Permission(RoleNeed('super'))
user_permission = Permission(RoleNeed('user'))


@bp.route('/bom_revise')
def bom_revise():
    return render_template('main/revise/bom_revise.html')


@bp.route("/ajax_revise_get_bom", methods=['POST'])
def ajax_revise_get_bom():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_product = ProductList.query.filter(ProductList.product_name == data['product_name']).first()
    product_id = q_product.id

    q_bom = db_session\
        .query(Bom.pnlist_id, PNList.inj_product_name, PNList.part_number, PNList.product_name_en,
                             PNList.std_produce, PNList.std_cycle_time, PNList.piece, Bom.available)\
        .join(PNList, Bom.pnlist_id == PNList.id)\
        .filter(Bom.product_id == product_id).all()

    bom_list = []
    for bom in q_bom:
        temp = {}
        temp['inj_product_name'] = bom[1]
        temp['part_number'] = bom[2]
        temp['product_name_en'] = bom[3]
        temp['std_produce'] = bom[4]
        temp['std_cycle_time'] = bom[5]
        temp['piece'] = bom[6]
        temp['available'] = bom[7]
        bom_list.append(temp)

    return jsonify(bom_list)


@bp.route("/ajax_revise_bom", methods=['POST'])
def ajax_revise_bom():
    data = request.get_data()
    data = json.loads(data)
    print(data)

    revised = data['revised']
    original = data['original']
    q_pnlist = PNList.query.filter(PNList.part_number == original['part_number']).first()
    error = []
    if q_pnlist is None:
        error.append('數據異常')
        return jsonify({'state': 1, 'error': error})
        pass
    else:
        q_pnlist.std_cycle_time = revised['std_cycle_time']
        q_pnlist.std_produce = revised['std_produce']
        db_session.add(q_pnlist)
        db_session.commit()

    return jsonify({'state': 0, 'error': error})


@bp.route("/ajax_hide_bom", methods=['POST'])
def ajax_hide_bom():
    data = request.get_data()
    data = json.loads(data)
    part_number = []
    for part in data['data']:
        print(part['part_number'])
        part_number.append(part['part_number'])
    q_pn_id = db_session.query(PNList.id).filter(PNList.part_number.in_(part_number)).subquery()
    q_bom = Bom.query.filter(Bom.pnlist_id.in_(q_pn_id)).all()
    for bom in q_bom:
        print(bom.id, bom.available)
        bom.available = 'hide'
        db_session.add(bom)
    db_session.commit()
    return jsonify()


@bp.route("/ajax_show_bom", methods=['POST'])
def ajax_show_bom():
    data = request.get_data()
    data = json.loads(data)
    part_number = []
    for part in data['data']:
        print(part['part_number'])
        part_number.append(part['part_number'])
    q_pn_id = db_session.query(PNList.id).filter(PNList.part_number.in_(part_number)).subquery()
    q_bom = Bom.query.filter(Bom.pnlist_id.in_(q_pn_id)).all()
    for bom in q_bom:
        print(bom.id, bom.available)
        bom.available = None
        db_session.add(bom)
    db_session.commit()
    return jsonify()
