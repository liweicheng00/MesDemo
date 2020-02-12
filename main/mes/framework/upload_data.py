from flask import (jsonify, render_template, request)
from flask_principal import Permission, RoleNeed
from main.mes.framework import bp
from main.model import *
from flask_login import login_user, logout_user, login_required
import json
admin_permission = Permission(RoleNeed('super'))
user_permission = Permission(RoleNeed('user'))


@bp.route('/upload_data')
def upload_data():
    return render_template('main/framework/upload_data.html')


@bp.route('/ajax_data_upload', methods=['POST'])
@login_required
@admin_permission.require()
@user_permission.require()
def ajax_data_upload():
    data = request.get_data()
    data = json.loads(data)
    upload_table = data['upload_table']
    data = data['data']
    if upload_table == 'Bom':

        # print('product id:', product_id)
        for dta in data:
            # print(dta)
            column = ['honhai_pn', 'product_name', 'product_code', 'part_number', 'inj_product_name', 'product_name_en',
                      'std_produce', 'std_cycle_time', 'piece', 'material_part_number', 'material_weight', 'material_type',
                      'material_spec', 'color_number', 'color', 'material_vendor']
            for col in column:
                print(col)
                if not (col in dta.keys()):
                    print(dta.keys())
                    return jsonify([{'state': '1', 'error': 'Bom 欄位不正確'}])
            honhai_pn = dta['honhai_pn']
            product_name = dta['product_name']
            product_code = dta['product_code']
            q_product = ProductList.query.filter(ProductList.honhai_pn == honhai_pn).first()
            if q_product is None:
                try:
                    new_product = ProductList(honhai_pn=honhai_pn, product_name=product_name, product_code=product_code)
                    db_session.add(new_product)
                    db_session.commit()
                except:
                    print('Failed to create new product in table [product_list].')
                    db_session.remove()
                else:
                    q_product = ProductList.query.filter(ProductList.honhai_pn == honhai_pn).first()

            q_product.honhai_pn = honhai_pn
            q_product.product_name = product_name
            q_product.product_code = product_code
            db_session.add(q_product)
            db_session.commit()

            product_id = q_product.id

            part_number = dta['part_number']
            inj_product_name = dta['inj_product_name']
            product_name_en = dta['product_name_en']
            piece = int(dta['piece']) if dta['piece'] != '' else None
            std_produce = float(dta['std_produce']) if dta['std_produce'] != '' else None
            std_cycle_time = float(dta['std_cycle_time']) if dta['std_cycle_time'] != '' else None

            q_pnlist = PNList.query.filter(PNList.part_number == part_number).first()
            if q_pnlist is None:
                try:
                    new_pnlist = PNList(part_number=part_number, inj_product_name=inj_product_name,
                                        product_name_en=product_name_en, std_produce=float(std_produce),
                                        std_cycle_time=float(std_cycle_time), piece=piece)
                    db_session.add(new_pnlist)
                    db_session.commit()
                    print('create new pnlist seccess')
                except:
                    print('Failed to create new pnlist in table [pn_list].')
                else:
                    q_pnlist = PNList.query.filter(PNList.part_number == part_number).first()
            q_pnlist.part_number = part_number
            q_pnlist.inj_product_name = inj_product_name
            q_pnlist.product_name_en = product_name_en
            q_pnlist.std_produce = std_produce
            q_pnlist.std_cycle_time = std_cycle_time
            q_pnlist.piece = piece
            db_session.add(q_pnlist)
            db_session.commit()

            pnlist_id = q_pnlist.id
            # print('pnlist id:', pnlist_id)

            material_part_number = dta['material_part_number']
            material_type = dta['material_type']
            material_spec = dta['material_spec']
            color_number = dta['color_number']
            color = dta['color']
            material_vendor = dta['material_vendor']
            q_material = MaterialList.query.filter(MaterialList.material_part_number == material_part_number).first()
            if q_material is None:
                try:
                    new_material = MaterialList(material_part_number=material_part_number, material_type=material_type,
                                                material_spec=material_spec, color_number=color_number, color=color,
                                                material_vendor=material_vendor)
                    db_session.add(new_material)
                    db_session.commit()
                    print('create new material seccess')
                except:
                    print('Failed to create new material in table [material_list].')
                else:
                    q_material = MaterialList.query.filter(
                        MaterialList.material_part_number == material_part_number).first()

            q_material.material_type = material_type
            q_material.material_spec = material_spec
            q_material.color_number = color_number
            q_material.color = color
            q_material.material_vendor = material_vendor
            db_session.add(q_material)
            db_session.commit()

            material_id = q_material.id
            # print('material id:', material_id)

            material_weight = dta['material_weight']
            q_pn_material = PNMaterialList.query.filter(PNMaterialList.pnlist_id == pnlist_id,
                                                        PNMaterialList.material_id == material_id).first()
            if q_pn_material is None:
                try:
                    new_pn_material = PNMaterialList(pnlist_id=pnlist_id, material_id=material_id,
                                                     material_weight=float(material_weight))
                    db_session.add(new_pn_material)
                    db_session.commit()
                except:
                    print('Failed to create new pn material in table [pn_material_list].')
                    db_session.remove()
                else:
                    q_pn_material = PNMaterialList.query.filter(PNMaterialList.pnlist_id == pnlist_id,
                                                                PNMaterialList.material_id == material_id).first()

            q_pn_material.pnlist_id = pnlist_id
            q_pn_material.material_id = material_id
            q_pn_material.material_weight = float(material_weight)
            db_session.add(q_pn_material)
            db_session.commit()
            pn_material_id = q_pn_material.id
            # print('pn_material id:', pn_material_id)

            q_bom = Bom.query.filter(Bom.product_id == product_id, Bom.pnlist_id == pnlist_id).first()
            if q_bom is None:
                try:
                    new_bom = Bom(product_id=product_id, pnlist_id=pnlist_id)
                    db_session.add(new_bom)
                    db_session.commit()
                except:
                    print('Failed to create new bom in table [Bom].')
                    db_session.remove()
                else:
                    q_bom = Bom.query.filter(Bom.product_id == product_id, Bom.pnlist_id == pnlist_id).first()
            q_bom.product_id = product_id
            q_bom.pnlist_id = pnlist_id
            db_session.add(q_bom)
            db_session.commit()

        # print(q_bom.__dict__)
        # print(q_bom.pn_list.__dict__)
        # print(q_bom.product_list.__dict__)
        # print(type(q_bom.pn_list.pn_material_list[0].__dict__['material_weight']))
        # print(q_bom.pn_list.pn_material_list[0].material_list.__dict__)

    elif upload_table == 'MachineList':
        column = ['building', 'machine', 'machine_name', 'machine_code', 'machine_tonnage', 'machine_type',
                  'machine_brand', 'machine_no', 'machine_location']
        for col in column:
            if not (col in data[0].keys()):
                return jsonify([{'state': '1', 'error': '機台列表 欄位不正確'}])
        for dta in data:
            # print(dta)
            building = dta['building']
            machine_name = dta['machine_name']
            machine_code = dta['machine_code']
            machine = dta['machine']
            machine_type = dta['machine_type']
            machine_brand = dta['machine_brand']
            machine_no = dta['machine_no']
            machine_location = dta['machine_location']
            machine_tonnage = dta['machine_tonnage']
            q_machine = MachineList.query.filter(MachineList.machine_code == machine_code).first()
            if q_machine is None:
                try:
                    new_machine = MachineList(building=building, machine_name=machine_name, machine_code=machine_code,
                                              machine=machine, machine_type=machine_type, machine_brand=machine_brand,
                                              machine_no=machine_no, machine_location=machine_location,
                                              machine_tonnage=machine_tonnage)
                    db_session.add(new_machine)
                    db_session.commit()
                    print('create new machine seccess')
                except:
                    print('Failed to create new machine in table [machine_list].')
                    db_session.remove()
                else:
                    q_machine = MachineList.query.filter(MachineList.machine_code == machine_code).first()
            q_machine.building = building
            q_machine.machine_name = machine_name
            q_machine.machine_code = machine_code
            q_machine.machine = machine
            q_machine.machine_tonnage = machine_tonnage
            q_machine.machine_type = machine_type
            q_machine.machine_brand = machine_brand
            q_machine.machine_no = machine_no
            q_machine.machine_location = machine_location
            db_session.add(q_machine)
            db_session.commit()

        pass
    elif upload_table == 'MoldPnAssociation':
        column = ['part_number', 'ejection_mode', 'mold_number', 'mold_number_f', 'cave_number']
        for col in column:
            if not (col in data[0].keys()):
                return jsonify([{'state': '1', 'error': '模具-料號對照表 欄位不正確'}])
        for dta in data:
            # print(dta)
            mold_number = dta['mold_number']
            mold_number_f = dta['mold_number_f']
            cave_number = dta['cave_number']
            ejection_mode = dta['ejection_mode']
            part_number = dta['part_number']
            q_mold = MoldList.query.filter(MoldList.mold_number == mold_number).first()
            if q_mold is None:
                try:
                    new_mold = MoldList(mold_number=mold_number, mold_number_f=mold_number_f, cave_number=cave_number,
                                        ejection_mode=ejection_mode)
                    db_session.add(new_mold)
                    db_session.commit()
                    print('create new mold seccess')
                except:
                    print('Failed to create new mold in table [mold_list].')
                    db_session.remove()
                else:
                    q_mold = MoldList.query.filter(MoldList.mold_number == mold_number).first()
            q_mold.mold_number = mold_number
            q_mold.mold_number_f = mold_number_f
            q_mold.cave_number = cave_number
            q_mold.ejection_mode = ejection_mode
            db_session.add(q_mold)
            db_session.commit()

            mold_id = q_mold.id
            q_pnlist = PNList.query.filter(PNList.part_number == part_number).first()

            if q_pnlist is None:
                continue
            else:
                pnlist_id = q_pnlist.id
            q_mold_pn = MoldPnAssociation.query.filter(MoldPnAssociation.pnlist_id == pnlist_id,
                                                       MoldPnAssociation.mold_id == mold_id).first()
            if q_mold_pn is None:
                try:
                    new_mold_pn = MoldPnAssociation(pnlist_id=pnlist_id, mold_id=mold_id)
                    db_session.add(new_mold_pn)
                    db_session.commit()
                except:
                    print('Failed to create new mold_pn in table [mold_pn_association].')
                    db_session.remove()
                else:
                    q_mold_pn = MoldPnAssociation.query.filter(MoldPnAssociation.pnlist_id == pnlist_id,
                                                               MoldPnAssociation.mold_id == mold_id).first()
            q_mold_pn.mold_id = mold_id
            q_mold_pn.pnlist_id = pnlist_id
            db_session.add(q_mold_pn)
            db_session.commit()

        # q_pnlist = PNList.query.filter(PNList.id == 14).first()
        # print(q_pnlist.__dict__)
        # print(q_pnlist.mold_list)
        # print(q_pnlist.mold_pn_association)
        # print(q_mold_pn.mold_list.__dict__)
        # print(q_mold_pn.pn_list.pn_material_list)
        # print(q_mold_pn.pn_list.pn_material_list[0].material_list.__dict__)
        # print(q_mold_pn.pn_list.bom)
        # print(q_mold_pn.pn_list.bom[0].product_list.__dict__)
        pass
    elif upload_table == 'Anomaly':
        # column = ['part_number', 'ejection_mode', 'mold_number', 'mold_number_f', 'cave_number']
        # for col in column:
        #     if not (col in data[0].keys()):
        #         return jsonify([{'state': '1', 'error': '模具-料號對照表 欄位不正確'}])
        for dta in data:
            # print(dta)
            anomaly_name = dta['anomaly_name']
            anomaly_code = dta['anomaly_code']
            anomaly_type_code = dta['anomaly_type_code']
            q_anomaly_type = AnomalyTypeList.query.filter(
                AnomalyTypeList.anomaly_type_code == anomaly_type_code).first()
            anomaly_type_id = q_anomaly_type.id
            db_session.add(AnomalyList(anomaly_type_id=anomaly_type_id, anomaly_name=anomaly_name,
                                       anomaly_code=anomaly_code))
        db_session.commit()

    return jsonify([{'state': '0', 'error': ''}])  # Return json object to make ajax success.
