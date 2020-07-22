from flask import Blueprint, render_template, jsonify, request

bp = Blueprint('revise', __name__)


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

from . import anomaly_revise, bad_revise, bom_revise, material_revise, product_revise, upload_data, \
    machine_revise, mold_revise
