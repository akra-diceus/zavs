#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  stage 0.3-0
#
#  Copyright 2016,2017 svetkesh <https://github.com/svetkesh>
#

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String #, Boolean
from sqlalchemy.orm import relationship, backref, sessionmaker
import random
import string
from sqlalchemy.ext.hybrid import hybrid_property

'''Proposed structure, zero-3 iteration
03 - tables linked in separate module


'''

engine = create_engine('sqlite:///:memory:', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class DataAccessLayer():
    '''Assumed conn_string="'sqlite:///:memory:'" .  '''

    def __init__(self):
        '''Initiate class DataAccessLayer():.  '''
        self.engine = None
        self.conn_string = 'conn string'

    def connect(self):
        '''Conect.  '''
        self.engine = create_engine(self.conn_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

#dal = DataAccessLayer()  #  Commented for future imports


class Computer(Base):
    '''
    Computer describes principal attributes for
    PC in LAN : name and ip.


    '''
    __tablename__ = "computers"

    computer_id = Column(Integer, primary_key=True, nullable=False, unique=True)
    _name = Column(String(50), index=True, nullable=False)  # NetBios is
                                                          # limited to 15 char
    _ip = Column(String(15))

    def __repr__(self):
        '''Presentation for computers.'''
        return(str('computer_id ' + str(self.computer_id) +
            ' name ' + str(self.name) +
            ' ip ' + str(self.ip)
            )
        )

    @hybrid_property
    def name(self):
        '''Property for PCs name.  '''
        return self._name

    @name.setter
    def name_setter(self, name):
        '''Setter PC name. '''
        #print('DBG: name_setter with name', name)
        self._name = name

    #ip

    @hybrid_property
    def ip(self):
        '''Property for PCs ip address.  '''
        return self._ip

    @ip.setter
    def ip_setter(self, ip):
        '''Setter for PC ip. '''
        #print('DBG: ip_setter with ip', ip)
        self._ip = ip


class Licence(Base):
    '''
    Describe antivirus licences for computers.


    '''
    __tablename__ = "licences"

    licence_id = Column(Integer, primary_key=True, nullable=False, unique=True)
    _licence_code = Column(String(50))

    def __init__(self):
        '''
        Uses un-safe version of random lenght of 10
        http://stackoverflow.com/questions/2257441/
        random-string-generation-with-upper-case-letters-and-digits-in-python .


        '''
        self.licence_code = ''.join(
            random.choice(
                string.ascii_uppercase + string.digits) for _ in range(10))

    def __repr__(self):
        '''Presentation for Licence.  '''
        return(str('licence_id ' + str(self.licence_id) +
            ' licence_code ' + str(self.licence_code)
            )
        )

    @hybrid_property
    def licence_code(self):
        '''Stores licence code.  '''
        return self._licence_code

    @licence_code.setter
    def licence_code_setter(self, code):
        '''Linence code could be modified in some sercumstances.  '''
        #print('DGB: licence_code_setter with code', code)
        self._licence_code = code


class LicComp(Base):
    '''
    Contains relation between Computers and issued Licences.


    '''
    __tablename__ = "liccomps"

    liccomps_id = Column(Integer, primary_key=True)
    _computers_id = Column(Integer, ForeignKey("computers.computer_id"))
    _licences_id = Column(Integer, ForeignKey("licences.licence_id"))

    computer = relationship("Computer", backref=backref("liccomps",
         order_by=liccomps_id))
    licence = relationship("Licence", backref=backref("liccomps",
         order_by=liccomps_id))

    def __repr__(self):
        '''Presentation for licenced computers.'''
        return ( "liccomps_id=" + str(self.liccomps_id) + " licences_id=" +
            str(self.licences_id) + " used by computers_id=" +
            str(self.computers_id))

    #computers_id part
    @hybrid_property
    def computers_id(self):
        '''Computer id should not be modified in this table normally.  '''
        return self._computers_id

    @computers_id.setter
    def computers_id_setter(self, comp_id):
        '''Placeholder for future restriction of modifications.  '''
        #print('DGB: computers_id_setter with id', comp_id)
        self._computers_id = comp_id


    #licences_id part
    @hybrid_property
    def licences_id(self):
        '''Licence id should not be modified here normally.  '''
        return self._licences_id

    @licences_id.setter
    def licences_id_setter(self, lic_id):
        '''Placeholder for future restriction of modifications.  '''
        #print('DGB: licences_id_setter with licences_id', lic_id)
        self._licences_id = lic_id

    def revoke_licence_id(self):
        '''Placeholder for licence revokator.  '''
        pass                            # most interesting place

    def assign_licence_computer(self):
        '''Placeholder for licence assigner.  '''
        pass

# some proc for manual testing and object manipulations
#assign licence to computer
def assign_l_c(licence, computer):
    '''Inline assigning licence to computer.  '''
    print('\nDBG: check data b4 assigning...')
    print('DBG: given lic_id {} and comp_id {}'.format(
        licence.licence_id ,
        computer.computer_id))
    try:
        new_lic_comp = LicComp(
            licences_id=licence.licence_id ,
            computers_id=computer.computer_id)
        #new_lic_comp = LicComp(licences_id=5, computers_id=5)  #raw nums ok
        print('DBG: about to add new ', new_lic_comp)
        session.add(new_lic_comp)
        session.commit()
        return True
    except: # general exception
        print('ERR: error while assigning licence to computer')
        return False

def compter_add(name, ip):  # - not working in import
    '''This shold be tetsted against possible use after import'''
    comp = Computer(name=name, ip=ip)
    session.add(comp)
    session.commit()

Base.metadata.create_all(engine)

#manual testing and exploring objects
comp1 = Computer(name='comp1', ip='10.10.10.1')
session.add(comp1)
comp2 = Computer(name='comp2', ip='10.10.10.2')
session.add(comp2)
session.commit()  # ok


print('Added computer with id:', comp1.computer_id)
print('Added computer', comp2)

#query-column order
q_col_ordered = session.query(Computer).all()
print('DBG: session.query(Computer).all()', q_col_ordered, type(q_col_ordered))

q_col_ordered = session.query(Computer.name, Computer.ip).first()
print('DBG: session.query(Computer.name, Computer.ip).first()',
     q_col_ordered, type(q_col_ordered))
print(q_col_ordered.__dir__())
print(q_col_ordered.keys())
print(q_col_ordered.keys()[0])
print(q_col_ordered.name)


#exploring Licence object
lic_1 = Licence()
print('Exploring Licence\nAdded licence_code', lic_1.licence_code)

lic_1.licence_code = 'aa-bb-cc'
print('Updated to aa-bb-cc licence_code', lic_1.licence_code)

session.add(lic_1)
session.commit()

all_lics = session.query(Licence).all()
print('All licences:', all_lics)

lic_3=Licence()
print(lic_3)  # not saved yet, just exploring

lic_3.licence_code = 'aa=ss=dd=ff'
print(lic_3)

session.add(lic_3)
session.commit()

lic_4 = Licence()
session.add(lic_4)
session.commit()

all_lics = session.query(Licence).all()
print('All licences:', all_lics)

#exploring Computer object
compter_add('comp3', '192.16.1.101')
c_all = session.query(Computer).all()
print(c_all)


#inline testing LicComp
lc1 = LicComp(licences_id=1, computers_id=3)
session.add(lc1)
session.commit()
lc_1 = session.query(LicComp).first()
print('New LicComp', lc_1)

#test change values for LicComps
lc1.licences_id, lc1.computers_id =2, 3
session.add(lc1)
session.commit()
updated_lic_comps = session.query(LicComp).first()
print('Upd LicComp', updated_lic_comps)


#manual test for assign_licence_to_computer
#prepare and counts existent objects

#later in tests
# c stands for Computer
# l for Licence
# lc for LicComp
print('\n Count present computers and licences')
c04 = session.query(Computer).all()
l04 = session.query(Licence).all()
lc04 = session.query(LicComp).all()
print(c04, l04, lc04)
print('Total Computers:', len(c04),
        'Licences:', len(l04),
        'LicComp:', len(lc04))

#add one more computer
c5 = Computer(name='comp5', ip='10.10.10.5')
l5 = Licence()
lc5 = LicComp(licences_id=5, computers_id=5)
#lc5 = LicComp()                   # adding empty row

session.add(c5)
session.add(l5)
session.add(lc5)
session.commit()
print('Added LicComp lc5: ', lc5)


if assign_l_c(l5, c5):
    all_lic_comp = session.query(LicComp).all()
    print('All licences for computers:\n', all_lic_comp)
else:
    print('assign_l_c did not assigned LicComp')


