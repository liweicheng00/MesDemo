from flask import Blueprint, jsonify
import datetime
bp = Blueprint('production', __name__)


@bp.route("/ajax_get_time", methods=['GET'])
def ajax_get_time():
    time = datetime.datetime.now().time()
    A = datetime.time(7, 30, 0)
    B = datetime.time(19, 30, 0)
    C = datetime.time(0, 0, 0)
    if time.__ge__(A) and time.__lt__(B):
        work_class = '白班'
    else:
        work_class = '夜班'
    if time.__ge__(C) and time.__lt__(A):
        next_day = True
    else:
        next_day = False
    return jsonify({"time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'work_class': work_class,
                    'next_day': next_day})


from . import production_overall, bad_statistic, \
    material_check, issuance, inbound, get_bad_statistic, bad_cause_query, \
    first_part

