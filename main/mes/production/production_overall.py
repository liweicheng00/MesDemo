import datetime

from flask import jsonify, render_template, request, session

from main.mes.production import bp
from main.model import *
from main.tictoc import *
# from sqlalchemy.event import listen
# from sqlalchemy.pool import Pool
#
#
# def my_on_connect(dbapi_con):
#     print('new', dbapi_con)
#
#
# listen(db_session, 'after_commit', my_on_connect)


@bp.route('/production_overall')
def production_overall():
    return render_template('main/production/production_overall_horizontal_v2.html')


def fun_machine_list(building):

    return


def fun_compare_schedule_actual_chart(machine_list, now, today, amount, chart_order):

    return


@bp.route('/ajax_get_machine_state')
def ajax_get_machine_state():

    return jsonify()


@bp.route('/ajax_get_machine_detail', methods=['POST'])
def ajax_get_machine_detail():

    return jsonify()


@bp.route('/ajax_get_machine_detail_schedule', methods=['POST'])
def ajax_get_machine_detail_schedule():

    return jsonify()

