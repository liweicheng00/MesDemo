import json
from mes.revise import *
from model import *


@bp.route('/mold_revise')
def mold_revise():
    return render_template('main/revise/mold_revise.html')


@bp.route("/ajax_get_mold_pn", methods=['POST'])
def ajax_get_mold_pn():
    data = request.get_data()
    data = json.loads(data)
    print('ajax_get_mold_pn')
    print(data)
    result = []
    q_mold_pn = db_session.query(MoldPnAssociation, MoldList, PNList)\
        .join(MoldList, MoldList.id == MoldPnAssociation.mold_id)\
        .join(PNList, PNList.id == MoldPnAssociation.pnlist_id)\
        .filter(PNList.part_number == data['part_number']).order_by(MoldList.mold_number).all()
    for mold_pn, mold, pn in q_mold_pn:
        temp = {}
        temp['inj_product_name'] = pn.inj_product_name
        temp['part_number'] = pn.part_number
        temp['mold_number'] = mold.mold_number + ' ' + mold.mold_number_f
        temp['mold_number_f'] = mold.mold_number_f
        temp['cave_number'] = mold.cave_number
        temp['ejection_mode'] = mold.ejection_mode
        result.append(temp)
    return jsonify(result)
