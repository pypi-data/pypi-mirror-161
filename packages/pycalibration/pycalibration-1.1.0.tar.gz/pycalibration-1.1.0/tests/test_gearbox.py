import pytest
from pycalibration import Gearbox

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"

def test_ratio():
    g=Gearbox()
    assert(g.ratio(1)==10)