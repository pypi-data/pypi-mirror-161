import pytest
from pycalibration import Value

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"

def test_x():
    value=Value([1,2,3])
    assert(value.x(0)==1)
    assert(value.y(1)==None)
    assert(value.z(1,1)==None)

def test_y():
    value=Value([1,2,3], [1,2,3])
    assert(value.x(0)==1)
    assert(value.y(1)==1)
    assert(value.z(1,1)==None)

def test_z():
    value=Value([1,2,3], [1,2,3], [[1,2,3],[4,5,6],[7,8,9]])
    assert(value.x(0)==1)
    assert(value.y(1)==None)
    assert(value.z(1,1)==1)
