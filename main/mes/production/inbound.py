import datetime
import json

from flask import (
    jsonify, render_template, request
)

from main.mes.production import bp
from main.model import *


@bp.route('/inbound')
def inbound():
    return render_template('main/production/inbound.html')


@bp.route("/ajax_latest_inbound", methods=['GET', 'POST'])
def ajax_latest_inbound():
    # todo:編輯按鈕新增料號
    # todo:結存報表
    # todo: 午夜系統時間調整
    if request.method == 'POST':
        data = request.get_data()
        data = json.loads(data)
        sql_1 = "where part_number in ('"
        for part in data['part_number']:
            sql_1 = sql_1 + part + ','
        sql_1 = sql_1 + "')"
    else:
        sql_1 = "where part_number in ('')"

    sql = """
            select 
                pn1 PN,
                inbound_amount inbound_amount,
                b.issuance_amount issuance_amount,
                inbound_amount-issuance_amount as total_amount,
                pn_list.part_number part_number,
                pn_list.inj_product_name,
                product_list.product_name
            from(
                SELECT sum(total_amount) AS inbound_amount, pnlist_id AS pn1
                FROM inbound_record
                where pnlist_id in (
                    select pnlist_id 
                    from produce_schedule 
                    where produce_schedule."date" = to_date(to_char(sysdate, 'yyyy-mm-dd'),'yyyy-mm-dd') 
                )
                or pnlist_id in (
                    select id 
                    from pn_list """ + sql_1 +\
    """
                )
                GROUP BY pnlist_id
                ) a
            inner join
                (SELECT
                    sum(total_amount) AS issuance_amount, pnlist_id AS pn2
                    FROM issuance_record
                    GROUP BY pnlist_id
                ) b on a.pn1 = b.pn2
            inner join pn_list on pn_list.id = a.pn1
            inner join bom on bom.pnlist_id = pn_list.id 
            inner join product_list on product_list.id = bom.product_id
    """
    q = db_session.execute(sql)
    # print(q)
    q_inbound = q.fetchall()
    result = []
    for inbound in q_inbound:
        print(inbound)
        temp = {}
        temp['inj_product_name'] = inbound[5]
        temp['part_number'] = inbound[4]
        temp['pnlist_id'] = inbound[0]
        temp['remain'] = inbound[3]
        # temp['box_amount'] = inbound[3]
        # temp['pallet'] = inbound[4]
        # temp['total'] = inbound[5]
        # temp['responsible'] = inbound[6]
        result.append(temp)

    return jsonify(result)


@bp.route("/ajax_revise_inbound", methods=['POST'])
def ajax_revise_inbound():
    data = request.get_data()
    data = json.loads(data)
    # print(data)

    for dta in data:
        print(dta)
        date = datetime.datetime.now()
        pnlist_id = dta['pnlist_id']

        box_amount = dta['box_amount']
        pallet = dta['pallet']
        total_amount = dta['total']
        responsible = dta['responsible']
        remain = float(dta['remain']) + float(total_amount)
        new_inbound = InboundRecord(date=date, pnlist_id=pnlist_id, remain=remain, box_amount=box_amount,
                                      pallet=pallet, total_amount=total_amount, responsible=responsible)
        db_session.add(new_inbound)
    db_session.commit()

    return jsonify()


@bp.route("/ajax_get_inbound", methods=['POST'])
def ajax_get_inbound():
    data = request.get_data()
    data = json.loads(data)
    # print(data)
    date = datetime.datetime.strptime(data['date'], "%Y-%m-%d")
    q_inbound = InboundRecord.query.filter(InboundRecord.date >= date,
                                             InboundRecord.date < date + datetime.timedelta(days=1)) \
        .order_by(InboundRecord.pnlist_id, InboundRecord.date.desc()).all()

    result = []
    for inbound in q_inbound:
        temp = {}
        temp['id'] = inbound.id
        temp['date'] = inbound.date.strftime('%Y-%m-%d %H:%M:%S')
        temp['inj_product_name'] = inbound.pn_list.inj_product_name
        temp['part_number'] = inbound.pn_list.part_number
        temp['remain'] = inbound.remain
        temp['box_amount'] = inbound.box_amount
        temp['pallet'] = inbound.pallet
        temp['total'] = inbound.total_amount
        temp['responsible'] = inbound.responsible
        result.append(temp)
    return jsonify(result)


@bp.route("/ajax_get_init_inbound", methods=['GET'])
def ajax_get_init_inbound():
    # data = request.get_data()
    # data = json.loads(data)
    q_bom = Bom.query.all()
    q_inbound = InboundRecord.query.all()

    temp1 = []
    if q_inbound:
        for inbound in q_inbound:
            temp1.append(inbound.pnlist_id)
        result = []
        for bom in q_bom:
            if bom.pnlist_id in temp1:
                pass
            else:
                temp3 = {}
                temp3['product_name'] = bom.product_list.product_name
                temp3['inj_product_name'] = bom.pn_list.inj_product_name
                temp3['part_number'] = bom.pn_list.part_number
                result.append(temp3)
        return jsonify(result)
    else:
        result = []
        for bom in q_bom:
            temp = {}
            temp['product_name'] = bom.product_list.product_name
            temp['inj_product_name'] = bom.pn_list.inj_product_name
            temp['part_number'] = bom.pn_list.part_number
            result.append(temp)
        return jsonify(result)
    return jsonify()


@bp.route("/ajax_add_inbound_part_number", methods=['POST'])
def ajax_add_inbound_part_number():

    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_pnlist = PNList.query.filter(PNList.part_number == data['part_number']).first()
    pnlist_id = q_pnlist.id
    date = datetime.datetime.strptime(data['date'], "%Y-%m-%d")
    new_inbound = InboundRecord(date=date, pnlist_id=pnlist_id,
                                remain=float(data['amount']), total_amount=float(data['amount']),
                                responsible='初始')
    new_issuance = IssuanceRecord(date=date, pnlist_id=pnlist_id,
                                  remain=0, total_amount=0, responsible='初始')
    db_session.add(new_issuance)
    db_session.add(new_inbound)
    db_session.commit()
    return jsonify()
