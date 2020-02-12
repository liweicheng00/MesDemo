from main.mes.schedule import *
from main.model import *
import json

@bp.route('/daily_report')
def daily_report():
    return render_template('main/schedule/daily_report.html')


@bp.route("/ajax_anomaly_detail", methods=['POST'])
def ajax_anomaly_detail():
    data = request.get_data()
    data = json.loads(data)

    daily_report_id = data['daily_report_id']
    q_anomaly = AnomalyRecord.query.filter(AnomalyRecord.daily_report_id == daily_report_id).all()
    result = []
    for anomaly in q_anomaly:
        temp = {}

        temp['lost_time'] = anomaly.lost_time
        temp['anomaly_name'] = anomaly.anomaly_list.anomaly_name
        temp['improve'] = anomaly.improve
        result.append(temp)
    return jsonify(result)


@bp.route("/ajax_daily_report_query", methods=['POST'])
def ajax_daily_report_query():
    data = request.get_data()
    data = json.loads(data)

    date = data['date']
    sql_2 = ''
    if 'product_name' in data.keys():
        product_name = data['product_name']
        sql_2 = sql_2 + " and product_list.product_name = '" + product_name + "'"
    if 'inj_product_name' in data.keys():
        inj_product_name = data['inj_product_name']
        sql_2 = sql_2 + " and inj_product_name = '" + inj_product_name + "'"
    if 'building' in data.keys():
        building = data['building']
        sql_2 = sql_2 + " and daily_report.building = '" + building + "'"
    sql = """
        SELECT
        daily_report."date" as date1,
        daily_report.machine as machine,
        daily_report.building as building,
            product_list.product_name as product_name, 
            pn_list.inj_product_name as inj_product_name,
        daily_report.part_number as part_number,
        daily_report.mold as mold,
        schedule.produce_order as produce_order,
        daily_report.lost_time as lost_time,
        schedule.amount as amount,
        daily_report.produce_amount as produce_amount,
        daily_report.bad_amount as bad_amount ,
        tableb.ac1 , tableb.ac2 , tableb.ac3 , tableb.ac4 , tableb.ac5 ,
        daily_report.id as id
        from daily_report
        inner join pn_list on pn_list.part_number = daily_report.part_number
        inner join bom on bom.pnlist_id = pn_list.id 
        inner join product_list on product_list.id = bom.product_id
        inner join machine_list on (
            machine_list.machine_name = daily_report.machine
            and machine_list.building = daily_report.building
            )
        left join (
            select
            produce_schedule."date" as date2, 
            produce_schedule.produce_order as produce_order, 
            produce_schedule.amount as amount, 
            produce_schedule.mold_id as mold_id, 
            produce_schedule.machine_id as machine_id,
            mold_list.mold_number_f as mold_f
            from produce_schedule
            inner join mold_list on mold_list.id = produce_schedule.mold_id
            ) schedule on (
            schedule.date2 = daily_report."date"
            and schedule.machine_id = machine_list.id
            and schedule.mold_f = daily_report.mold
            )
        left join (
            select
            id, lost_time, ac1, ac2, ac3, ac4, ac5 
            from(
                select
                daily_report.id as id,
                daily_report.lost_time as lost_time,
                sum (case when anomaly_list.anomaly_type_id = 1 then anomaly_record.lost_time
                     else NULL
                     END
                ) as ac1,
                sum (case when anomaly_list.anomaly_type_id = 2 then anomaly_record.lost_time
                     else NULL
                     END
                ) as ac2,
                sum (case when anomaly_list.anomaly_type_id = 3 then anomaly_record.lost_time
                     else NULL
                     END
                ) as ac3,
                sum (case when anomaly_list.anomaly_type_id = 4 then anomaly_record.lost_time
                     else NULL
                     END
                ) as ac4,
                sum (case when anomaly_list.anomaly_type_id = 5 then anomaly_record.lost_time
                     else NULL
                     END
                ) as ac5
                from daily_report
                inner join anomaly_record 
                on anomaly_record.daily_report_id = daily_report.id 
                inner join anomaly_list 
                on anomaly_record.anomaly_id = anomaly_list.id
                inner join anomaly_type_list 
                on anomaly_type_list.id = anomaly_list.anomaly_type_id 
                group by daily_report.id, daily_report.lost_time 
            )
        ) tableB on tableB.id = daily_report.id 
    """
    sql_1 = """where daily_report."date" = to_date('""" + date + """', 'yyyy-mm-dd') """

    sql = sql + sql_1 + sql_2 + " order by machine"

    q = db_session.execute(sql)

    result = q.fetchall()
    report_list = []
    for re in result:
        temp = {}

        temp['date'] = re[0].strftime('%Y-%m-%d')
        temp['machine'] = re[1]
        temp['building'] = re[2]
        temp['product_name'] = re[3]
        temp['inj_product_name'] = re[4]
        temp['part_number'] = re[5]
        temp['mold'] = re[6]
        temp['produce_order'] = re[7]
        temp['lost_time'] = re[8]
        temp['amount'] = re[9]
        temp['produce_amount'] = re[10]
        temp['bad_amount'] = re[11]
        fun = lambda a: float(a) if a is not None else None
        temp['AC1'] = fun(re[12])
        temp['AC2'] = fun(re[13])
        temp['AC3'] = fun(re[14])
        temp['AC4'] = fun(re[15])
        temp['AC5'] = fun(re[16])
        temp['daily_report_id'] = re[17]
        report_list.append(temp)

    return jsonify(report_list)


@admin_permission.require(http_exception=403)
@bp.route("/ajax_delete_daily_report", methods=['POST'])
def ajax_delete_daily_report():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    id = []
    for a in data['data']:
        print('刪除id:', a['daily_report_id'])
        id.append(a['daily_report_id'])
    id = tuple(id)
    q_bad = BadRecord.query.filter(BadRecord.daily_report_id.in_(id)).all()
    for bad in q_bad:
        print(bad)
        db_session.delete(bad)
    # db_session.commit()

    q_anomaly = AnomalyRecord.query.filter(AnomalyRecord.daily_report_id.in_(id)).all()
    for anomaly in q_anomaly:
        db_session.delete(anomaly)
    # db_session.commit()

    q_class = DailyClassReport.query.filter(DailyClassReport.daily_report_id.in_(id)).all()
    for d_class in q_class:
        db_session.delete(d_class)
    # db_session.commit()

    q_daily = DailyReport.query.filter(DailyReport.id.in_(id)).all()
    for daily in q_daily:
        db_session.delete(daily)
    db_session.commit()
    error = '刪除成功'
    return jsonify({'error': error})
