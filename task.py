import datetime
from __init__ import scheduler
from model import *
import random


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
        else:
            new_amount = Amount(machine_id=ma.id,
                                produce_amount=amount,
                                state=state,
                                update_time=datetime.datetime.now())
            db_session.add(new_amount)
    db_session.commit()
    pass


@scheduler.task("cron", id="init_data", hour='0', minute='0', second="30")
def init_data(date=None):
    q_machine = MachineList.query.all()  # 儲存進去記憶體
    q_mold = None

    for ma in q_machine:

        '''initial amount'''
        amount = 0
        state = 0
        q_amount = Amount.query.filter(Amount.machine_id == ma.id).first()
        if q_amount:

            q_daily = DailyReport.query.filter(DailyReport.date == datetime.date.today() + datetime.timedelta(days=-1),
                                               DailyReport.machine == ma.machine_name,
                                               DailyReport.building == ma.building).first()

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

        '''adding schedule'''
        machine_name = ma.machine_name

        if machine_name[0] == 'A':
            if int(machine_name[1:]) in range(1, 10):
                q_mold = mold_fun("001-0020-9282", q_mold, ma)
                if machine_name == 'A09':
                    q_mold = None
            else:
                q_mold = mold_fun("001-0020-9283", q_mold, ma)
                if machine_name == 'A18':
                    q_mold = None

        elif machine_name[0] == 'B':
            if int(machine_name[1:]) in range(1, 9):
                q_mold = mold_fun("001-0020-9284", q_mold, ma)
                if machine_name == 'B08':
                    q_mold = None
            else:
                q_mold = mold_fun("001-0020-9285", q_mold, ma)
                if machine_name == 'B16':
                    q_mold = None
        elif machine_name[0] == 'C':
            if int(machine_name[1:]) in range(1, 8):
                q_mold = mold_fun("002-0030-3982", q_mold, ma)
                if machine_name == 'C07':
                    q_mold = None
            elif int(machine_name[1:]) in range(8, 18):
                q_mold = mold_fun("002-0030-3983", q_mold, ma)
                if machine_name == 'C17':
                    q_mold = None
            else:
                q_mold = mold_fun("002-0030-3984", q_mold, ma)
                if machine_name == 'C22':
                    q_mold = None
        else:
            if int(machine_name[1:]) in range(1, 11):
                q_mold = mold_fun("002-0030-3985", q_mold, ma)
                if machine_name == 'D10':
                    q_mold = None
            else:
                q_mold = mold_fun("002-0030-3986", q_mold, ma)
                if machine_name == 'D20':
                    q_mold = None

    db_session.commit()


def mold_fun(part_number, q_mold, ma):
    q_pn = PNList.query.filter(PNList.part_number == part_number).first()
    if not q_mold:
        q_mold = MoldPnAssociation.query.filter(MoldPnAssociation.pnlist_id == q_pn.id).all()
        q_mold = iter(q_mold)
    try:
        mold = next(q_mold)
        mold_id = mold.mold_id
        date = datetime.date.today() + datetime.timedelta(days=8)
        new_schedule = ProduceSchedule(date=date,
                                       machine_id=ma.id,
                                       mold_id=mold_id,
                                       pnlist_id=q_pn.id,
                                       amount=q_pn.std_produce,
                                       product_name=q_pn.inj_product_name,
                                       produce_order='')
        new_daily = DailyReport(date=date,
                                building="A18",
                                machine=ma.machine_name,
                                machine_id=ma.id,
                                mold_id=mold.id,
                                part_number=q_pn.part_number,
                                mold=mold.mold_number_f)
        db_session.add(new_daily)

        db_session.add(new_schedule)
        db_session.commit()
    except StopIteration:
        print("沒有模具了")
        q_mold = None
    return q_mold


