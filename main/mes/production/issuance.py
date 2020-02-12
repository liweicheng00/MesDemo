import datetime
import json

from flask import (
    jsonify, render_template, request
)

from main.mes.production import bp
from main.model import *


@bp.route('/issuance')
def issuance():
    return render_template('main/production/issuance.html')


@bp.route("/ajax_latest_issuance", methods=['GET'])
def ajax_latest_issuance():
    # sql = """
    #             SELECT
    #                 issuance_record."date",
    #                 issuance_record.pnlist_id,
    #                 issuance_record.remain,
    #                 issuance_record.box_amount,
    #                 issuance_record.pallet,
    #                 issuance_record.total_amount,
    #                 issuance_record.responsible,
    #                     pn_list.part_number,
    #                     pn_list.inj_product_name,
    #                     product_list.product_name
    #             FROM
    #                 issuance_record
    #             inner join
    #                 (SELECT
    #                     MAX("date") AS mm, pnlist_id AS pn
    #                     FROM issuance_record
    #                     GROUP BY pnlist_id
    #                 ) a on ("date" = a.mm and issuance_record.pnlist_id = a.pn)
    #             inner join pn_list on pn_list.id = issuance_record.pnlist_id
    #             inner join bom on bom.pnlist_id = pn_list.id
    #             inner join product_list on product_list.id = bom.product_id
    #         """
    # todo: 午夜系統時間調整
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
    q_issuance = q.fetchall()
    result = []
    for issuance in q_issuance:
        # print(issuance)
        temp = {}
        temp['inj_product_name'] = issuance[5]
        temp['part_number'] = issuance[4]
        temp['pnlist_id'] = issuance[0]
        temp['remain'] = issuance[3]
        # temp['box_amount'] = issuance[3]
        # temp['pallet'] = issuance[4]
        # temp['total'] = issuance[5]
        # temp['responsible'] = issuance[6]
        result.append(temp)

    return jsonify(result)


@bp.route("/ajax_revise_issuance", methods=['POST'])
def ajax_revise_issuance():
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
        remain = float(dta['remain']) - float(total_amount)
        new_issuance = IssuanceRecord(date=date, pnlist_id=pnlist_id, remain=remain, box_amount=box_amount,
                                      pallet=pallet, total_amount=total_amount, responsible=responsible)
        db_session.add(new_issuance)
    db_session.commit()

    return jsonify()


@bp.route("/ajax_get_issuance", methods=['POST'])
def ajax_get_issuance():
    data = request.get_data()
    data = json.loads(data)
    # print(data)
    date = datetime.datetime.strptime(data['date'], "%Y-%m-%d")
    q_issuance = IssuanceRecord.query.filter(IssuanceRecord.date >= date,
                                             IssuanceRecord.date < date+datetime.timedelta(days=1))\
        .order_by(IssuanceRecord.pnlist_id, IssuanceRecord.date.desc()).all()

    result = []
    for issuance in q_issuance:
        temp = {}
        temp['id'] = issuance.id
        temp['date'] = issuance.date.strftime('%Y-%m-%d %H:%M:%S')
        temp['inj_product_name'] = issuance.pn_list.inj_product_name
        temp['part_number'] = issuance.pn_list.part_number
        temp['remain'] = issuance.remain
        temp['box_amount'] = issuance.box_amount
        temp['pallet'] = issuance.pallet
        temp['total'] = issuance.total_amount
        temp['responsible'] = issuance.responsible
        result.append(temp)
    return jsonify(result)


@bp.route("/ajax_get_init_issuance", methods=['GET'])
def ajax_get_init_issuance():
    # data = request.get_data()
    # data = json.loads(data)
    q_bom = Bom.query.all()
    q_issuance = IssuanceRecord.query.all()

    temp1 = []
    if q_issuance:
        for issuance in q_issuance:
            temp1.append(issuance.pnlist_id)
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


@bp.route("/ajax_add_issuance_part_number", methods=['POST'])
def ajax_add_issuance_part_number():

    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_pnlist = PNList.query.filter(PNList.part_number == data['part_number']).first()
    pnlist_id = q_pnlist.id
    date = datetime.datetime.strptime(data['date'], "%Y-%m-%d")
    new_issuance = IssuanceRecord(date=date, pnlist_id=pnlist_id,
                                  remain=float(data['amount']), total_amount=float(data['amount']))
    db_session.add(new_issuance)
    db_session.commit()
    return jsonify()
