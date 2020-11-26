import datetime
from __init__ import scheduler, app
from model import *
import random
import json
from flask import jsonify


@scheduler.task("interval", id="fake_data", minutes=1)
def fake_data():
    q_machine = MachineList.query.all()  # 儲存進去記憶體
    for ma in q_machine:
        # 隨機數據
        amount = random.randint(0, 9)
        state = random.randint(0, 3)

        q_amount = Amount.query.filter(Amount.machine_id == ma.id).first()
        if q_amount:
            q_amount.produce_amount = q_amount.produce_amount + amount
            q_amount.state = state
            q_amount.update_time = datetime.datetime.now()
            db_session.add(q_amount)

            q_daily = DailyReport.query.filter(DailyReport.date == datetime.datetime.today().date(),
                                               DailyReport.machine_id == ma.id).first()
            if q_daily:
                q_daily.produce_amount = q_amount.produce_amount
                db_session.add(q_daily)
        else:
            new_amount = Amount(machine_id=ma.id,
                                produce_amount=amount,
                                state=state,
                                update_time=datetime.datetime.now())
            db_session.add(new_amount)
    db_session.commit()


@scheduler.task("interval", id="init_data",  minutes=15)
def init_data(date=None):
    q_machine = MachineList.query.all()  # 儲存進去記憶體
    q_mold = None
    date = datetime.date.today()+ datetime.timedelta(days=1)
    q_schedule = ProduceSchedule.query.filter(ProduceSchedule.date == date).first()

    if not q_schedule:

        for ma in q_machine:

            '''initial amount'''
            amount = 0
            state = 0
            q_amount = Amount.query.filter(Amount.machine_id == ma.id).first()
            if q_amount:

                q_daily = DailyReport.query.filter(DailyReport.date == datetime.date.today() + datetime.timedelta(days=-1),
                                                   DailyReport.machine == ma.machine_name,
                                                   DailyReport.building == ma.building).first()

                if q_daily:
                    q_daily.produce_amount = q_amount.produce_amount
                    db_session.add(q_daily)

                q_amount.produce_amount = amount
                q_amount.state = state
                q_amount.update_time = datetime.datetime.now()
                db_session.add(q_amount)
            else:
                new_amount = Amount(machine_id=ma.id,
                                    produce_amount=amount,
                                    state=state,
                                    update_time=datetime.datetime.now())
                db_session.add(new_amount)
            db_session.commit()

        '''adding schedule'''

        with open('schedule.json') as f:
            data = json.load(f)

            print(len(data))
            for info in data:
                new_schedule = ProduceSchedule(date=date,
                                               machine_id=info['machine_id'],
                                               mold_id=info['mold_id'],
                                               pnlist_id=info['pnlist_id'],
                                               amount=info['amount'],
                                               product_name=info['product_name'],
                                               produce_order='')
                new_daily = DailyReport(date=date,
                                        building="A18",
                                        machine=info['machine_name'],
                                        machine_id=info['machine_id'],
                                        mold_id=info['mold_id'],
                                        part_number=info['part_number'],
                                        mold=info['mold'],
                                        record_state=0)
                db_session.add(new_schedule)
                db_session.add(new_daily)
            db_session.commit()


@scheduler.task("interval", id="delete_data",  minutes=1)
def delete_data():
    date = datetime.datetime.today()
    q_schedule = ProduceSchedule.query.filter(ProduceSchedule.date <= date + datetime.timedelta(days=-30)).all()
    q_daily = DailyReport.query.filter(DailyReport.date <= date + datetime.timedelta(days=-30)).all()

    for q in q_schedule:
        db_session.delete(q)
    for q in q_daily:
        db_session.delete(q)
    db_session.commit()


if __name__ == '__main__':
    init_data()

