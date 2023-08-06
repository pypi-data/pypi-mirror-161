import pytest
from pycalibration import Extract
from pycalibration import Trigger

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"

extract =Extract()
extract.add_file('./tests/test.mf4')
extract.add_channel('EngSpeed','n',True)
extract.add_channel('TransShiftInProcess','ShiftInProcess')

def test_set_trigger():
    trigger=Trigger()
    trigger.set_trigger('ShiftInProcess')
    assert(trigger.trigger=='ShiftInProcess')

def test_process_up():
    trigger=Trigger()
    trigger.set_trigger('ShiftInProcess')
    data=extract.get()[0]
    triggers=trigger.process(data)
    assert(len(triggers.index)!=0)

def test_process_down():
    trigger=Trigger()
    trigger.set_trigger('ShiftInProcess',False)
    data=extract.get()[0]
    triggers=trigger.process(data)
    assert(len(triggers.index)!=0)
