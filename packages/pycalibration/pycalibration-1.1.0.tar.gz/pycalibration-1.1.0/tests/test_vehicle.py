import pytest
from pycalibration import Vehicle

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"

def test_energy():
    v=Vehicle()
    assert(round(v.energy(1000,5,4000))==33346)

def test_engine_to_speed():
    v=Vehicle()
    assert(round(v.engine_to_speed(1000,1),2)==2.45)

def test_fresist():
    v=Vehicle()
    assert(v.fresist(1,1,0)==10.31)

def test_force_to_torque():
    v=Vehicle()
    assert(round(v.force_to_torque(1000,1),2)==23.4)

def test_ratio():
    v=Vehicle()
    assert(v.ratio(1)==21.5)

def test_speed_to_engine():
    v=Vehicle()
    assert(round(v.speed_to_engine(1,1))==408)

def test_torque():
    v=Vehicle()
    assert(v.torque(1000)==500)

def test_torque_to_force():
    v=Vehicle()
    assert(v.torque_to_force(100,1)==1081.45)

