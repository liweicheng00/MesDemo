from flask import Blueprint, render_template, jsonify, request
from main.permission import *

bp = Blueprint('schedule', __name__)


@bp.errorhandler(403)
def no_permission(e):
    if 'XMLHttpRequest' in request.headers.keys():
        if request.headers['X-Requested-With'] == 'XMLHttpRequest':
            return jsonify({'error': e})
        else:
            return jsonify({'error': "What happened?"})
    else:
        return render_template('no_authority.html')


from . import schedule, overall, material_dispatch, daily_report
