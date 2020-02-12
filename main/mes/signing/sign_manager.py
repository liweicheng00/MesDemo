import datetime

from flask import (jsonify, render_template, request)
from flask_login import current_user

from main.mes.signing import bp
from main.model import *


@bp.route('/ajax_get_badge_update', methods=['GET'])
def ajax_get_badge_update():
    user_id = current_user.id
    q_user = User.query.filter(User.id == user_id).first()
    q_sign_state = SignerState.query.filter(SignerState.signer == str(q_user.id), SignerState.flag == 1).count()
    print(q_sign_state)
    # q_event = SignEvent.query.filter(SignEvent.initiator_id == user_id).count()
    return jsonify({'badge': q_sign_state, 'launch': ''})


@bp.route('/sign_process_manager')
def sign_process_manager():
    return render_template('main/signing/sign_process_manager.html')


@bp.route('/ajax_get_sign_table_list', methods=['GET', 'POST'])
def ajax_get_sign_table_list():
    q_table_list = SignTableList.query.all()
    result = []
    for table_list in q_table_list:
        temp = {}
        temp['value'] = table_list.table_name
        temp['text'] = table_list.name
        temp['id'] = table_list.id
        result.append(temp)
    return jsonify(result)


@bp.route('/ajax_get_sign_process', methods=['GET', 'POST'])
def ajax_get_sign_process():
    sql = """select 
                sign_process_list_detail.signer,
                sign_process_list_detail.sign_order,
                sign_process_list.process_name,
                sign_process_list.id,
                sign_table_list.table_name
            from sign_process_list_detail
            inner join sign_process_list on sign_process_list_detail.process_list_id = sign_process_list.id
            inner join sign_table_list on sign_table_list.id = sign_process_list.table_list_id
            """
    sql1 = """ 
            order by sign_table_list.table_name, sign_process_list.process_name, sign_process_list_detail.sign_order"""
    if request.method == "GET":
        q_result = db_session.execute(sql+sql1)
    elif request.method == "POST":
        data = request.get_data()
        data = json.loads(data)
        print(data)
        sql2 = " where sign_table_list.table_name = '" + data['sign_table_list'] + "'"
        q_result = db_session.execute(sql+sql2+sql1)
    else:
        q_result = []
    process = {}
    for result in q_result:
        if not result[4] in process.keys():
            process[result[4]] = {}
        if not result[3] in process[result[4]]:
            process[result[4]][result[3]] = {'process_list_name': result[2], 'process': []}
        process[result[4]][result[3]]['process'].append({'order': result[1], 'name': result[0]})
    a = []
    for p in process.keys():
        for pp in process[p].keys():
            b = {}
            b['table'] = p
            b['process_name'] = pp
            b['process_list_name'] = process[p][pp]['process_list_name']
            b['process'] = process[p][pp]['process']
            a.append(b)
    return jsonify({'process': process, 'array_process': a})


@bp.route('/ajax_upload_sign_process', methods=['POST'])
def ajax_upload_sign_process():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    table = data['table']
    q_table_list = SignTableList.query.filter(SignTableList.table_name == table).first()
    if q_table_list is not None:
        table_list_id = q_table_list.id
    else:
        return jsonify({'error': '找不到此表單'})

    order = data['order']
    process_name = data['process_name']
    new_process = SignProcessList(table_list_id=table_list_id, process_name=process_name)
    db_session.add(new_process)
    db_session.commit()

    q_process = SignProcessList.query.filter(SignProcessList.table_list_id == table_list_id,
                                             SignProcessList.process_name == process_name).first()
    process_id = q_process.id
    for key in order.keys():
        print(key)
        new_process_detail = SignProcessListDetail(process_list_id=process_id,
                                                   user_id=order[key]['user_id'],
                                                   signer=order[key]['work_name'],
                                                   sign_order=order[key]['order'])
        db_session.add(new_process_detail)
    db_session.commit()
    return jsonify({'error': '新增成功'})


@bp.route('/ajax_get_user', methods=['POST'])
def ajax_get_user():
    # todo: 同名防呆
    data = request.get_data()
    data = json.loads(data)
    if 'work_number' in data.keys():
        q_user = User.query.filter(User.username == data['work_number']).first()
        if q_user is not None:
            return jsonify({'state': 1, 'work_name': q_user.name, 'user_id': q_user.id})
        else:
            return jsonify({'input': 'input:' + data['work_number'], 'error': 'work_name is none.'})

    if 'work_name' in data.keys():
        q_user = User.query.filter(User.name == data['work_name']).first()
        if q_user is not None:
            return jsonify({'state': 1, 'work_number': q_user.username, 'user_id': q_user.id})
        else:
            return jsonify({'input': 'input:' + data['work_name'], 'error': 'Work_number is none.'})

    return jsonify({'state': 0})


@bp.route('/ajax_create_sign_event', methods=['POST'])
def ajax_create_sign_event():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    initiator = current_user.name
    initiator_id = current_user.id
    form_index = data['form_index']  # get this
    date = datetime.datetime.now()
    # todo: 一張表一個簽核流程
    q_table_list = SignTableList.query.filter(SignTableList.table_name == data['table']).first()
    new_sign_event = SignEvent(date=date, table_list_id=q_table_list.id, process_name_id=data['process_name_id'],
                               form_index=form_index, sign_state=0, initiator=initiator, initiator_id=initiator_id)
    db_session.add(new_sign_event)
    db_session.commit()
    q_sign_event = SignEvent.query.filter(SignEvent.date == date, SignEvent.process_name_id == data['process_name_id'],
                                          SignEvent.form_index == form_index).first()
    sign_event_id = q_sign_event.id
    q_process_detail = SignProcessListDetail.query.filter(
        SignProcessListDetail.process_list_id == data['process_name_id']).all()
    for process_detail in q_process_detail:
        new_signer_state = SignerState(event_id=sign_event_id, process_list_detail_id=process_detail.id,
                                       signer=process_detail.user_id, signer_order=process_detail.sign_order,
                                       signer_state=0, flag=1 if (process_detail.sign_order == 1) else 0)
        db_session.add(new_signer_state)
    db_session.commit()
    return jsonify({'sign_event_id':  sign_event_id})


@bp.route('/work_item')
def work_item():
    return render_template('main/signing/work_item.html')


@bp.route('/ajax_get_work_item', methods=['POST'])
def ajax_get_work_item():

    print('current user:', current_user.username, current_user.id)
    user_id = current_user.id

    data = request.get_data()
    data = json.loads(data)
    print(data)
    category = data['category']
    sql1 = """
                SELECT
                    sign_event.*,
                    sign_table_list.name,
                    sign_table_list.table_name,
                    signer_state.signer_state
                FROM
                    sign_event
                inner join sign_table_list on sign_event.table_list_id = sign_table_list.id
                inner join signer_state on sign_event.id = signer_state.event_id
                WHERE
                    sign_event.id IN (
                        SELECT
                            event_id
                        FROM
                            signer_state
                        WHERE
            """
    if data['category'] == 'work_item':
        sql2 = """
                    signer = """ + str(user_id) + """ and signer_state = 0)
                    and signer_state.signer = """ + str(user_id) + """ and signer_state.signer_state = 0 
                    and sign_event.sign_state = 0
                """
        sql = sql1 + sql2
        q_sign_state = db_session.execute(sql)
    elif data['category'] == 'retreat_item':
        sql2 = """
                    signer = """ + str(user_id) + """ and signer_state = 2)
                    and signer_state.signer = """ + str(user_id) + """ and signer_state.signer_state = 2
                """
        sql = sql1 + sql2
        q_sign_state = db_session.execute(sql)
    elif data['category'] == 'finish_item':
        sql2 = """
            signer = """ + str(user_id) + """ and signer_state = 1) 
            and signer_state.signer = """ + str(user_id) + """ and signer_state.signer_state = 1
        """
        sql = sql1 + sql2
        q_sign_state = db_session.execute(sql)
    else:
        q_sign_state = []

    result = []
    for sign_state in q_sign_state:
        temp = {}
        temp['event_id'] = sign_state[0]
        temp['date'] = sign_state[1].strftime('%Y-%m-%d %H:%M:%S')
        temp['work_item'] = sign_state[9]
        temp['work_item_chi'] = sign_state[8]
        temp['form_index'] = sign_state[6]
        temp['initiator'] = sign_state[5]
        temp['url'] = "<a href='/redirect_sign_page?work_item=" + str(temp['work_item'])\
                      + "&form_index=" + str(temp['form_index']) + "&event_id=" + str(temp['event_id'])\
                      + "&category=" + str(category) + "' target='_blank' class='layui-table-link'>url</a>"
        temp['state'] = map_state(sign_state[10])

        temp['sign_order'] = ''
        result.append(temp)
    #     todo: 簽核順序優化
    # for sign_state in q_sign_state:
    #     temp = {}
    #     # print('sign event:', sign_state.event_id, 'signer:', sign_state.signer,
    #     #       'signer order:', sign_state.signer_order, 'signer state:', sign_state.signer_state)
    #     q_event = SignEvent.query.filter(SignEvent.id == sign_state.event_id).first()
    #     temp['event_id'] = sign_state.event_id
    #     temp['date'] = q_event.date.strftime('%Y-%m-%d %H:%M:%S')
    #     temp['work_item'] = q_event.sign_table_list.table_name
    #     temp['work_item_chi'] = q_event.sign_table_list.name
    #     temp['form_index'] = q_event.form_index
    #     temp['initiator'] = q_event.initiator
    #     temp['url'] = "<a href='/redirect_sign_page?work_item=" + temp['work_item']\
    #                   + "&form_index=" + temp['form_index'] + "&event_id=" + str(temp['event_id'])\
    #                   + "&category=" + category + "' target='_blank' class='layui-table-link'>url</a>"
    #     temp['state'] = map_state(sign_state.signer_state)
    #     q_precess_detail = SignProcessListDetail.query.filter(
    #         SignProcessListDetail.process_list_id == q_event.process_name_id).all()
    #     s = ''
    #     for process_detail in q_precess_detail:
    #         s = s + str(process_detail.sign_order) + process_detail.signer + '>>'
    #     temp['sign_order'] = s
    #     result.append(temp)
    print(result)
    return jsonify(result)


@bp.route('/launch_item')
def launch_item():
    return render_template('main/signing/launch_item.html')


@bp.route('/ajax_get_launch_item', methods=['POST'])
def ajax_get_launch_item():

    print('current user:', current_user.username, current_user.id)
    user_id = current_user.id

    data = request.get_data()
    data = json.loads(data)
    print(data)
    category = data['category']
    sql1 = """
                SELECT
                    sign_event.*,
                    sign_table_list.name,
                    sign_table_list.table_name
                FROM
                    sign_event
                inner join sign_table_list on sign_event.table_list_id = sign_table_list.id
                WHERE
            """
    if data['category'] == 'work_item':
        sql2 = """
                    (sign_event.initiator_id =  """ + str(user_id) + """ 
                    OR initiator = '""" + str(current_user.name) + """')
                    and sign_event.sign_state = 0
                """
        sql = sql1 + sql2
        q_sign_state = db_session.execute(sql)
    elif data['category'] == 'retreat_item':
        sql2 = """
                           (sign_event.initiator_id =  """ + str(user_id) + """ 
                           OR initiator = '""" + str(current_user.name) + """')
                           and sign_event.sign_state = 2
                       """
        sql = sql1 + sql2
        q_sign_state = db_session.execute(sql)
    elif data['category'] == 'finish_item':
        sql2 = """
                           (sign_event.initiator_id =  """ + str(user_id) + """ 
                           OR initiator = '""" + str(current_user.name) + """')
                           and sign_event.sign_state = 1
                       """
        sql = sql1 + sql2

        print(sql)
        q_sign_state = db_session.execute(sql)
    else:
        q_sign_state = []

    result = []
    for sign_state in q_sign_state:
        temp = {}
        temp['event_id'] = sign_state[0]
        temp['date'] = sign_state[1].strftime('%Y-%m-%d %H:%M:%S')
        temp['work_item'] = sign_state[9]
        temp['work_item_chi'] = sign_state[8]
        temp['form_index'] = sign_state[6]
        temp['initiator'] = sign_state[5]
        temp['url'] = "<a href='/redirect_sign_page?work_item=" + str(temp['work_item'])\
                      + "&form_index=" + str(temp['form_index']) + "&event_id=" + str(temp['event_id'])\
                      + "&category=" + str(category) + "' target='_blank' class='layui-table-link'>url</a>"
        temp['state'] = map_state(sign_state[4])

        result.append(temp)

    print(result)
    return jsonify(result)


@bp.route('/redirect_sign_page')
def redirect_sign_page():
    print(request.args.get('work_item'))
    print(request.args.get('form_index'))
    work_item = request.args.get('work_item')
    form_index = request.args.get('form_index')
    event_id = request.args.get('event_id')
    category = request.args.get('category')
    if work_item == 'daily_bad_report':
        return render_template('main/signing/table/daily_bad_report_query.html',
                               form_index=form_index, event_id=event_id, category=category)
    elif work_item == 'inj_param_record':
        return render_template('main/signing/table/inj_param_record.html',
                               form_index=form_index, event_id=event_id, category=category)
    elif work_item == 'inj_param_standard':
        return render_template('main/signing/table/inj_param_standard.html',
                               form_index=form_index, event_id=event_id, category=category)
    # return render_template('main/production/bad_record_query.html')
    return '404'


@bp.route('/ajax_get_event_process', methods=['POST'])
def ajax_get_event_process():
    data = request.get_data()
    data = json.loads(data)
    event_id = data['event_id']
    q_sign_state = SignerState.query.filter(SignerState.event_id == event_id).order_by(SignerState.signer_order).all()
    result = []
    for sign_state in q_sign_state:
        temp = {}
        q_user = User.query.filter(User.id == sign_state.signer).first()
        temp['order'] = sign_state.signer_order
        temp['user_id'] = sign_state.signer
        temp['name'] = q_user.name
        temp['sign_state'] = map_state(sign_state.signer_state)
        temp['sign_date'] = sign_state.sign_date.strftime('%Y-%m-%d %H:%M:%S') if sign_state.sign_date else None
        result.append(temp)
    return jsonify(result)


def map_state(state):
    if state == 0:
        return '待簽'
    elif state == 1:
        return '完成'
    else:
        return '退回'


@bp.route('/ajax_sign_confirm', methods=['POST'])
def ajax_sign_confirm():
    data = request.get_data()
    data = json.loads(data)
    event_id = data['event_id']
    date = datetime.datetime.now()
    q_sign_state = SignerState.query.filter(SignerState.event_id == event_id,
                                            SignerState.signer == current_user.id,
                                            SignerState.signer_state == 0,
                                            SignerState.flag == 1).first()
    order = q_sign_state.signer_order
    q_sign_state.signer_state = 1
    q_sign_state.flag = 0
    q_sign_state.sign_date = date
    db_session.add(q_sign_state)
    db_session.commit()

    q_sign_state = SignerState.query.filter(SignerState.event_id == event_id, SignerState.signer_order == order+1).all()
    if q_sign_state:
        for sign_state in q_sign_state:
            sign_state.flag = 1
            db_session.add(sign_state)
            db_session.commit()
        return jsonify({'event_state': 0})
    else:
        print('No other sign process. Event finished')
        q_event = SignEvent.query.filter(SignEvent.id == event_id).first()
        q_event.sign_state = 1
        db_session.add(q_event)
        db_session.commit()
        return jsonify({'event_state': 1})


@bp.route('/ajax_sign_retreat', methods=['POST'])
def ajax_sign_retreat():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    event_id = data['event_id']
    date = datetime.datetime.now()
    q_sign_state = SignerState.query.filter(SignerState.event_id == event_id,
                                            SignerState.signer == current_user.id).first()
    q_sign_state.signer_state = 2
    q_sign_state.flag = 0
    q_sign_state.sign_date = date
    db_session.add(q_sign_state)
    db_session.commit()

    q_event = SignEvent.query.filter(SignEvent.id == event_id).first()
    q_event.sign_state = 2
    db_session.add(q_event)
    db_session.commit()
    return jsonify()

# todo:完成通知
