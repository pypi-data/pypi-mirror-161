import pytest
from pycalibration.mdf import MDF

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"

#mdf.set_file('./tests/test.mf4')

def test_add_channel():
    mdf = MDF('./tests/test.mf4')
    mdf.add_channel('EngSpeed')
    assert(len(mdf.channels.loc[mdf.channels['channel']=='EngSpeed'])==1)
    assert(len(mdf.channels.loc[mdf.channels['rename']=='EngSpeed'])==1)
    assert(len(mdf.channels.index)==1)
    mdf.add_channel('EngSpeed') # double insertion
    assert(len(mdf.channels.index)==1)

def test_get_channel():
    mdf = MDF('./tests/test.mf4')
    data=mdf.get_channel('EngSpeed')
    assert(data.iloc[0][0]==1093)

    # TODO error when trying to get a channel that does not exist
    mdf = MDF('./tests/test.mf4')
    #with pytest.raises(Exception):
    mdf.get_channel('Speed')

def test_get_data():
    mdf = MDF('./tests/test.mf4')
    mdf.add_channel('EngSpeed','n')
    mdf.add_channel('EngSpeedd','n') # no error just for case of already a rename
    data=mdf.get_data()
    assert(len(data.columns)==3)
    assert('n' in data.columns)

def test_set_file():
    mdf = MDF()
    assert(mdf.filename==None)
    mdf.set_file('./tests/test.mf4')
    assert(mdf.filename=='./tests/test.mf4')
    # TODO test set file for version 3 and 4
