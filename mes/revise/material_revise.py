import json
from flask import (
    jsonify, render_template, request
)
from flask_principal import Permission, RoleNeed

from mes.revise import bp
from model import *
admin_permission = Permission(RoleNeed('super'))
user_permission = Permission(RoleNeed('user'))


@bp.route('/material_revise')
def material_revise():
    return render_template('main/revise/material_revise.html')


@bp.route("/ajax_revise_get_material", methods=['POST'])
def ajax_revise_get_material():
    data = request.get_data()
    data = json.loads(data)
    print(data)

    q_product = ProductList.query.filter(ProductList.product_name == data['product_name']).first()
    product_id = q_product.id

    q_bom = db_session \
        .query(Bom.pnlist_id, PNList.inj_product_name, PNList.part_number,
               PNMaterialList.material_id, PNMaterialList.material_weight,
               MaterialList.material_part_number, MaterialList.color, MaterialList.color_number,
               MaterialList.material_spec, MaterialList.material_type, MaterialList.material_vendor) \
        .join(PNList, Bom.pnlist_id == PNList.id)\
        .join(PNMaterialList, PNMaterialList.pnlist_id == Bom.pnlist_id)\
        .join(MaterialList, MaterialList.id == PNMaterialList.material_id) \
        .filter(Bom.product_id == product_id).all()
    bom_m_list = []
    for q in q_bom:
        temp = {}
        temp['pnlist_id'] = q[0]
        temp['inj_product_name'] = q[1]
        temp['part_number'] = q[2]
        temp['material_id'] = q[3]
        temp['material_weight'] = float(q[4])
        temp['material_part_number'] = q[5]
        temp['color'] = q[6]
        temp['color_number'] = q[7]
        temp['material_spec'] = q[8]
        temp['material_type'] = q[9]
        temp['material_vendor'] = q[10]
        bom_m_list.append(temp)
    return jsonify(bom_m_list)