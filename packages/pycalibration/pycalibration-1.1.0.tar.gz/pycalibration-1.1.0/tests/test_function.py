import pytest
from pycalibration import Function

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"

def test_process():
    f=Function()
    f.add_file('./tests/test.mf4')
    f.add_channel('EngSpeed')
    data=f.process()[0]
    assert(len(data.index)!=0)

    # TODO test not workinig
    f=Function()
    f.add_file('./tests/test.mf4')
    f.add_channel('Speed')
    data=f.process()[0]
    assert(len(data.index)==0)


def test_evaluate():
    f=Function()
    f.add_file('./tests/test.mf4')
    f.add_channel('EngSpeed')
    data=f.get()[0]
    assert(data.equals(f.evaluate(data)))

def test_lab():
    f=Function()
    f.add_channel('EngSpeed')
    f.lab()
    from os.path import exists
    # TODO file not found
    assert(exists('./pycalibratiom.function.lab'))

# def test_csv():
#     f=Function()
#     f.add_file('./tests/test.mf4')
#     assert(len(extract.files)==1)

# def test_pretty():
#     f=Function()
#     f.add_file('./tests/test.mf4')
#     assert(len(extract.files)==1)

# def test_queued():
#     f=Function()
#     f.add_file('./tests/test.mf4')
#     assert(len(extract.files)==1)

# def test_worker():
#     f=Function()
#     f.add_file('./tests/test.mf4')
#     assert(len(extract.files)==1)
