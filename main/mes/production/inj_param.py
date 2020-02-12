import datetime, time
import decimal

from flask import (jsonify, render_template, request, url_for)

from main.mes.production import bp
from main.model import *
from main.model import db_session as db_model1
from main.model2 import *
from main.model2 import db_session as db_model2
from main.tictoc import *


@bp.route('/inj_param_record')
def inj_param_record():
    return render_template('main/production/inj_param_record.html')


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


@bp.route("/ajax_get_used_mold", methods=['POST'])
def ajax_get_used_mold():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    date = data['date']
    date = datetime.datetime.strptime(date, "%Y-%m-%d")
    building = data['building']
    machine = data['machine']
    # part_number = data['part_number']
    # worker = data['worker']
    # QC = data['QC']
    q_machine = MachineList.query.filter(MachineList.building == building,
                                         MachineList.machine_name == machine).first()
    machine_id = q_machine.id
    q_schedule = ProduceSchedule.query.filter(ProduceSchedule.date == date,
                                              ProduceSchedule.machine_id == machine_id).all()
    error = ''
    result = []
    temp_b = {}
    if not q_schedule:
        error = '今日無排產'
    else:
        if len(q_schedule) > 1:
            error = '請選擇模具'
        temp = {}
        temp['part_number'] = q_schedule[0].pn_list.part_number
        temp['mold'] = q_schedule[0].mold_list.mold_number_f
        temp['mold_id'] = q_schedule[0].mold_id
        temp['machine_id'] = q_schedule[0].machine_id
        result.append(temp)

    temp_b['default'] = result
    q_schedule = db_model1.query(ProduceSchedule.pnlist_id, ProduceSchedule.mold_id) \
        .filter(ProduceSchedule.machine_id == machine_id).distinct()
    temp_a = {}
    for schedule in q_schedule:
        print(schedule)
        if not schedule[0] in temp_a.keys():
            temp_a[schedule[0]] = []
        temp_a[schedule[0]].append(schedule[1])
    print(temp_a)

    for key in temp_a:
        q_pnlist = PNList.query.filter(PNList.id == key).first()
        temp_b[q_pnlist.part_number] = []
        for mold in temp_a[key]:
            q_mold = MoldList.query.filter(MoldList.id == mold).first()

            temp = {}
            temp['part_number'] = q_pnlist.part_number
            temp['mold'] = q_mold.mold_number_f
            temp['mold_id'] = q_mold.id
            temp['machine_id'] = machine_id
            temp_b[q_pnlist.part_number].append(temp)

    return jsonify({'state': 0, 'error': error, 'data': temp_b, 'test': temp_b})


@bp.route('/ajax_get_inj_param', methods=['POST'])
def ajax_get_inj_param():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    result = {}
    A = time.time()
    q_machine = Machine.query.filter(Machine.MachineName == data['machine'],
                                     Machine.BuildingNr == data['building']).first()
    q_mold = MoldList.query.filter(MoldList.id == data['mold_id']).first()
    q_machine_list = MachineList.query.filter(MachineList.id == data['machine_id']).first()
    # print(q_machine_list.machine_type)
    # print(q_mold.mold_pn_association[0].pn_list.part_number)
    # print(q_mold.mold_pn_association[0].pn_list.pn_material_list[0].material_list.material_part_number)
    # print(q_mold.mold_pn_association[0].pn_list.pn_material_list[0].material_list.material_spec)
    result['machine_type'] = q_machine_list.machine_type
    result['machine_no'] = q_machine_list.machine_no
    # result['part_number'] = data['part_number']
    result['part_number'] = q_mold.mold_pn_association[0].pn_list.part_number
    result['material_part_number'] = q_mold.mold_pn_association[0].pn_list.pn_material_list[0].material_list.material_part_number
    result['material_spec'] = q_mold.mold_pn_association[0].pn_list.pn_material_list[0].material_list.material_spec
    B = time.time()
    print('time:', B-A)

    q_param = InjParam.query.filter(InjParam.MachineId == q_machine.MachineId).first().to_dict()
    q_standard = InjParamStandard.query.filter(InjParamStandard.MOLD_ID == data['mold_id'],
                                               InjParamStandard.MACHINE_ID == data['machine_id'],
                                               InjParamStandard.flag == 1,
                                               InjParamStandard.part_number == data['part_number']).first()
    if q_standard is None:
        q_standard = {}
    else:
        q_standard = q_standard.to_dict()

    result['machine'] = q_param['MachineId']
    for key in q_param.keys():
        result[key] = {}
        result[key]['name'] = key
        result[key]['auto'] = 1
        result[key]['actual'] = q_param[key]
        if key in q_standard:
            result[key]['std'] = float(q_standard[key]) if q_standard[key] is not None else '-'
        else:
            result[key]['std'] = 0
    for (key, key1) in [('NowTn2', 'Tn2'), ('NowT1', 'T1'), ('NowT2', 'T2'), ('NowT3', 'T3'), ('NowT4', 'T4')]:
        if key1 in q_standard:
            result[key]['std'] = float(q_standard[key1]) if q_standard[key1] is not None else '-'
        else:
            result[key1]['std'] = 0

        # result[key]['std'] = float(q_standard[key1]) if key1 in q_standard else '-'

    try:
        with open("static/json/ManualParams.json", 'r', encoding='utf8') as rf:
            load_dict = json.load(rf)
    except:
        print('read ManualParams.json failed.')
        with open("venv/lib/python3.7/site-packages/main/static/json/ManualParams.json", 'r', encoding='utf8') as rf:
            load_dict = json.load(rf)
        print('read ManualParams.json success.')
    else:
        print('read ManualParams.json success.')
    q_param = InjParamRecord.query.filter(InjParamRecord.MOLD_ID == data['mold_id'],
                                          InjParamRecord.MACHINE_ID == data['machine_id'],
                                          InjParamRecord.part_number == data['part_number']) \
        .order_by(InjParamRecord.TIMESTAMP.desc()).first()

    if q_param is not None:
        q_param = q_param.to_dict()
        for key in load_dict.keys():
            result[key] = {}
            result[key]['name'] = key
            result[key]['auto'] = 0
            result[key]['actual'] = float(q_param[key]) if q_param[key] is not None else None
            if key in q_standard:
                result[key]['std'] = float(q_standard[key]) if q_standard[key] is not None else '-'
            else:
                result[key]['std'] = 0
    else:
        for key in load_dict.keys():
            result[key] = {}
            result[key]['name'] = key
            result[key]['auto'] = 0
            result[key]['actual'] = None
            if key in q_standard:
                result[key]['std'] = '-'

    return jsonify(result)


@bp.route('/ajax_record_inj_param', methods=['POST'])
def ajax_record_inj_param():
    data = request.get_data()
    data = json.loads(data)
    date = datetime.datetime.now()
    new_record = InjParamRecord(TIMESTAMP=date,
                                MACHINE_ID=data['machine_id'],
                                MOLD_ID=data['mold_id'],
                                part_number=data['part_number'],
                                NowTn2=data['NowTn2']['actual'],
                                NowT1=data['NowT1']['actual'],
                                NowT2=data['NowT2']['actual'],
                                NowT3=data['NowT3']['actual'],
                                NowT4=data['NowT4']['actual'],
                                ChrSpd3=data['ChrSpd3']['actual'],
                                ChrPrs3=data['ChrPrs3']['actual'],
                                ChrPos4=data['ChrPos4']['actual'],
                                ChrPos4_ChrPos3=data['ChrPos4']['actual'] - data['ChrPos3']['actual'],
                                InjPos0=data['InjPos0']['actual'],
                                InjPos1=data['InjPos1']['actual'],
                                InjPos2=data['InjPos2']['actual'],
                                InjPos3=data['InjPos3']['actual'],
                                InjPos4=data['InjPos4']['actual'],
                                InjSpd0=data['InjSpd0']['actual'],
                                InjSpd1=data['InjSpd1']['actual'],
                                InjSpd2=data['InjSpd2']['actual'],
                                InjSpd3=data['InjSpd3']['actual'],
                                InjSpd4=data['InjSpd4']['actual'],
                                InjPrs0=data['InjPrs0']['actual'],
                                InjPrs1=data['InjPrs1']['actual'],
                                InjPrs2=data['InjPrs2']['actual'],
                                InjPrs3=data['InjPrs3']['actual'],
                                InjPrs4=data['InjPrs4']['actual'],
                                TtimeInjP=data['TtimeInjP']['actual'],
                                HldPrs0=data['HldPrs0']['actual'],
                                HldPrs1=data['HldPrs1']['actual'],
                                HldPrs2=data['HldPrs2']['actual'],
                                HldPrs3=data['HldPrs3']['actual'],
                                HldTime0=data['HldTime0']['actual'],
                                HldTime1=data['HldTime1']['actual'],
                                HldTime2=data['HldTime2']['actual'],
                                HldTime3=data['HldTime3']['actual'],
                                TimeDchr=data['TimeDchr']['actual'],
                                # BFCSTTIME=data['BfCstTime']['actual'],
                                DryTemp=data['DryTemp']['actual'],
                                DryTime=data['DryTime']['actual'],
                                DewPoint=data['DewPoint']['actual'],
                                OilTemp=data['OilTemp']['actual'],
                                MoTnMale=data['MoTnMale']['actual'],
                                MoTnFemale=data['MoTnFemale']['actual'],
                                MoSlider=data['MoSlider']['actual'],
                                Plate=data['Plate']['actual'],
                                HtRunT1=data['HtRunT1']['actual'],
                                HtRunT2=data['HtRunT2']['actual'],
                                HtRunT3=data['HtRunT3']['actual'],
                                HtRunT4=data['HtRunT4']['actual'],
                                HtRunT5=data['HtRunT5']['actual'],
                                HtRunT6=data['HtRunT6']['actual'],
                                HtRunT7=data['HtRunT7']['actual'],
                                HtRunT8=data['HtRunT8']['actual'],
                                HtRunT9=data['HtRunT9']['actual'],
                                HtRunT10=data['HtRunT10']['actual'],
                                HtRunT11=data['HtRunT11']['actual'],
                                HtRunT12=data['HtRunT12']['actual'],
                                HtRunT13=data['HtRunT13']['actual'],
                                HtRunT14=data['HtRunT14']['actual'],
                                HtRunT15=data['HtRunT15']['actual']
                                )
    db_model1.add(new_record)
    db_model1.commit()
    q_record = InjParamRecord.query.filter(InjParamRecord.TIMESTAMP == date,
                                           InjParamRecord.MOLD_ID == data['mold_id'],
                                           InjParamRecord.part_number == data['part_number']).first()
    return jsonify({'form_no': q_record.id})


"""FOR 簽核功能"""
@bp.route('/ajax_get_inj_param_record', methods=['POST'])
def ajax_get_inj_param_record():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    result = {}
    q_param = InjParamRecord.query.filter(InjParamRecord.id == data['form_no']).first().to_dict()
    for key in q_param.keys():
        result[key] = {}
        result[key]['name'] = key
        result[key]['auto'] = 0
        result[key]['actual'] = float(q_param[key]) if isinstance(q_param[key], decimal.Decimal) else q_param[key]
        result[key]['std'] = 0

    print(q_param['MOLD_ID'])
    print(q_param['MACHINE_ID'])
    q_mold = MoldList.query.filter(MoldList.id == q_param['MOLD_ID']).first()
    q_machine = MachineList.query.filter(MachineList.id == q_param['MACHINE_ID']).first()
    result['mold_id'] = q_mold.id
    result['mold'] = q_mold.mold_number_f
    result['part_number'] = q_mold.mold_pn_association[0].pn_list.part_number
    result['machine_id'] = q_machine.id
    result['machine'] = q_machine.machine_name
    result['tonnage'] = q_machine.machine_tonnage
    result['building'] = q_machine.building
    return jsonify(result)


@bp.route('/inj_param_standard')
def inj_param_standard():
    return render_template('main/production/inj_param_standard.html')


@bp.route('/ajax_get_inj_param_standard', methods=['POST'])
def ajax_get_inj_param_standard():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    q_standard = InjParamStandard.query.filter(InjParamStandard.MOLD_ID == data['mold_id'],
                                               InjParamStandard.MACHINE_ID == data['machine_id'],
                                               InjParamStandard.flag == 1,
                                               InjParamStandard.part_number == data['part_number']) \
        .order_by(InjParamStandard.TIMESTAMP.desc()).first()

    if q_standard is None:
        date = datetime.datetime.now()
        new_standard = InjParamStandard(TIMESTAMP=date,
                                        MACHINE_ID=int(data['machine_id']),
                                        MOLD_ID=int(data['mold_id']),
                                        part_number=data['part_number'],
                                        flag=1)
        db_model1.add(new_standard)
        db_model1.commit()
        q_standard = InjParamStandard.query.filter(InjParamStandard.MOLD_ID == data['mold_id'],
                                                   InjParamStandard.MACHINE_ID == data['machine_id'],
                                                   InjParamStandard.part_number == data['part_number']) \
            .order_by(InjParamStandard.TIMESTAMP.desc()).first()
        q_standard = q_standard.to_dict()
        sign = '無簽核標準成型條件'
    else:
        q_standard = q_standard.to_dict()
        q_event = SignEvent.query.filter(SignEvent.table_list_id == 5, SignEvent.form_index == q_standard['id']).first()
        if q_event is not None:
            print(q_event.sign_process_list.sign_process_list_detail)
            sign_date = q_event
            q_event = q_event.sign_process_list.sign_process_list_detail
            sign = '已簽核'
            for i in q_event:
                sign = sign + '>>' + str(i.sign_order) + '.' + i.signer
            sign = sign + '------------有效日期: ' + str(sign_date.date.date()) + '~' + str((sign_date.date+datetime.timedelta(days=15)).date())
            print(sign)
        else:
            sign = '無簽核標準成型條件'
    result = {}
    for key in q_standard.keys():
        result[key] = {}
        result[key]['name'] = key
        result[key]['auto'] = 0
        result[key]['std'] = float(q_standard[key]) if isinstance(q_standard[key], decimal.Decimal) else q_standard[key]
    result['form_no'] = q_standard['id']
    result['sign'] = sign
    return jsonify(result)


@bp.route('/ajax_record_inj_param_standard', methods=['POST'])
def ajax_record_inj_param_standard():
    data = request.get_data()
    data = json.loads(data)
    date = datetime.datetime.now()
    new_standard = InjParamStandard(TIMESTAMP=date,
                                    MACHINE_ID=data['machine_id'],
                                    MOLD_ID=data['mold_id'],
                                    part_number=data['part_number'],
                                    flag=0,
                                    Tn2=data['Tn2']['std'],
                                    T1=data['T1']['std'],
                                    T2=data['T2']['std'],
                                    T3=data['T3']['std'],
                                    T4=data['T4']['std'],
                                    ChrSpd3=data['ChrSpd3']['std'],
                                    ChrPrs3=data['ChrPrs3']['std'],
                                    ChrPos4=data['ChrPos4']['std'],
                                    # ChrPos4_ChrPos3=data['ChrPos4']['std'] - data['ChrPos3']['std'],
                                    InjPos0=data['InjPos0']['std'],
                                    InjPos1=data['InjPos1']['std'],
                                    InjPos2=data['InjPos2']['std'],
                                    InjPos3=data['InjPos3']['std'],
                                    InjPos4=data['InjPos4']['std'],
                                    InjSpd0=data['InjSpd0']['std'],
                                    InjSpd1=data['InjSpd1']['std'],
                                    InjSpd2=data['InjSpd2']['std'],
                                    InjSpd3=data['InjSpd3']['std'],
                                    InjSpd4=data['InjSpd4']['std'],
                                    InjPrs0=data['InjPrs0']['std'],
                                    InjPrs1=data['InjPrs1']['std'],
                                    InjPrs2=data['InjPrs2']['std'],
                                    InjPrs3=data['InjPrs3']['std'],
                                    InjPrs4=data['InjPrs4']['std'],
                                    TtimeInjP=data['TtimeInjP']['std'],
                                    HldPrs0=data['HldPrs0']['std'],
                                    HldPrs1=data['HldPrs1']['std'],
                                    HldPrs2=data['HldPrs2']['std'],
                                    HldPrs3=data['HldPrs3']['std'],
                                    HldTime0=data['HldTime0']['std'],
                                    HldTime1=data['HldTime1']['std'],
                                    HldTime2=data['HldTime2']['std'],
                                    HldTime3=data['HldTime3']['std'],
                                    TimeDchr=data['TimeDchr']['std'],
                                    EjtPos3=data['EjtPos3']['std'],
                                    EjtSpd3=data['EjtSpd3']['std'],
                                    EjtPrs3=data['EjtPrs3']['std'],
                                    EjtPos0=data['EjtPos0']['std'],
                                    EjtSpd0=data['EjtSpd0']['std'],
                                    EjtPrs0=data['EjtPrs0']['std'],
                                    MopPos3=data['MopPos3']['std'],
                                    MopPrs3=data['MopPrs3']['std'],
                                    MclPos5=data['MclPos5']['std'],
                                    MclPos4=data['MclPos4']['std'],
                                    MclPrs4=data['MclPrs4']['std'],
                                    TimeLpr=data['TimeLpr']['std'],
                                    TimeDch=data['TimeDch']['std'],

                                    BfInjTime=data['BfInjTime']['std'],
                                    BfCstTime=data['BfCstTime']['std'],

                                    DryTemp=data['DryTemp']['std'],
                                    DryTime=data['DryTime']['std'],
                                    DewPoint=data['DewPoint']['std'],
                                    OilTemp=data['OilTemp']['std'],
                                    MoTnMale=data['MoTnMale']['std'],
                                    MoTnFemale=data['MoTnFemale']['std'],
                                    MoSlider=data['MoSlider']['std'],
                                    Plate=data['Plate']['std'],
                                    HtRunT1=data['HtRunT1']['std'],
                                    HtRunT2=data['HtRunT2']['std'],
                                    HtRunT3=data['HtRunT3']['std'],
                                    HtRunT4=data['HtRunT4']['std'],
                                    HtRunT5=data['HtRunT5']['std'],
                                    HtRunT6=data['HtRunT6']['std'],
                                    HtRunT7=data['HtRunT7']['std'],
                                    HtRunT8=data['HtRunT8']['std'],
                                    HtRunT9=data['HtRunT9']['std'],
                                    HtRunT10=data['HtRunT10']['std'],
                                    HtRunT11=data['HtRunT11']['std'],
                                    HtRunT12=data['HtRunT12']['std'],
                                    HtRunT13=data['HtRunT13']['std'],
                                    HtRunT14=data['HtRunT14']['std'],
                                    HtRunT15=data['HtRunT15']['std'],
                                    ClmFrc=data['ClmFrc']['std'],
                                    ProdWeight=data['ProdWeight']['std'],
                                    FeederWeight=data['FeederWeight']['std'],
                                    CnsmptPH=data['CnsmptPH']['std'],
                                    )
    db_model1.add(new_standard)
    db_model1.commit()
    q_standard = InjParamStandard.query.filter(InjParamStandard.TIMESTAMP == date,
                                               InjParamStandard.MOLD_ID == data['mold_id'],
                                               InjParamStandard.MACHINE_ID == data['machine_id'],
                                               InjParamStandard.part_number == data['part_number']).first()
    return jsonify({'form_no': q_standard.id})


@bp.route('/ajax_get_now_params', methods=['POST'])
def ajax_get_now_params():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    result = {}
    q_machine = Machine.query.filter(Machine.MachineName == data['machine'],
                                     Machine.BuildingNr == data['building']).first()
    q_param = InjParam.query.filter(InjParam.MachineId == q_machine.MachineId).first().to_dict()
    result['machine'] = q_param['MachineId']
    for key in q_param.keys():
        result[key] = {}
        result[key]['name'] = key
        result[key]['auto'] = 1
        result[key]['std'] = q_param[key]

    return jsonify(result)


@bp.route('/ajax_get_inj_param_standard_form', methods=['POST'])
def ajax_get_inj_param_standard_form():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    result = {}
    q_param = InjParamStandard.query.filter(InjParamStandard.id == data['form_no']).first().to_dict()
    result['form_no'] = q_param['id']
    for key in q_param.keys():
        result[key] = {}
        result[key]['name'] = key
        result[key]['auto'] = 0
        result[key]['std'] = float(q_param[key]) if isinstance(q_param[key], decimal.Decimal) else q_param[key]

    print(q_param['MOLD_ID'])
    print(q_param['MACHINE_ID'])
    q_mold = MoldList.query.filter(MoldList.id == q_param['MOLD_ID']).first()
    q_machine = MachineList.query.filter(MachineList.id == q_param['MACHINE_ID']).first()
    result['mold_id'] = q_mold.id
    result['mold'] = q_mold.mold_number_f
    result['part_number'] = q_param['part_number']
    result['machine_id'] = q_machine.id
    result['machine'] = q_machine.machine_name
    result['tonnage'] = q_machine.machine_tonnage
    result['building'] = q_machine.building
    return jsonify(result)


@bp.route('/ajax_confirm_new_standard_params', methods=['POST'])
def ajax_confirm_new_standard_params():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    form_no = data['form_no']

    q_standard = InjParamStandard.query.filter(InjParamStandard.id == form_no).first()
    q_standard.flag = 1
    q_old_standard = InjParamStandard.query.filter(InjParamStandard.MOLD_ID == q_standard.MOLD_ID, InjParamStandard.flag == 1).first()
    q_old_standard.flag = 0

    db_model1.add(q_standard)
    db_model1.add(q_old_standard)
    db_model1.commit()

    return jsonify()


@bp.route('/inj_param_record_query')
def inj_param_record_query():
    return render_template('main/production/inj_param_record_query.html')


@bp.route('/ajax_params_record_query', methods=['POST'])
def ajax_params_record_query():
    data = request.get_data()
    data = json.loads(data)
    print(data)
    # 時間段
    if 'time_range' in data.keys():
        time_range = data['time_range']
        begin_time = time_range[0:10]
        end_time = time_range[13:]
    else:
        # begin_time = datetime.date.today() + datetime.timedelta(days=-1)
        begin_time = datetime.date.today()
        end_time = datetime.date.today()
        begin_time = str(begin_time)
        end_time = str(end_time)
    q_machine = MachineList.query.filter(MachineList.building == data['building'],
                                         MachineList.machine_name == data['machine']).first()
    print(q_machine.id)
    q_record = InjParamRecord.query.filter(InjParamRecord.MOLD_ID == data['mold_id'],
                                           InjParamRecord.MACHINE_ID == q_machine.id,
                                           InjParamRecord.part_number == data['part_number'],
                                           InjParamRecord.TIMESTAMP >= datetime.datetime.strptime(begin_time, "%Y-%m-%d"),
                                           InjParamRecord.TIMESTAMP <= datetime.datetime.strptime(end_time, "%Y-%m-%d")+datetime.timedelta(days=1))\
        .order_by(InjParamRecord.TIMESTAMP.desc()).all()
    if not q_record:
        return '無數據', 404
    result = {}
    for key in q_record[0].to_dict():
        temp = []
        for record in q_record:
            records = record.to_dict()

            temp.append(float(records[key]) if isinstance(records[key], decimal.Decimal) else records[key])

        result[key] = temp
    temp_time = []
    for i in result['TIMESTAMP']:
        temp_time.append(i.strftime('%Y-%m-%d %H:%M:%S'))
    result['TIMESTAMP'] = temp_time

    q_mold = MoldList.query.filter(MoldList.id == data['mold_id']).first()
    q_machine_list = MachineList.query.filter(MachineList.id == data['machine_id']).first()
    q_pnlist = PNList.query.filter(PNList.part_number == data['part_number']).first()
    # print(q_machine_list.machine_type)
    # print(q_mold.mold_pn_association[0].pn_list.part_number)
    # print(q_mold.mold_pn_association[0].pn_list.pn_material_list[0].material_list.material_part_number)
    # print(q_mold.mold_pn_association[0].pn_list.pn_material_list[0].material_list.material_spec)
    result['machine_type'] = q_machine_list.machine_type
    result['machine_no'] = q_machine_list.machine_no
    result['part_number'] = data['part_number']
    assert len(q_pnlist.pn_material_list) == 1, '超過一款原料'
    result['material_part_number'] = q_pnlist.pn_material_list[0].material_list.material_spec
    result['material_spec'] = q_mold.mold_pn_association[0].pn_list.pn_material_list[0].material_list.material_spec
    return jsonify(result)
