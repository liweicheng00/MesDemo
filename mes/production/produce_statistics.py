import json

from mes.production import *
from model import *


@bp.route('/produce_statistics')
def produce_statistics():
    return render_template('main/production/produce_statistics.html')


@bp.route("/ajax_produce_statistics", methods=['POST'])
def ajax_produce_statistics():
    data = request.get_data()
    data = json.loads(data)
    print(data)

    q_daily = db_session.query(DailyReport.part_number, DailyReport.date, func.sum(DailyReport.produce_amount)) \
        .group_by(DailyReport.part_number, DailyReport.date).order_by(DailyReport.date).all()
    result = {}
    for pn, date, sum in q_daily:
        temp = {"date": date.strftime("%Y-%m-%d"), "sum": sum}
        if pn in result:
            result[pn].append(temp)
        else:
            result[pn] = [temp]

    q_pn = PNList.query.all()
    pn = {}
    for q in q_pn:
        pn[q.part_number] = q.inj_product_name
    result['pn'] = pn
    return jsonify(result)
