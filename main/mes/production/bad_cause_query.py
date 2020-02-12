import datetime
import json
import copy
from flask import (
    jsonify, render_template, request
)
from flask_login import current_user
from main.mes.production import bp
from main.model import *


@bp.route('/bad_cause_query')
def bad_cause_query():
    return render_template('main/production/bad_cause_query.html')


@bp.route('/ajax_bad_cause_query', methods=['GET', 'POST'])
def ajax_bad_cause_query():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    if 'part_number' in data.keys() and data['part_number']:
        if 'bad_name' in data.keys() and data['bad_name']:
            q_bad_cause = BadCause.query.filter(BadCause.inj_part_number == data['part_number'],
                                                BadCause.bad_name == data['bad_name'])\
                .order_by(BadCause.bad_name) \
                .all()
        else:
            q_bad_cause = BadCause.query.filter(BadCause.inj_part_number == data['part_number'])\
                .order_by(BadCause.bad_name) \
                .all()
    else:
        q_bad_cause = BadCause.query.filter(BadCause.bad_name == data['bad_name'])\
            .order_by(BadCause.bad_name) \
            .all()

    result = []
    for q in q_bad_cause:
        print(q.bad_name, q.improvement)
        result.append(q.to_dict())
    return jsonify(result)
