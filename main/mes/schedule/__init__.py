from flask import Blueprint, render_template, jsonify, request
from flask_principal import Permission, RoleNeed

bp = Blueprint('schedule', __name__)

"""權限管理"""
admin_permission = Permission(RoleNeed('super'))
user_permission = Permission(RoleNeed('user'))


@bp.errorhandler(403)
def no_permission(e):
    if 'XMLHttpRequest' in request.headers.keys():
        if request.headers['X-Requested-With'] == 'XMLHttpRequest':
            return jsonify({'error': e})
        else:
            return jsonify({'error': "What happened?"})
    else:
        return render_template('no_authority.html')


from . import schedule, daily_report\
    , overall, auto_schedule, material_dispatch
