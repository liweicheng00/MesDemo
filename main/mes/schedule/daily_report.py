from main.mes.schedule import *
from main.model import *
import json
import datetime


@bp.route('/daily_report')
def daily_report():
    return render_template('main/schedule/daily_report_v2.html')


@bp.route("/ajax_anomaly_detail", methods=['POST'])
def ajax_anomaly_detail():
    data = request.get_data()
    data = json.loads(data)

    daily_report_id = data['daily_report_id']
    q_anomaly = AnomalyRecord.query.filter(AnomalyRecord.daily_report_id == daily_report_id).all()
    result = []
    for anomaly in q_anomaly:
        temp = {}
        temp['begin_time'] = anomaly.begin_time.strftime('%Y-%m-%d %H:%M:%S')
        if anomaly.anomaly_id:
            temp['anomaly_name'] = anomaly.anomaly_list.anomaly_name
        else:
            temp['anomaly_name'] = anomaly.tpm_repair_desc
        temp['lost_time'] = round(anomaly.lost_time, 2) if anomaly.lost_time is not None else None
        temp['improve'] = anomaly.improve
        temp['ps'] = anomaly.ps
        result.append(temp)
    return jsonify(result)


@bp.route("/ajax_daily_report_query", methods=['POST'])
def ajax_daily_report_query():
    data = request.get_data()
    data = json.loads(data)
    print('ajax_daily_report_query')
    print(data)
    date = data['date']
    q = db_session.query(DailyReport, PNList, ProduceSchedule) \
        .join(PNList, PNList.part_number == DailyReport.part_number) \
        .join(ProduceSchedule, and_(ProduceSchedule.date == DailyReport.date,
                                    ProduceSchedule.machine_id == DailyReport.machine_id,
                                    ProduceSchedule.mold_id == DailyReport.mold_id), isouter=True) \
        .filter(DailyReport.date == datetime.datetime.strptime(date, "%Y-%m-%d")) \
        .order_by(DailyReport.machine)

    if 'product_name' in data.keys() and data['product_name']:
        q = q.filter(ProductList.product_name == data['product_name'])
    if 'inj_product_name' in data.keys() and data['inj_product_name']:
        q = q.filter(PNList.inj_product_name == data['inj_product_name'])
    if 'building' in data.keys() and data['building']:
        q = q.filter(DailyReport.building == data['building'])
    q = q.all()



    report_list = []
    for daily, pn, schedule in q:
        temp = {}
        temp['daily_report_id'] = daily.id
        temp['date'] = daily.date.strftime('%Y-%m-%d')
        temp['machine'] = daily.machine
        temp['machine_id'] = daily.machine_id
        temp['building'] = daily.building
        temp['part_number'] = daily.part_number
        temp['mold'] = daily.mold
        temp['mold_id'] = daily.mold_id
        temp['lost_time'] = daily.lost_time
        temp['produce_amount'] = daily.produce_amount
        temp['bad_amount'] = daily.bad_amount

        temp['inj_product_name'] = pn.inj_product_name
        # temp['product_name'] = product.product_name
        temp['amount'] = schedule.amount if schedule is not None else ''
        temp['produce_order'] = schedule.produce_order if schedule is not None else ''

        q_anomaly = AnomalyRecord.query.filter(AnomalyRecord.daily_report_id == daily.id).all()
        temp['lost_time'] = 0
        for ano in q_anomaly:
            temp['lost_time'] = temp['lost_time'] + (ano.lost_time or 0)
        temp['lost_time'] = round(temp['lost_time'], 3)

        report_list.append(temp)

    return jsonify(report_list)


@bp.route("/ajax_delete_daily_report", methods=['POST'])
def ajax_delete_daily_report():
    data = request.get_data()
    data = json.loads(data)
    print('ajax_delete_daily_report')
    print(data)
    id = []
    id.append(data['daily_report_id'])
    id = tuple(id)
    q_bad = BadRecord.query.filter(BadRecord.daily_report_id.in_(id)).all()
    for bad in q_bad:
        db_session.delete(bad)

    q_anomaly = AnomalyRecord.query.filter(AnomalyRecord.daily_report_id.in_(id)).all()
    for anomaly in q_anomaly:
        db_session.delete(anomaly)

    q_daily = DailyReport.query.filter(DailyReport.id.in_(id)).all()
    for daily in q_daily:
        db_session.delete(daily)
    db_session.commit()
    error = '刪除成功'
    return jsonify({'error': error})


