import pytest, numpy
from pycalibration import Engine

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"

def test_torque():
    engine=Engine()
    assert(engine.torque(1000)==500)

def test_power():
    engine=Engine()
    assert(engine.power(1000)==engine.torque(1000)*1000/60*2*numpy.pi)

def test_npower():
    engine=Engine()
    power=engine.power(1000)
    assert(engine.npower(power)==1000)

