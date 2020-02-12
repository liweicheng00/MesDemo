from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, func
import datetime

engine = create_engine('mssql+pymssql://sa:1234@10.194.184.167/PisWeb', echo=False)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class Machine(Base):
    __tablename__ = 'Machine'
    MachineId = Column(Integer, primary_key=True)
    MachineName = Column(String(80), primary_key=False)
    BuildingNr = Column(String(80), primary_key=False)


class InjParam(Base):
    __tablename__ = 'InjParam'
    MachineId = Column(Integer, primary_key=True)
    MachStateId = Column(Integer, primary_key=False)
    QcTolCnt = Column(Integer, primary_key=False)
    CstAvgTime = Column(Float, primary_key=False)
    LastUpdate = Column(Integer, primary_key=False)
    CtrlSideId = Column(Integer, primary_key=False)
    ParaFileName = Column(Integer, primary_key=False)
    PartsNum = Column(Integer, primary_key=False)
    ResinType = Column(Integer, primary_key=False)
    Motor = Column(Integer, primary_key=False)
    Heater = Column(Integer, primary_key=False)
    BfPowerOnTime = Column(Integer, primary_key=False)
    BfAutoCycleTime = Column(Integer, primary_key=False)
    QcTolSum = Column(Integer, primary_key=False)
    QcTolPer = Column(Integer, primary_key=False)
    QcLastTime = Column(Integer, primary_key=False)
    QcAvgSum = Column(Integer, primary_key=False)
    MclSel = Column(Integer, primary_key=False)
    MclSelEng = Column(Integer, primary_key=False)
    TimeLpr = Column(Integer, primary_key=False)
    MclSpd1 = Column(Integer, primary_key=False)
    MclSpd2 = Column(Integer, primary_key=False)
    MclSpd3 = Column(Integer, primary_key=False)
    MclSpd4 = Column(Integer, primary_key=False)
    MclSpd5 = Column(Integer, primary_key=False)
    MclPrs1 = Column(Integer, primary_key=False)
    MclPrs2 = Column(Integer, primary_key=False)
    MclPrs3 = Column(Integer, primary_key=False)
    MclPrs4 = Column(Integer, primary_key=False)
    MclPrs5 = Column(Integer, primary_key=False)
    MclPos1 = Column(Integer, primary_key=False)
    MclPos2 = Column(Integer, primary_key=False)
    MclPos3 = Column(Integer, primary_key=False)
    MclPos4 = Column(Integer, primary_key=False)
    MclPos5 = Column(Integer, primary_key=False)
    MopSel = Column(Integer, primary_key=False)
    MopSelEng = Column(Integer, primary_key=False)
    ClampForce = Column(Integer, primary_key=False)
    MopSpd4 = Column(Integer, primary_key=False)
    MopSpd3 = Column(Integer, primary_key=False)
    MopSpd2 = Column(Integer, primary_key=False)
    MopSpd1 = Column(Integer, primary_key=False)
    MopSpd0 = Column(Integer, primary_key=False)
    MopPrs4 = Column(Integer, primary_key=False)
    MopPrs3 = Column(Integer, primary_key=False)
    MopPrs2 = Column(Integer, primary_key=False)
    MopPrs1 = Column(Integer, primary_key=False)
    MopPrs0 = Column(Integer, primary_key=False)
    MopPos4 = Column(Integer, primary_key=False)
    MopPos3 = Column(Integer, primary_key=False)
    MopPos2 = Column(Integer, primary_key=False)
    MopPos1 = Column(Integer, primary_key=False)
    MopPos0 = Column(Integer, primary_key=False)
    HldSel = Column(Integer, primary_key=False)
    HldSelEng = Column(Integer, primary_key=False)
    InjMode = Column(Integer, primary_key=False)
    InjModeEng = Column(Integer, primary_key=False)
    HldSpd4 = Column(Integer, primary_key=False)
    HldSpd3 = Column(Integer, primary_key=False)
    HldSpd2 = Column(Integer, primary_key=False)
    HldSpd1 = Column(Integer, primary_key=False)
    HldSpd0 = Column(Integer, primary_key=False)
    HldPrs4 = Column(Integer, primary_key=False)
    HldPrs3 = Column(Integer, primary_key=False)
    HldPrs2 = Column(Integer, primary_key=False)
    HldPrs1 = Column(Integer, primary_key=False)
    HldPrs0 = Column(Integer, primary_key=False)
    HldTime4 = Column(Integer, primary_key=False)
    HldTime3 = Column(Integer, primary_key=False)
    HldTime2 = Column(Integer, primary_key=False)
    HldTime1 = Column(Integer, primary_key=False)
    HldTime0 = Column(Integer, primary_key=False)
    TtimeInjP = Column(Integer, primary_key=False)
    InjSel = Column(Integer, primary_key=False)
    InjSelEng = Column(Integer, primary_key=False)
    TimeDchr = Column(Integer, primary_key=False)
    InjSpd5 = Column(Integer, primary_key=False)
    InjSpd4 = Column(Integer, primary_key=False)
    InjSpd3 = Column(Integer, primary_key=False)
    InjSpd2 = Column(Integer, primary_key=False)
    InjSpd1 = Column(Integer, primary_key=False)
    InjSpd0 = Column(Integer, primary_key=False)
    InjPrs5 = Column(Integer, primary_key=False)
    InjPrs4 = Column(Integer, primary_key=False)
    InjPrs3 = Column(Integer, primary_key=False)
    InjPrs2 = Column(Integer, primary_key=False)
    InjPrs1 = Column(Integer, primary_key=False)
    InjPrs0 = Column(Integer, primary_key=False)
    InjPos5 = Column(Integer, primary_key=False)
    InjPos4 = Column(Integer, primary_key=False)
    InjPos3 = Column(Integer, primary_key=False)
    InjPos2 = Column(Integer, primary_key=False)
    InjPos1 = Column(Integer, primary_key=False)
    InjPos0 = Column(Integer, primary_key=False)
    InjInjp = Column(Integer, primary_key=False)
    EjtSel = Column(Integer, primary_key=False)
    EjtSelEng = Column(Integer, primary_key=False)
    EjtCnt = Column(Integer, primary_key=False)
    EjtSpd0 = Column(Integer, primary_key=False)
    EjtSpd1 = Column(Integer, primary_key=False)
    EjtSpd2 = Column(Integer, primary_key=False)
    EjtSpd3 = Column(Integer, primary_key=False)
    EjtPrs0 = Column(Integer, primary_key=False)
    EjtPrs1 = Column(Integer, primary_key=False)
    EjtPrs2 = Column(Integer, primary_key=False)
    EjtPrs3 = Column(Integer, primary_key=False)
    EjtPos0 = Column(Integer, primary_key=False)
    EjtPos1 = Column(Integer, primary_key=False)
    EjtPos2 = Column(Integer, primary_key=False)
    EjtPos3 = Column(Integer, primary_key=False)
    EjtBkMode = Column(Integer, primary_key=False)
    EjtBkModeEng = Column(Integer, primary_key=False)
    EjtFwMode = Column(Integer, primary_key=False)
    EjtFwModeEng = Column(Integer, primary_key=False)
    ChrSel = Column(Integer, primary_key=False)
    ChrSelEng = Column(Integer, primary_key=False)
    ChrBar = Column(Integer, primary_key=False)
    TimeChrp = Column(Integer, primary_key=False)
    ChrSpd0 = Column(Integer, primary_key=False)
    ChrSpd1 = Column(Integer, primary_key=False)
    ChrSpd2 = Column(Integer, primary_key=False)
    ChrSpd3 = Column(Integer, primary_key=False)
    ChrSpd4 = Column(Integer, primary_key=False)
    ChrPrs0 = Column(Integer, primary_key=False)
    ChrPrs1 = Column(Integer, primary_key=False)
    ChrPrs2 = Column(Integer, primary_key=False)
    ChrPrs3 = Column(Integer, primary_key=False)
    ChrPrs4 = Column(Integer, primary_key=False)
    ChrPos0 = Column(Integer, primary_key=False)
    ChrPos1 = Column(Integer, primary_key=False)
    ChrPos2 = Column(Integer, primary_key=False)
    ChrPos3 = Column(Integer, primary_key=False)
    ChrPos4 = Column(Integer, primary_key=False)
    Tn1 = Column(Integer, primary_key=False)
    Tn2 = Column(Integer, primary_key=False)
    T1 = Column(Integer, primary_key=False)
    T2 = Column(Integer, primary_key=False)
    T3 = Column(Integer, primary_key=False)
    T4 = Column(Integer, primary_key=False)
    T5 = Column(Integer, primary_key=False)
    T6 = Column(Integer, primary_key=False)
    Tmold1 = Column(Integer, primary_key=False)
    Tmold2 = Column(Integer, primary_key=False)
    Tin = Column(Integer, primary_key=False)
    NowTn1 = Column(Integer, primary_key=False)
    NowTn2 = Column(Integer, primary_key=False)
    NowT1 = Column(Integer, primary_key=False)
    NowT2 = Column(Integer, primary_key=False)
    NowT3 = Column(Integer, primary_key=False)
    NowT4 = Column(Integer, primary_key=False)
    NowT5 = Column(Integer, primary_key=False)
    NowT6 = Column(Integer, primary_key=False)
    NowTmold1 = Column(Integer, primary_key=False)
    NowTmold2 = Column(Integer, primary_key=False)
    NowTin = Column(Integer, primary_key=False)
    Oee = Column(Integer, primary_key=False)

    def to_dict(self):
        """將數據轉為字典"""
        dictionary = self.__dict__
        if "_sa_instance_state" in dictionary:
            del dictionary["_sa_instance_state"]
        return dictionary


class InjParamTol(Base):
    __tablename__ = 'InjParamTol'
    ParamID = Column(Integer, primary_key=True)
    ParamName = Column(String(20), primary_key=False, nullable=False)
    ParamChiName = Column(String(20), primary_key=False, nullable=True)
    Tolerance = Column(Float, nullable=True)
    Category = Column(String(20), primary_key=False, nullable=True)


class SpcRecord(Base):
    __bind_key__ = 'mold'
    __tablename__ = 'SpcRecord'
    MachineId = Column(Integer, primary_key=True)
    TimeStemp = Column(DateTime, primary_key=True)
    BfInjEnd = Column(Float, nullable=False)

    def __init__(self, MachineId=None):
        self.MachineId = MachineId

    def __repr__(self):
        return '<User %r>' % self.MachineId


class MdyRecord(Base):
    __bind_key__ = 'mold'
    __tablename__ = 'MdyRecord'
    MachineId = Column(Integer, primary_key=True)
    MdyTime = Column(DateTime, primary_key=False)
    MdyAddr = Column(String(80), primary_key=False)
    OldValue = Column(Integer, primary_key=False)
    NewValue = Column(Integer, primary_key=False)


class AlmRecord(Base):
    __bind_key__ = 'mold'
    __tablename__ = 'AlmRecord'
    MachineId = Column(Integer, primary_key=True)
    AlmTime = Column(DateTime, primary_key=True)
    AlmCode = Column(Integer, primary_key=False)
    AlmMsg = Column(String(80), primary_key=False)

    def to_dict(self):
        """將數據轉為字典"""
        dictionary = self.__dict__
        if "_sa_instance_state" in dictionary:
            del dictionary["_sa_instance_state"]
        return dictionary


def init_db():
    """建立表"""
    Base.metadata.create_all(bind=engine)
    print('Database Initialized')


if __name__ == '__main__':
    # init_db()
    from main.tictoc import *
    now = datetime.datetime.now()
    q_count_tol = db_session.query(SpcRecord.MachineId) \
        .filter(SpcRecord.MachineId == 1,
                SpcRecord.TimeStemp >= '2019-11-01',
                SpcRecord.TimeStemp < str(now.date())).count()

    print(q_count_tol)
    # # q_state = db_session.execute('select MachineId, MachStateId, CstAvgTime from InjParam')
    # toc(t)
    # print(MdyRecord.query.first().MdyAddr)
    # print(InjParam.query.first().to_dict())

    # i = 1
    # for key in dict.keys():
    #     print(key)
    #     new_tol = InjParamTol(ParamID=i, ParamName=key)
    #     i = i+1
    #     db_session.add(new_tol)
    # db_session.commit()
