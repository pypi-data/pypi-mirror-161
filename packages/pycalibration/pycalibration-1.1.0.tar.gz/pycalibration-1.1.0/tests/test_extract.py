import pytest
from pycalibration import Extract

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"

def test_add_file():
    extract =Extract()
    extract.add_file('./tests/test.mf4')
    assert(extract.files==['./tests/test.mf4'])

def test_add_directory():
    extract =Extract()
    #extract.files=[]
    extract.add_directory('./tests')
    assert(len(extract.files)==1)

def test_add_channel():
    extract =Extract()
    extract.add_channel('EngSpeed')
    assert(len(extract.channels.loc[extract.channels['channel']=='EngSpeed'])==1)
    assert(len(extract.channels.loc[extract.channels['rename']=='EngSpeed'])==1)
    assert(len(extract.channels.index)==1)
    extract.add_channel('EngSpeed') # double insertion
    assert(len(extract.channels.index)==1)

def test_get():
    extract =Extract()
    extract.add_file('./tests/test.mf4')
    extract.add_channel('EngSpeed')
    data=extract.get()
    assert(len(data[0].columns)==3)
    assert('EngSpeed' in data[0].columns)

def test_iter():
    extract =Extract()
    extract.add_file('./tests/test.mf4')
    extract.add_channel('EngSpeed')
    d1=extract.get()[0]
    extract.__iter__()
    data=extract.__next__()
    assert(d1.equals(data))
    with pytest.raises(StopIteration):
        extract.__next__()