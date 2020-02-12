import datetime
import json
import copy
from flask import (
    jsonify, render_template, request
)
from flask_login import current_user
from main.mes.revise import bp
from main.model import *


@bp.route("/ajax_building", methods=['GET'])
def ajax_building():
    q_building = BuildingList.query.all()
    result = []
    for q in q_building:
        temp = {}
        temp['id'] = q.id
        temp['building'] = q.building
        result.append(temp)
    return jsonify(result)


@bp.route("/ajax_machine", methods=['POST'])
def ajax_machine():
    data = request.get_data()
    data = json.loads(data)
    print(data)

    if 'building' in data.keys():
        building = data['building']
        q_machine = MachineList.query.filter(MachineList.building == building).all()
        result = {}
        for machine in q_machine:
            if not (machine.machine_tonnage in result.keys()):
                result[machine.machine_tonnage] = []
            result[machine.machine_tonnage].append({'machine_name': machine.machine_name,
                                                    'id:': machine.id,
                                                    'machine_code': machine.machine_code})
        return jsonify(result)
    else:
        return jsonify({'msg': 'No building in post data.'})


@bp.route("/ajax_product", methods=['GET'])
def ajax_product():
    q_product = ProductList.query.all()
    result = []
    for q in q_product:
        temp = {}
        temp['id'] = q.id
        temp['honhai_pn'] = q.honhai_pn
        temp['product_code'] = q.product_code
        temp['product_name'] = q.product_name
        result.append(temp)
    return jsonify(result)


@bp.route("/ajax_bom", methods=['POST'])
def ajax_bom():
    data = request.get_data()
    data = json.loads(data)
    print(data)

    if 'product' in data.keys():
        product = data['product']

        q_product = ProductList.query.filter(ProductList.product_name == product).first()
        q_bom = q_product.bom if (q_product is not None) else []
        result = {}
        for bom in q_bom:
            result[bom.pn_list.part_number] = {'inj_product_name': bom.pn_list.inj_product_name,
                                               'id': bom.pn_list.id}

        return jsonify(result)
    else:
        return jsonify({'msg': 'No product in post data.'})


@bp.route("/ajax_mold", methods=['POST'])
def ajax_mold():
    data = request.get_data()
    data = json.loads(data)
    if 'pnlist_id' in data.keys():
        pnlist_id = data['pnlist_id']
        q_mold_pn = MoldPnAssociation.query.filter(MoldPnAssociation.pnlist_id == pnlist_id).all()
        result = {}
        for mold in q_mold_pn:
            result[mold.mold_list.mold_number] = mold.mold_list.mold_number_f
        return jsonify(result)
    else:
        return jsonify({'msg': 'No pnlist_id in post data.'})


@bp.route("/ajax_bad", methods=['GET', 'POST'])
def ajax_bad():
    q_bad = BadList.query.all()
    bad_list = []
    for bad in q_bad:
        temp = {}
        temp['bad_name'] = bad.bad_name
        temp['bad_code'] = bad.bad_code
        bad_list.append(temp)

    return jsonify(bad_list)



