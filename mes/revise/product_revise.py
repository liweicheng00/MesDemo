import json
from flask import (
    jsonify, render_template, request
)
from flask_principal import Permission, RoleNeed

from mes.revise import bp
from model import *
admin_permission = Permission(RoleNeed('super'))
user_permission = Permission(RoleNeed('user'))


@bp.route('/product_revise')
def product_revise():
    return render_template('main/revise/product_revise.html')


@bp.route("/ajax_revise_get_product", methods=['GET'])
def ajax_revise_get_product():

    q_product = ProductList.query.all()

    product_list = []
    for product in q_product:
        temp = {}
        temp['honhai_pn'] = product.honhai_pn
        temp['product_name'] = product.product_name
        temp['product_code'] = product.product_code

        product_list.append(temp)

    return jsonify(product_list)


@bp.route("/ajax_revise_product", methods=['POST'])
def ajax_revise_product():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    revised = data['revised']
    original = data['original']
    q_product = ProductList.query.filter(ProductList.product_name == original['product_name'],
                                         ProductList.product_code == original['product_code'],
                                         ProductList.honhai_pn == original['honhai_pn']).first()
    error = []
    if q_product is None:
        error.append('數據異常')
        return jsonify({'state': 1, 'error': error})
        pass
    else:
        try:
            q_product.product_name = revised['product_name']
            q_product.product_code = revised['product_code']
            q_product.honhai_pn = revised['honhai_pn']
            db_session.add(q_product)
            db_session.commit()
        except:
            error = '不可重複'
        else:
            pass

    return jsonify({'state': 0, 'error': error})
