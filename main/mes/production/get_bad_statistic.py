import datetime
import json
import copy
from flask import (
    jsonify, render_template, request
)
from flask_login import current_user
from main.mes.production import bp
from main.model import *


@bp.route('/bad_report_query')
def bad_report_query():
    return render_template('main/production/bad_record_query.html')


@bp.route('/bad_report_progress_query')
def bad_report_progress_query():
    return render_template('main/production/bad_record_progress_query.1.html')


@bp.route('/ajax_bad_query', methods=['GET', 'POST'])
def ajax_bad_query():
    data = request.get_data()
    data = json.loads(data)
    return jsonify(fun_bad_query(data))


def fun_bad_query(data):
    keys = list(data.keys())
    for key in keys:
        if data[key] == '':
            data.pop(key)
    print(data)
    query_bool = [data['query_bool']['machine_bool'], data['query_bool']['mold_bool']]
    if 'time_range' in data.keys():
        time_range = data['time_range']
        begin_time = time_range[0:10]
        end_time = time_range[13:]
    else:
        # begin_time = datetime.date.today() + datetime.timedelta(days=-1)
        begin_time = datetime.date.today()
        end_time = datetime.date.today()
        begin_time = str(begin_time)
        end_time = str(end_time)
    if query_bool == [0, 0]:
        sql = """
                SELECT
                    a.*,
                    pn_list.inj_product_name AS inj_product_name,
                    product_list.product_name as product_name 
                FROM(
                        SELECT
                            part_number,
                            SUM(produce_amount) AS total_amount,
                            SUM(bad_amount) AS total_bad,
                            SUM(lost_time) AS total_lost_time
                        FROM
                            daily_report
                        WHERE
                            "date" >=  to_date('""" + begin_time + """', 'yyyy-mm-dd') and
                            "date" <=  to_date('""" + end_time + """', 'yyyy-mm-dd')
                        GROUP BY
                            part_number
                    ) a
                INNER JOIN pn_list ON pn_list.part_number = a.part_number
                INNER JOIN bom on pn_list.id = bom.pnlist_id
                inner JOIN product_list on product_list.id = bom.product_id
            """
        sql_filter = ''
        if 'product_name' in data.keys():
            if not sql_filter:
                sql_filter = " where product_name = '" + data['product_name'] + "'"
            else:
                sql_filter = sql_filter + " and product_name = '" + data['product_name'] + "'"
        if 'inj_product_name' in data.keys():
            if not sql_filter:
                sql_filter = " where inj_product_name = '" + data['inj_product_name'] + "'"
            else:
                sql_filter = sql_filter + " and inj_product_name = '" + data['inj_product_name'] + "'"
        else:
            sql_filter = sql_filter + ''
        sql = sql + sql_filter
        q_report = db_session.execute(sql)
        return fun_q_report([0, 0], q_report, begin_time, end_time)
    elif query_bool == [1, 0]:
        sql = """
            SELECT
                a.*,
                pn_list.inj_product_name AS inj_product_name,
                product_list.product_name as product_name 
            FROM(
                    SELECT
                        part_number,
                        SUM(produce_amount) AS total_amount,
                        SUM(bad_amount) AS total_bad,
                        SUM(lost_time) AS total_lost_time,
                        machine
                    FROM
                        daily_report
                    WHERE
                        "date" >=  to_date('""" + begin_time + """', 'yyyy-mm-dd') and
                        "date" <=  to_date('""" + end_time + """', 'yyyy-mm-dd')
                    GROUP BY
                        part_number,
                        machine
                    order by machine
                ) a
            INNER JOIN pn_list ON pn_list.part_number = a.part_number
            INNER JOIN bom on pn_list.id = bom.pnlist_id
            inner JOIN product_list on product_list.id = bom.product_id
        """
        sql_filter = ''
        if 'product_name' in data.keys():
            if not sql_filter:
                sql_filter = " where product_name = '" + data['product_name'] + "'"
            else:
                sql_filter = sql_filter + " and product_name = '" + data['product_name'] + "'"
        if 'inj_product_name' in data.keys():
            if not sql_filter:
                sql_filter = " where inj_product_name = '" + data['inj_product_name'] + "'"
            else:
                sql_filter = sql_filter + " and inj_product_name = '" + data['inj_product_name'] + "'"
        if 'machine' in data.keys():
            if not sql_filter:
                sql_filter = " where machine = '" + data['machine'] + "'"
            else:
                sql_filter = sql_filter + " and machine = '" + data['machine'] + "'"
        sql = sql + sql_filter
        q_report = db_session.execute(sql)
        return fun_q_report([1, 0], q_report, begin_time, end_time)
    elif query_bool == [0, 1]:
        sql = """
            SELECT
                a.*,
                pn_list.inj_product_name AS inj_product_name,
                product_list.product_name as product_name 
            FROM(
                    SELECT
                        part_number,
                        SUM(produce_amount) AS total_amount,
                        SUM(bad_amount) AS total_bad,
                        SUM(lost_time) AS total_lost_time,
                        mold
                    FROM
                        daily_report
                    WHERE
                        "date" >=  to_date('""" + begin_time + """', 'yyyy-mm-dd') and
                        "date" <=  to_date('""" + end_time + """', 'yyyy-mm-dd')
                    GROUP BY
                        part_number,
                        mold
                    order by mold
                ) a
            INNER JOIN pn_list ON pn_list.part_number = a.part_number
            INNER JOIN bom on pn_list.id = bom.pnlist_id
            inner JOIN product_list on product_list.id = bom.product_id
        """
        sql_filter = ''
        if 'product_name' in data.keys():
            if not sql_filter:
                sql_filter = " where product_name = '" + data['product_name'] + "'"
            else:
                sql_filter = sql_filter + " and product_name = '" + data['product_name'] + "'"
        if 'inj_product_name' in data.keys():
            if not sql_filter:
                sql_filter = " where inj_product_name = '" + data['inj_product_name'] + "'"
            else:
                sql_filter = sql_filter + " and inj_product_name = '" + data['inj_product_name'] + "'"
        if 'mold' in data.keys():
            if not sql_filter:
                sql_filter = " where mold = '" + data['mold'] + "'"
            else:
                sql_filter = sql_filter + " and mold = '" + data['mold'] + "'"
        sql = sql + sql_filter
        q_report = db_session.execute(sql)
        return fun_q_report([0, 1], q_report, begin_time, end_time)
    elif query_bool == [1, 1]:
        sql = """
            SELECT
                a.*,
                pn_list.inj_product_name AS inj_product_name,
                product_list.product_name as product_name 
            FROM(
                    SELECT
                        part_number,
                        SUM(produce_amount) AS total_amount,
                        SUM(bad_amount) AS total_bad,
                        SUM(lost_time) AS total_lost_time,
                        machine,
                        mold
                    FROM
                        daily_report
                    WHERE
                        "date" >=  to_date('""" + begin_time + """', 'yyyy-mm-dd') and
                        "date" <=  to_date('""" + end_time + """', 'yyyy-mm-dd')
                    GROUP BY
                        part_number,
                        machine,
                        mold
                    order by machine
                ) a
            INNER JOIN pn_list ON pn_list.part_number = a.part_number
            INNER JOIN bom on pn_list.id = bom.pnlist_id
            inner JOIN product_list on product_list.id = bom.product_id
        """
        sql_filter = ''
        if 'product_name' in data.keys():
            if not sql_filter:
                sql_filter = " where product_name = '" + data['product_name'] + "'"
            else:
                sql_filter = sql_filter + " and product_name = '" + data['product_name'] + "'"
        if 'inj_product_name' in data.keys():
            if not sql_filter:
                sql_filter = " where inj_product_name = '" + data['inj_product_name'] + "'"
            else:
                sql_filter = sql_filter + " and inj_product_name = '" + data['inj_product_name'] + "'"
        if 'machine' in data.keys():
            if not sql_filter:
                sql_filter = " where machine = '" + data['machine'] + "'"
            else:
                sql_filter = sql_filter + " and machine = '" + data['machine'] + "'"
        if 'mold' in data.keys():
            if not sql_filter:
                sql_filter = " where mold = '" + data['mold'] + "'"
            else:
                sql_filter = sql_filter + " and mold = '" + data['mold'] + "'"
        sql = sql + sql_filter
        q_report = db_session.execute(sql)
        return fun_q_report([1, 1], q_report, begin_time, end_time)
    else:
        print('something wrong')
    return jsonify()


def fun_q_report(q_type, q_report, begin_time, end_time):
    result = []
    if q_report is None:
        return {}
    num = 0

    for report in q_report:
        print(report)
        temp = {}
        temp['key'] = str(num)
        temp['part_number'] = report[0]
        temp['total_amount'] = float(report[1]) if (report[1]) else None
        temp['total_bad'] = float(report[2]) if (report[2]) else None
        temp['total_lost_time'] = float(report[3]) if (report[3]) else None
        temp['machine'] = report[4] if (q_type == [1, 0] or q_type == [1, 1]) else None
        if q_type == [0, 1]:
            temp['mold'] = report[4]
        elif q_type == [1, 1]:
            temp['mold'] = report[5]
        else:
            temp['mold'] = None

        if q_type == [0, 0]:
            temp['inj_product_name'], temp['product_name'] = [report[4], report[5]]
        elif q_type == [1, 1]:
            temp['inj_product_name'], temp['product_name'] = [report[6], report[7]]
        elif q_type == [1, 0] or q_type == [0, 1]:
            temp['inj_product_name'], temp['product_name'] = [report[5], report[6]]
        else:
            print('something wrong')

        sql_filter = "daily_report.part_number = '" + temp['part_number'] + "' and "
        if temp['machine'] is not None:
            sql_filter = sql_filter + "daily_report.machine = '" + temp['machine'] + "' and "
        if temp['mold'] is not None:
            sql_filter = sql_filter + "daily_report.mold = '" + temp['mold'] + "' and "

        # sql = """
        #     select
        #         bad_amount,
        #         bad_list.bad_name
        #     from(select
        #                 bad_id,
        #                 COUNT(bad_id) as bad_amount
        #             from bad_record
        #             where daily_report_id in (
        #                 SELECT
        #                     id
        #                 FROM
        #                     (SELECT
        #                         daily_report.id,
        #                         daily_report.part_number,
        #                         pn_list.inj_product_name AS inj_product_name,
        #                         product_list.product_name as product_name
        #                     FROM
        #                         daily_report
        #                     INNER JOIN pn_list ON pn_list.part_number = daily_report.part_number
        #                     INNER JOIN bom on pn_list.id = bom.pnlist_id
        #                     inner JOIN product_list on product_list.id = bom.product_id
        #                     where (""" + sql_filter + """
        #                           "date" >=  to_date('""" + begin_time + """', 'yyyy-mm-dd') and
        #                           "date" <=  to_date('""" + end_time + """', 'yyyy-mm-dd')))
        #                 )
        #             GROUP BY bad_id)
        #     right join bad_list on bad_list.id=bad_id
        #     order by bad_list.id
        # """
        sql = """
                select
                    bad_amount,
                    bad_list.bad_name
                from(
                    select
                        bad_id,
                        COUNT(bad_id) as bad_amount
                    from bad_record
                    where daily_report_id in (
                        SELECT
                            idarray.id
                        FROM (
                            SELECT
                                daily_report.id as id,
                                daily_report.part_number,
                                pn_list.inj_product_name AS inj_product_name,
                                product_list.product_name as product_name 
                            FROM 
                                daily_report
                            INNER JOIN pn_list ON pn_list.part_number = daily_report.part_number
                            INNER JOIN bom on pn_list.id = bom.pnlist_id
                            inner JOIN product_list on product_list.id = bom.product_id
                            where ({} 
                                  "date" >=  to_date('{}', 'yyyy-mm-dd') and
                                  "date" <=  to_date('{}', 'yyyy-mm-dd'))
                        ) as idarray
                    )
                    GROUP BY bad_id
                ) as badtb
                right join bad_list on bad_list.id=bad_id
                order by bad_list.id
        """.format(sql_filter, begin_time, end_time)
        q_bad_statistic = db_session.execute(sql)

        temp_a = []
        for bad_sta in q_bad_statistic:
            temp1 = {}
            temp1['value'] = bad_sta[0]
            temp1['name'] = bad_sta[1]
            temp_a.append(temp1)
        temp['bad_statistic'] = temp_a

        sql1 = """
        select
            lost_time,
            anomaly_list.anomaly_name
        from(
            select
                anomaly_id,
                sum(lost_time) as lost_time
            from anomaly_record
            where daily_report_id in (
                SELECT
                    id
                FROM (
                    SELECT
                         daily_report.id,
                         daily_report.part_number,
                         pn_list.inj_product_name AS inj_product_name,
                         product_list.product_name as product_name 
                    FROM 
                        daily_report
                    INNER JOIN pn_list ON pn_list.part_number = daily_report.part_number
                    INNER JOIN bom on pn_list.id = bom.pnlist_id
                    inner JOIN product_list on product_list.id = bom.product_id
                    where ({}
                          "date" >=  to_date('{}', 'yyyy-mm-dd') and
                          "date" <=  to_date('{}', 'yyyy-mm-dd'))
                ) as idarray
            )
            GROUP BY anomaly_id
        ) as anotb
        right join anomaly_list on anomaly_list.id=anomaly_id
        order by anomaly_list.id
        """.format(sql_filter, begin_time, end_time)
        q_anomaly_statistic = db_session.execute(sql1)

        temp_a = []
        for anomaly_sta in q_anomaly_statistic:
            temp2 = {}
            temp2['value'] = float(anomaly_sta[0]) if (anomaly_sta[0] is not None) else None
            temp2['name'] = anomaly_sta[1]
            temp_a.append(temp2)
        temp['anomaly_statistic'] = temp_a
        result.append(temp)
        num = num + 1
    return result


@bp.route('/ajax_get_bad_progress', methods=['GET', 'POST'])
def ajax_get_bad_progress():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    if 'inj_product_name' in data.keys() and 'inj_part_number' in data.keys():
        q = PNList.query.filter(PNList.part_number == data['inj_part_number']).first()
        data['inj_product_name'] = q.inj_product_name
        print('here')
    weekday = datetime.date.today().weekday()
    result = []
    for i in range(weekday+3):
        begin_time = datetime.date.today() + datetime.timedelta(days=-i)
        end_time = datetime.date.today() + datetime.timedelta(days=-i)
        begin_time = str(begin_time)
        end_time = str(end_time)
        data['time_range'] = begin_time+' - '+end_time
        result.append({'day': begin_time, 'data': fun_bad_query(data)})
    # 前二周
    week = datetime.date.today().isocalendar()[1]  # 第幾周
    begin_time = datetime.date.today() + datetime.timedelta(days=-weekday-7)
    end_time = datetime.date.today() + datetime.timedelta(days=-weekday-1)
    begin_time = str(begin_time)
    end_time = str(end_time)
    data['time_range'] = begin_time + ' - ' + end_time
    result.append({'day': 'W' + str(week-1), 'data': fun_bad_query(data)})

    begin_time = datetime.date.today() + datetime.timedelta(days=-weekday - 14)
    end_time = datetime.date.today() + datetime.timedelta(days=-weekday-7-1)
    begin_time = str(begin_time)
    end_time = str(end_time)
    data['time_range'] = begin_time + ' - ' + end_time
    result.append({'day': 'W' + str(week-2), 'data': fun_bad_query(data)})
    # 每月
    today = datetime.date.today()
    month = today.month
    for i in range(month, 0, -1):
        begin_time = datetime.date(today.year, i, 1)
        if i == 12:
            end_time = datetime.date(today.year, 1, 1) + datetime.timedelta(days=-1)
        else:
            end_time = datetime.date(today.year, i+1, 1) + datetime.timedelta(days=-1)
        begin_time = str(begin_time)
        end_time = str(end_time)
        data['time_range'] = begin_time + ' - ' + end_time
        result.append({'day': str(i) + '月', 'data': fun_bad_query(data)})
    result.reverse()
    xaxis = []
    series = []
    legend = []
    bad_count = []
    ppm_data = []
    bad_count.append([])
    ppm_data.append([])
    bad_count[0].append('bad')
    ppm_data[0].append('bad')
    for a in result:

        if a['data']:
            print(a['day'], a['data'][0]['bad_statistic'])
            bad_count[0].append(a['day'])
            ppm_data[0].append(a['day'])
        else:
            pass

    i = 1
    q_bad = BadList.query.all()
    bad = []
    for temp in q_bad:
        bad.append(temp.bad_name)
    for item in bad:
        bad_count.append([])
        ppm_data.append([])
        bad_count[i].append(item)
        ppm_data[i].append(item)
        for a in result:
            if a['data']:
                bad_count[i].append(a['data'][0]['bad_statistic'][i-1]['value'] if a['data'][0]['bad_statistic'][i-1]['value'] is not None else 0)
                ppm_data[i].append(int(a['data'][0]['bad_statistic'][i-1]['value']/a['data'][0]['total_amount']*1000000) if a['data'][0]['bad_statistic'][i-1]['value'] is not None else 0)
            else:
                pass
        i = i + 1
    ppm_data.append(['ppm'])
    ppm_data.append(['產量'])
    for a in result:
        if a['data']:
            ppm_data[-1].append(a['data'][0]['total_amount'] if a['data'][0]['total_amount'] is not None else 0)
            ppm_data[-2].append(round(a['data'][0]['total_bad'] / a['data'][0]['total_amount'] * 1000000) if a['data'][0]['total_bad'] is not None else 0)
        else:
            pass

    legend = {}
    for a in bad_count:
        print(a)
        legend[a[0]] = any(a[1:])

    return jsonify([{'bad_count': bad_count, 'ppm_data': ppm_data, 'legend': legend}])
    # pie = copy.deepcopy(result[1]['data'][0]['bad_statistic'])
    # for item in result[1]['data'][0]['bad_statistic']:
    #     if item['value'] is None:
    #         pie.remove(item)
    # result.reverse()
    # q_bad = BadList.query.all()
    # i = 0
    # for bad in q_bad:
    #     temp_bad = []
    #     temp = {}
    #     temp['name'] = bad.bad_name
    #     for day in result:
    #         if day['data']:
    #             if not day['data'][0]['bad_statistic'][i]['value']:
    #                 temp_bad.append(None)
    #             else:
    #                 # temp_bad.append(day['data'][0]['bad_statistic'][i]['value'])
    #                 temp_bad.append(round(day['data'][0]['bad_statistic'][i]['value']/
    #                                       day['data'][0]['total_amount']*1000000, 0))
    #         else:
    #             # temp_bad.append(0)
    #             pass
    #     print(temp_bad)
    #     for n in temp_bad:
    #         if n is not None:
    #             bol = 1
    #             break
    #         else:
    #             bol = 0
    #     if bol:
    #         legend.append(temp['name'])
    #         temp['data'] = temp_bad
    #         temp['type'] = 'bar'
    #         # temp['label'] = {'show': 1, 'position': 'top'}
    #         temp['stack'] = '不良'
    #         series.append(temp)
    #     i = i + 1
    # temp_total = []
    # temp_ppm = []
    # for day in result:
    #     if day['data']:
    #         xaxis.append(day['day'])
    #
    #         if not day['data'][0]['total_amount']:
    #             temp_total.append(None)
    #             temp_ppm.append(None)
    #         else:
    #             temp_total.append(day['data'][0]['total_amount'])
    #             temp_ppm.append(round(day['data'][0]['total_bad']/day['data'][0]['total_amount']*1000000, 0))
    #     else:
    #         # temp_total.append(None)
    #         pass
    # series.append({'name': '產能', 'type': 'line', 'label': {'show': 1}, 'data': temp_total, 'xAxisIndex': 0, 'yAxisIndex': '1'})
    # series.append({'name': 'ppm', 'type': 'line', 'label': {'show': 1, 'color': 'black'}, 'data': temp_ppm, 'xAxisIndex': 0, 'yAxisIndex': '0'})
    #
    # legend.append('產能')
    #
    # return jsonify([{'key': 0, 'xAxis': xaxis, 'series': series, 'legend': legend,
    #                  'pie': {"date": str(datetime.date.today() + datetime.timedelta(days=-1)), "data": pie}}])


@bp.route('/ajax_get_improvement', methods=['POST'])
def ajax_get_improvement():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    weekday = datetime.date.today().weekday()
    if 'week' in data.keys():
        week = data['week']
    else:
        week = datetime.date.today().isocalendar()[1] - 1  # 第幾周
    this_week = datetime.date.today().isocalendar()[1]
    result = []
    # print('week: ', week)
    bad_sort = []

    begin_time = datetime.date.today() + datetime.timedelta(days=-weekday-(this_week-week)*7)
    end_time = datetime.date.today() + datetime.timedelta(days=-weekday-(this_week-week-1)*7-1)
    begin_time = str(begin_time)
    end_time = str(end_time)
    # print(begin_time)
    # print(end_time)
    data['time_range'] = begin_time + ' - ' + end_time
    result.append({'day': 'W' + str(week), 'data': fun_bad_query(data)})
    print(result[0]['data'])
    bad_name = []
    bad_value = []
    for bad in result[0]['data'][0]['bad_statistic']:
        bad_name.append(bad['name'])
        bad_value.append(bad['value'] if bad['value'] is not None else 0)
    print(result)
    print(bad_name)
    print(bad_value)
    for value in range(len(bad_value)):
        # print('value:', bad_value)
        temp = {}
        index = bad_value.index(max(bad_value))
        if bad_value[index]:
            temp['id'] = value
            temp['bad_name'] = bad_name.pop(index)
            temp['pics'] = bad_value.pop(index)
            temp['ppm'] = round(1000000*temp['pics']/result[0]['data'][0]['total_amount'], 0)
            temp['week'] = 'W' + str(week)
            bad_sort.append(temp)
        else:
            pass

    print('bad_sort: ')
    for i in range(len(bad_sort)):
        print(bad_sort[i])

    q_cause = BadCause.query.filter(BadCause.week == week,
                                    BadCause.inj_part_number == data['inj_part_number'])\
        .order_by(BadCause.pics.desc()).all()
    for cause in q_cause:
        for i in range(len(bad_sort)):
            if cause.bad_name == bad_sort[i]['bad_name']:
                bad_sort[i]['cause'] = cause.cause
                bad_sort[i]['improvement'] = cause.improvement
                bad_sort[i]['finish_date'] = cause.finish_date
                bad_sort[i]['response'] = cause.response
            else:
                pass
    print('bad_sort+record: ')
    for i in range(len(bad_sort)):
        print(bad_sort[i])

    return jsonify({'record': bad_sort})


@bp.route('/ajax_save_improvement', methods=['POST'])
def ajax_save_improvement():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    # print(current_user.username)

    error = '保存成功'
    if 'bad' in data.keys():
        for key in data['bad'].keys():
            if 'cause' in data['bad'][key].keys():
                cause = data['bad'][key]['cause']
            else:
                cause = ''
            if 'improvement' in data['bad'][key].keys():
                improvement = data['bad'][key]['improvement']
            else:
                improvement = ''
            if 'finish_date' in data['bad'][key].keys():
                finish_date = data['bad'][key]['finish_date']
            else:
                finish_date = ''
            if 'response' in data['bad'][key].keys():
                response = data['bad'][key]['response']
            else:
                response = ''
            q_cause = BadCause.query.filter(BadCause.week == data['bad'][key]['week'][1:],
                                            BadCause.bad_name == key,
                                            BadCause.inj_part_number == data['inj_part_number']).first()
            if q_cause is None:
                new_cause = BadCause(week=data['bad'][key]['week'][1:],
                                     inj_part_number=data['inj_part_number'],
                                     bad_name=data['bad'][key]['bad_name'],
                                     ppm=data['bad'][key]['ppm'],
                                     pics=data['bad'][key]['pics'],
                                     cause=cause,
                                     improvement=improvement,
                                     finish_date=finish_date,
                                     response=response)
                db_session.add(new_cause)
                error = '新增不良對策'
            else:
                print("更新不良對策")
                q_cause.cause = cause
                q_cause.improvement = improvement
                q_cause.finish_date = finish_date
                q_cause.response = response
                db_session.add(q_cause)
                error = '更新不良對策'
        db_session.commit()
    return jsonify({'error': error})
