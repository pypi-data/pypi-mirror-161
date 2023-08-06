import pytest
from pycalibration import Resistance

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"

def test_resistance():
    r=Resistance(1,1,1)
    assert(r.resistance(1,1,0)==10.31)

def test_fair():
    r=Resistance(1,1,1)
    assert(r.fair(1)==0.5)

def test_frolling():
    r=Resistance(1,1,1)
    assert(r.frolling(1,0)==9.81)

def test_fpitch():
    r=Resistance(1,1,1)
    assert(round(r.fpitch(1,0))==0)
