import pytest
from pycalibration import Extract
from pycalibration import Shift

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"

def test_process():
    extract =Extract()
    extract.add_file('./tests/test.mf4')
    extract.add_channel('EngSpeed','n',True)
    extract.add_channel('TransShiftInProcess','ShiftInProcess')
    shift=Shift()
    shift.set_pre('ShiftInProcess')
    shift.set_post('ShiftInProcess')
    data=extract.get()[0]
    shifts=shift.process(data)
    assert(len(shifts.index)!=0)
