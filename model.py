from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, Date, Text, Numeric, Float, \
    DateTime, REAL, or_, and_, func
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from sqlalchemy.schema import Sequence
import os
# from __init__ import app_config
url = os.environ.get('DATABASE_URL')
if url is not None:
    url = url.split('postgres://')[1]
    SQLALCHEMY_URL = 'postgresql+psycopg2://{}'.format(url)
else:
    SQLALCHEMY_URL = "postgresql://liweicheng:@127.0.0.1:5432/demo-mes"

engine = create_engine(SQLALCHEMY_URL, convert_unicode=True, encoding='utf8')

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
# postgresql+psycopg2://user:password@host:port/dbname[?key=value&key=value...]


association_table = Table(
    'user_role_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('role_id', Integer, ForeignKey('role.id'))
)


class TestTable(Base):
    __tablename__ = 'test_table'
    username = Column(String(80), unique=True, nullable=False,  primary_key=True)
    password = Column(String(120), unique=True, nullable=False)
    name = Column(String(20), unique=False, nullable=False)


class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), unique=True, nullable=False)
    name = Column(String(20), unique=False, nullable=False)
    role = relationship('Role', secondary=association_table)  # N>>N

    def to_dict(self):
        """將數據轉為字典"""
        dictionary = self.__dict__
        if "_sa_instance_state" in dictionary:
            del dictionary["_sa_instance_state"]
        return dictionary

    def __repr__(self):
        """讓print這個物件的時候，看起來好看"""
        return '<User %r>' % self.username


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, Sequence('role_id_seq'), primary_key=True)
    role = Column(String(80), unique=True, nullable=False)
    chi_name = Column(String(80), unique=False, nullable=True)

    def to_dict(self):
        """將數據轉為字典"""
        dictionary = self.__dict__
        if "_sa_instance_state" in dictionary:
            del dictionary["_sa_instance_state"]
        return dictionary

    def __repr__(self):
        """讓print這個物件的時候，看起來好看"""
        return '<Role %r>' % self.role


class BuildingList(Base):
    __tablename__ = 'building_list'
    id = Column(Integer, Sequence('building_list_id_seq'), primary_key=True)
    building = Column(String(80), unique=False, nullable=False)


class ProductList(Base):
    __tablename__ = 'product_list'
    id = Column(Integer, Sequence('product_list_id_seq'), primary_key=True)
    honhai_pn = Column(String(80), unique=True, nullable=False)
    product_code = Column(String(80), unique=False, nullable=False)
    product_name = Column(String(80), unique=True, nullable=False)
    ps = Column(Text, unique=False, nullable=True)


class MaterialList(Base):
    __tablename__ = 'material_list'
    id = Column(Integer, Sequence('material_list_id_seq'), primary_key=True)
    material_part_number = Column(String(80), unique=True, nullable=False)
    material_type = Column(String(80), unique=False, nullable=True)
    material_spec = Column(String(80), unique=False, nullable=True)
    color_number = Column(String(80), unique=False, nullable=True)
    color = Column(String(80), unique=False, nullable=True)
    material_vendor = Column(String(80), unique=False, nullable=True)
    alm_state = Column(Integer, unique=False, nullable=True)
    ps = Column(Text, unique=False, nullable=True)


class MachineList(Base):
    __tablename__ = 'machine_list'
    id = Column(Integer, Sequence('machine_list_id_seq'), primary_key=True)
    building = Column(String(80), unique=False, nullable=True)
    machine_name = Column(String(80), unique=True, nullable=False)
    machine_code = Column(String(80), unique=True, nullable=False)
    machine = Column(String(80), unique=False, nullable=True)
    machine_type = Column(String(80), unique=False, nullable=True)
    machine_tonnage = Column(String(80), unique=False, nullable=True)
    machine_brand = Column(String(80), unique=False, nullable=True)
    machine_no = Column(String(80), unique=False, nullable=True)
    machine_location = Column(String(80), unique=False, nullable=True)
    machine_state = Column(Integer, unique=False, nullable=True)
    ps = Column(Text, unique=False, nullable=True)


class MoldList(Base):
    __tablename__ = 'mold_list'
    id = Column(Integer, Sequence('mold_list_id_seq'), primary_key=True)
    mold_number = Column(String(80), unique=True, nullable=False)
    mold_number_f = Column(String(80), unique=False, nullable=False)
    cave_number = Column(Integer, unique=False, nullable=False)
    ejection_mode = Column(String(80), unique=False, nullable=True)
    mold_state = Column(Integer, unique=False, nullable=True)
    ps = Column(Text, unique=False, nullable=True)


class PNList(Base):
    __tablename__ = 'pn_list'
    id = Column(Integer, Sequence('pn_list_id_seq'), primary_key=True)
    part_number = Column(String(80), unique=True, nullable=False)
    inj_product_name = Column(String(80), unique=False, nullable=False)
    product_name_en = Column(String(80), unique=False, nullable=False)
    std_produce = Column(Float, unique=False, nullable=False)
    std_cycle_time = Column(Float, unique=False, nullable=False)
    ps = Column(Text, unique=False, nullable=True)
    piece = Column(Integer, unique=False, nullable=True)


class Bom(Base):
    __tablename__ = 'bom'
    id = Column(Integer, Sequence('bom_id_seq'), primary_key=True)
    product_id = Column(Integer, ForeignKey('product_list.id'))
    product_list = relationship('ProductList', backref="bom")
    pnlist_id = Column(Integer, ForeignKey('pn_list.id'))
    pn_list = relationship('PNList', backref="bom")
    ps = Column(Text, unique=False, nullable=True)
    available = Column(String(80), unique=False, nullable=True)


class PNMaterialList(Base):
    __tablename__ = 'pn_material_list'
    id = Column(Integer, Sequence('pn_material_list_id_seq'), primary_key=True)
    pnlist_id = Column(Integer, ForeignKey('pn_list.id'))
    pn_list = relationship('PNList', backref="pn_material_list")
    material_id = Column(Integer, ForeignKey('material_list.id'))
    material_list = relationship('MaterialList', backref="pn_material_list")
    material_weight = Column(Numeric, unique=False, nullable=True)
    ps = Column(Text, unique=False, nullable=True)


class ProduceSchedule(Base):
    __tablename__ = 'produce_schedule'
    id = Column(Integer, Sequence('produce_schedule_id_seq'), primary_key=True)
    date = Column(Date, unique=False, nullable=False)
    machine_id = Column(Integer, ForeignKey('machine_list.id'))
    machine_list = relationship('MachineList', backref="produce_schedule")
    mold_id = Column(Integer, ForeignKey('mold_list.id'))
    mold_list = relationship('MoldList', backref="produce_schedule")
    pnlist_id = Column(Integer, ForeignKey('pn_list.id'))
    pn_list = relationship('PNList', backref="produce_schedule")
    amount = Column(Float, unique=False, nullable=False)
    product_name = Column(String(80), unique=False, nullable=True)
    produce_order = Column(String(80), unique=False, nullable=True)
    version = Column(String(80), unique=False, nullable=True)
    ps = Column(Text, unique=False, nullable=True)


class MoldPnAssociation(Base):
    __tablename__ = 'mold_pn_association'
    id = Column(Integer, Sequence('mold_pn_association_id_seq'), primary_key=True)
    mold_id = Column(Integer, ForeignKey('mold_list.id'))
    pnlist_id = Column(Integer, ForeignKey('pn_list.id'))
    mold_list = relationship('MoldList', backref="mold_pn_association")
    pn_list = relationship('PNList', backref="mold_pn_association")
    ps = Column(Text, unique=False, nullable=True)


class Amount(Base):
    __tablename__ = "amount"
    machine_id = Column(Integer, primary_key=True, unique=False, nullable=True)
    produce_amount = Column(Integer, unique=False, nullable=True)
    state = Column(Integer, unique=False, nullable=True)
    update_time = Column(DateTime, unique=False, nullable=True)


class DailyReport(Base):
    __tablename__ = 'daily_report'
    id = Column(Integer, Sequence('daily_report_id_seq'), primary_key=True)
    date = Column(Date, unique=False, nullable=False)
    building = Column(String(20), unique=False, nullable=False)
    machine = Column(String(20), unique=False, nullable=False)
    machine_id = Column(Integer, unique=False, nullable=True)
    part_number = Column(String(20), unique=False, nullable=False)
    mold = Column(String(20), unique=False, nullable=True)
    mold_id = Column(Integer, unique=False, nullable=True)
    produce_amount = Column(Integer, unique=False, nullable=True)
    bad_amount = Column(Integer, unique=False, nullable=True)
    bad_percent = Column(Float, unique=False, nullable=True)
    bad_ppm = Column(Integer, unique=False, nullable=True)
    lost_time = Column(Float, unique=False, nullable=True)
    real_cycle_time = Column(Float, unique=False, nullable=True)
    record_state = Column(Integer, unique=False, nullable=True)
    additional_amount = Column(Integer, unique=False, nullable=True)


class BadList(Base):
    __tablename__ = 'bad_list'
    id = Column(Integer, Sequence('bad_list_id_seq'), primary_key=True)
    bad_name = Column(String(20), unique=True, nullable=False)
    bad_code = Column(String(20), unique=True, nullable=False)
    ps = Column(Text, unique=False, nullable=True)


class AnomalyList(Base):
    __tablename__ = 'anomaly_list'
    id = Column(Integer, Sequence('anomaly_list_id_seq'), primary_key=True)
    anomaly_type_id = Column(Integer, ForeignKey('anomaly_type_list.id'))
    anomaly_type_list = relationship('AnomalyTypeList', backref="anomaly_list")
    anomaly_name = Column(String(20), unique=False, nullable=False)
    anomaly_code = Column(String(20), unique=True, nullable=False)
    ps = Column(Text, unique=False, nullable=True)


class AnomalyTypeList(Base):
    __tablename__ = 'anomaly_type_list'
    id = Column(Integer, Sequence('anomaly_type_list_id_seq'), primary_key=True)
    anomaly_type = Column(String(20), unique=False, nullable=False)
    anomaly_type_code = Column(String(20), unique=True, nullable=False)
    ps = Column(Text, unique=False, nullable=True)


class BadRecord(Base):
    __tablename__ = 'bad_record'
    id = Column(Integer, Sequence('bad_record_id_seq'), primary_key=True)
    daily_report_id = Column(Integer, ForeignKey('daily_report.id'))
    daily_report = relationship('DailyReport', backref="bad_record")
    bad_id = Column(Integer, ForeignKey('bad_list.id'))
    bad_list = relationship('BadList', backref="bad_record")
    record_time = Column(DateTime, unique=False, nullable=False)
    cause = Column(Text, unique=False, nullable=True)
    improve = Column(Text, unique=False, nullable=True)
    responsible = Column(String(20), unique=False, nullable=True)
    finish_date = Column(DateTime, unique=False, nullable=True)
    ps = Column(Text, unique=False, nullable=True)


class AnomalyRecord(Base):
    __tablename__ = 'anomaly_record'
    id = Column(Integer, Sequence('anomaly_record_id_seq'), primary_key=True)
    daily_report_id = Column(Integer, ForeignKey('daily_report.id'))
    daily_report = relationship('DailyReport', backref="anomaly_record")
    anomaly_id = Column(Integer, ForeignKey('anomaly_list.id'))
    anomaly_list = relationship('AnomalyList', backref="anomaly_record")
    begin_time = Column(DateTime, unique=False, nullable=False)
    end_time = Column(DateTime, unique=False, nullable=False)
    lost_time = Column(Float, unique=False, nullable=False)
    improve = Column(Text, unique=False, nullable=True)
    responsible = Column(String(20), unique=False, nullable=True)
    finish_date = Column(Date, unique=False, nullable=True)
    ps = Column(Text, unique=False, nullable=True)


class MaterialDispatch(Base):
    __tablename__ = 'material_dispatch'
    id = Column(Integer, Sequence('material_dispatch_id_seq'), primary_key=True)
    date = Column(Date, unique=False, nullable=False)
    building = Column(String(20), unique=False, nullable=True)
    pnlist_id = Column(Integer, ForeignKey('pn_list.id'))
    pn_list = relationship('PNList', backref="material_dispatch")
    material_id = Column(Integer, ForeignKey('material_list.id'))
    material_list = relationship('MaterialList', backref="material_dispatch")
    demand_weight = Column(Float, unique=False, nullable=True)
    remain_weight = Column(Float, unique=False, nullable=True)
    dispatch_weight = Column(Float, unique=False, nullable=True)
    get_weight = Column(Float, unique=False, nullable=True)
    state = Column(Integer, unique=False, nullable=True)

    def to_dict(self):
        """將數據轉為字典"""
        dictionary = self.__dict__
        if "_sa_instance_state" in dictionary:
            del dictionary["_sa_instance_state"]
        return dictionary


class MaterialCheck(Base):
    __tablename__ = 'material_check'
    id = Column(Integer, Sequence('material_check_id_seq'), primary_key=True)
    date = Column(Date, unique=False, nullable=False)
    building = Column(String(20), unique=False, nullable=False)
    material_id = Column(Integer, ForeignKey('material_list.id'))
    material_list = relationship('MaterialList', backref="material_check")
    get_amount = Column(Integer, unique=False, nullable=False)
    feeding_bucket = Column(Integer, unique=False, nullable=False)
    dry_bucket = Column(Integer, unique=False, nullable=False)
    material_bucket = Column(Integer, unique=False, nullable=False)
    total = Column(Integer, unique=False, nullable=False)


class SignTableList(Base):
    __tablename__ = 'sign_table_list'
    id = Column(Integer, Sequence('sign_table_list_id_seq'), primary_key=True)
    table_name = Column(String(80), unique=True, nullable=False)
    db_table_name = Column(String(80), unique=True, nullable=False)
    name = Column(String(80), unique=True, nullable=True)


class SignProcessList(Base):
    __tablename__ = 'sign_process_list'
    id = Column(Integer, Sequence('sign_process_list_id_seq'), primary_key=True)
    table_list_id = Column(Integer, ForeignKey('sign_table_list.id'))
    sign_table_list = relationship('SignTableList', backref="sign_process_list")
    process_name = Column(String(20), unique=False, nullable=True)


class SignProcessListDetail(Base):
    __tablename__ = 'sign_process_list_detail'
    id = Column(Integer, Sequence('sign_process_list_detail_id_seq'), primary_key=True)
    process_list_id = Column(Integer, ForeignKey('sign_process_list.id'))
    sign_process_list = relationship('SignProcessList', backref="sign_process_list_detail")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', backref="sign_process_list_detail")
    signer = Column(String(20), unique=False, nullable=False)
    sign_order = Column(Integer, unique=False, nullable=False)


class SignEvent(Base):
    __tablename__ = 'sign_event'
    id = Column(Integer, Sequence('sign_event_id_seq'), primary_key=True)
    date = Column(DateTime, unique=False, nullable=False)
    table_list_id = Column(Integer, ForeignKey('sign_table_list.id'))
    sign_table_list = relationship('SignTableList', backref="sign_event")
    process_name_id = Column(Integer, ForeignKey('sign_process_list.id'))
    sign_process_list = relationship('SignProcessList', backref="sign_event")
    sign_state = Column(Integer, unique=False, nullable=False)
    form_index = Column(String(20), unique=False, nullable=True)
    initiator = Column(String(20), unique=False, nullable=True)
    initiator_id = Column(Integer, unique=False, nullable=True)


class SignerState(Base):
    __tablename__ = 'signer_state'
    id = Column(Integer, Sequence('signer_state_id_seq'), primary_key=True)
    event_id = Column(Integer, ForeignKey('sign_event.id'))
    sign_event = relationship('SignEvent', backref="signer_state")
    process_list_detail_id = Column(Integer, ForeignKey('sign_process_list_detail.id'))
    process_list_detail = relationship('SignProcessListDetail', backref="signer_state")
    signer = Column(String(20), unique=False, nullable=False)
    signer_order = Column(Integer, unique=False, nullable=False)
    signer_state = Column(Integer, unique=False, nullable=False)
    sign_date = Column(DateTime, unique=False, nullable=False)
    flag = Column(Numeric, unique=False, nullable=False)
    ps = Column(Text, unique=False, nullable=True)


class BadCause(Base):
    __tablename__ = 'bad_cause'
    id_seq = Sequence('id_bad_cause', metadata=Base.metadata, cache=2)
    id = Column(Integer, id_seq, primary_key=True)
    week = Column(Integer, unique=False, nullable=False)
    inj_part_number = Column(String(80), unique=False, nullable=False)
    bad_name = Column(String(80), unique=False, nullable=False)
    ppm = Column(Integer, unique=False, nullable=False)
    pics = Column(Integer, unique=False, nullable=False)
    cause = Column(Text, unique=False, nullable=False)
    improvement = Column(Text, unique=False, nullable=False)
    finish_date = Column(String(80), unique=False, nullable=False)
    response = Column(String(80), unique=False, nullable=False)


class BackendDemand(Base):
    __tablename__ = 'backend_demand'
    id = Column(Integer, Sequence('backend_demand_id_seq'), primary_key=True)
    date = Column(Date, unique=False, nullable=False)
    product_name = Column(String(80), unique=False, nullable=True)
    part_number = Column(String(80), unique=False, nullable=True)
    demand_amount = Column(Integer, unique=False, nullable=True)
    open_num = Column(Integer, unique=False, nullable=True)
    revise_amount = Column(Integer, unique=False, nullable=True)
    revise_open_num = Column(Integer, unique=False, nullable=True)
    scheduled_num = Column(Integer, unique=False, nullable=True)
    state = Column(Integer, unique=False, nullable=True)
    ps = Column(Text, unique=False, nullable=True)


class FirstPartRecord(Base):
    __tablename__ = 'first_part_record'
    id = Column(Integer, Sequence('first_part_record_id_seq'), primary_key=True)
    send_time = Column(DateTime, unique=False, nullable=False)
    finish_time = Column(DateTime, unique=False, nullable=True)
    pnlist_id = Column(Integer, unique=False, nullable=False)
    part_number = Column(String(80), unique=False, nullable=False)
    machine_id = Column(Integer, unique=False, nullable=False)
    machine_name = Column(String(80), unique=False, nullable=False)
    mold_id = Column(Integer, unique=False, nullable=False)
    mold_number = Column(String(80), unique=False, nullable=False)
    mold_number_f = Column(String(80), unique=False, nullable=False)
    material_id = Column(Integer, unique=False, nullable=True)
    material_part_number = Column(String(80), unique=False, nullable=True)
    grn_no = Column(String(80), unique=False, nullable=True)
    batch_number = Column(String(80), unique=False, nullable=True)
    examine_dependence = Column(String(80), unique=False, nullable=True)
    type = Column(String(80), unique=False, nullable=True)
    type_id = Column(Integer, unique=False, nullable=True)
    all_determination = Column(String(80), unique=False, nullable=True)
    dimension_id = Column(Integer, unique=False, nullable=True)
    ps = Column(Text, unique=False, nullable=True)
    building = Column(String(80), unique=False, nullable=True)
    dimension_state = Column(Integer, unique=False, nullable=True)
    examine_state = Column(Integer, unique=False, nullable=True)

    def to_dict(self):
        """將數據轉為字典"""
        dictionary = self.__dict__
        if "_sa_instance_state" in dictionary:
            del dictionary["_sa_instance_state"]
        if "send_time" in dictionary:
            try:
                dictionary["send_time"] = dictionary["send_time"].strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
            else:
                pass
        if "finish_time" in dictionary:
            try:
                dictionary["finish_time"] = dictionary["finish_time"].strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
            else:
                pass
        return dictionary


class Dimension(Base):
    __tablename__ = 'dimension'
    id = Column(Integer, Sequence('dimension_id_seq'), primary_key=True)
    mold_id = Column(Integer, unique=False, nullable=True)
    pnlist_id = Column(Integer, unique=False, nullable=False)
    dim = Column(Integer, unique=False, nullable=False)
    dim_name = Column(String(80), unique=False, nullable=True)
    measure_tool = Column(String(80), unique=False, nullable=True)
    upper_limit = Column(Float, unique=False, nullable=True)
    lower_limit = Column(Float, unique=False, nullable=True)


class DimensionRecord(Base):
    __tablename__ = 'dimension_record'
    id = Column(Integer, Sequence('dimension_record_id_seq'), primary_key=True)
    cave_number = Column(Integer, unique=False, nullable=False)
    first_part_id = Column(Integer, unique=False, nullable=False)
    dimension_id = Column(Integer, unique=False, nullable=False)
    measure_data = Column(Float, unique=False, nullable=True)
    determination = Column(String(80), unique=False, nullable=True)
    ng = Column(Integer, unique=False, nullable=False)


class ExamineRecord(Base):
    __tablename__ = 'examine_record'
    id = Column(Integer, Sequence('examine_record_id_seq'), primary_key=True)
    cave_number = Column(Integer, unique=False, nullable=False)
    first_part_id = Column(Integer, unique=False, nullable=False)
    examine_1 = Column(Integer, unique=False, nullable=True)
    examine_2 = Column(Integer, unique=False, nullable=True)
    examine_3 = Column(Integer, unique=False, nullable=True)
    examine_4 = Column(Integer, unique=False, nullable=True)
    examine_5 = Column(Integer, unique=False, nullable=True)
    examine_6 = Column(Integer, unique=False, nullable=True)
    examine_7 = Column(Integer, unique=False, nullable=True)
    examine_8 = Column(Integer, unique=False, nullable=True)
    examine_9 = Column(Integer, unique=False, nullable=True)
    examine_10 = Column(Integer, unique=False, nullable=True)
    examine_11 = Column(Integer, unique=False, nullable=True)
    examine_12 = Column(Integer, unique=False, nullable=True)
    examine_13 = Column(Integer, unique=False, nullable=True)
    examine_14 = Column(Integer, unique=False, nullable=True)
    examine_15 = Column(Integer, unique=False, nullable=True)
    examine_16 = Column(Integer, unique=False, nullable=True)
    examine_17 = Column(Integer, unique=False, nullable=True)
    examine_18 = Column(Integer, unique=False, nullable=True)
    examine_19 = Column(Integer, unique=False, nullable=True)
    determination = Column(String(80), unique=False, nullable=True)

    def to_dict(self):
        """將數據轉為字典"""
        dictionary = self.__dict__
        if "_sa_instance_state" in dictionary:
            del dictionary["_sa_instance_state"]
        return dictionary


class AuthManager(Base):
    __tablename__ = 'auth_manager'
    id_seq = Sequence('auth_manager_id_seq', metadata=Base.metadata)
    id = Column(Integer, id_seq, primary_key=True)
    route_name = Column(String(80), unique=True, nullable=True)
    permission = Column(String(80), unique=False, nullable=True)
    page_url = Column(String(80), unique=True, nullable=True)
    num = Column(Integer, unique=True, nullable=True)
    func_name = Column(String(80), unique=True, nullable=True)

    def to_dict(self):
        """將數據轉為字典"""
        dictionary = self.__dict__
        if "_sa_instance_state" in dictionary:
            del dictionary["_sa_instance_state"]
        return dictionary


# Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    print('Initialize database.')
