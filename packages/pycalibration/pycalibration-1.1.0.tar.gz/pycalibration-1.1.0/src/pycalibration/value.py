import json
from scipy.interpolate import interp1d, interp2d

class Value(object):
    '''
    Value class represent the informations stored in a parameter. Each value can be a single value, a curve or a map. All points are interpolated
    '''
    def __init__(self,x,y=None,z=None):
        '''
        Initialisation of the value
        :param val: values in string json format
        '''
        self._x=x
        self._y=y
        self._z=z
        self._f = lambda x: None

        if y is not None:
            if z is None:
                self._f = interp1d(self._x, self._y)
            else:
                self._f = interp2d(self._x, self._y, self._z)

    def x(self,pos):
        '''
        Return the X value at a position ( interpolated from the array)
        :param pos: position in the array
        :return: X value
        '''
        return self._x[pos]

    def y(self,x):
        '''
        Return the Y value at a X position ( interpolated from the array)
        :param pos: position in the array
        :return: Y value
        '''
        if self._y is None:
            return None
        if self._z is not None:
            return None
        return self._f(x)

    def z(self,x,y):
        '''
        Return the Z value at a X,Y position ( interpolated from the array)
        :param pos: position in the array
        :return: Z value
        '''
        if self._z is None:
            return None
        return self._f(x,y)
