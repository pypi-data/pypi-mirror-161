import pytest
from pycalibration import Map

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"

def test_z():
    g=Map(
        [1,1,1,2,2,2,3,3,3],
        [1,1,1,2,2,2,3,3,3],
        [1,2,3,4,5,6,7,8,9])
    assert(g.z(1,1)==1)

def test_y():
    g=Map(
        [1,1,1,2,2,2,3,3,3],
        [1,1,1,2,2,2,3,3,3],
        [1,2,3,4,5,6,7,8,9])
    assert(g.y(1,1)==1)

def test_x():
    g=Map(
        [1,1,1,2,2,2,3,3,3],
        [1,1,1,2,2,2,3,3,3],
        [1,2,3,4,5,6,7,8,9])
    assert(g.x(1,1)==1)