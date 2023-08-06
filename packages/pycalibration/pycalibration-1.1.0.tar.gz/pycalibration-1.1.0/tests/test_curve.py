import pytest
from pycalibration import Curve

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"

def test_y():
    curve=Curve([1,2,3],[1,2,3])
    assert(curve.y(1)==1)
    assert(curve.y(2)==2)
    assert(curve.y(3)==3)
    assert(curve.y(1.5)==1.5)

def test_insert():
    curve=Curve([1,2,3],[1,2,3])
    curve.insert(4,4)
    curve.insert(3,5)
    assert(len(curve.data['x']==4))
    assert(len(curve.data['y']==4))
    assert(curve.y(3)==5)

