from flask import Blueprint, render_template, jsonify, request


bp = Blueprint('auth', __name__)

@bp.errorhandler(403)
def no_permission(e):
    if 'XMLHttpRequest' in request.headers.keys():
        if request.headers['X-Requested-With'] == 'XMLHttpRequest':
            return jsonify({'error': e})
        else:
            return jsonify({'error': "What happened?"})
    else:
        return render_template('no_authority.html'), 403

from . import auth, query