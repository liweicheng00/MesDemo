from flask import Blueprint, jsonify, request, render_template
import datetime
bp = Blueprint('production', __name__)

#
# @bp.route("/ajax_get_time", methods=['GET'])
# def ajax_get_time():
#     time = datetime.datetime.now().time()
#     A = datetime.time(7, 30, 0)
#     B = datetime.time(19, 30, 0)
#     C = datetime.time(0, 0, 0)
#     if time.__ge__(A) and time.__lt__(B):
#         work_class = '白班'
#     else:
#         work_class = '夜班'
#     if time.__ge__(C) and time.__lt__(A):
#         next_day = True
#     else:
#         next_day = False
#     return jsonify({"time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#                     'work_class': work_class,
#                     'next_day': next_day})

@bp.errorhandler(403)
def no_permission(e):
    if 'XMLHttpRequest' in request.headers.keys():
        if request.headers['X-Requested-With'] == 'XMLHttpRequest':
            return jsonify({'error': e})
        else:
            return jsonify({'error': "What happened?"})
    else:
        # return
        return render_template('no_authority.html'), 403

from . import production_overall, bad_statistic, \
    material_check, bad_cause_query, \
    first_part, produce_statistics

