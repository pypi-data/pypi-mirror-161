import pytest
from pycalibration import VBO

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"

def test_vbo():
    vbo=VBO()
    data=vbo.read('./tests/vbo.vbo')
    data=vbo.df
    assert(len(data.index)==100)