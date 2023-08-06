import pandas
from scipy.interpolate import interp1d, interp2d, RectBivariateSpline

class Map(object):

    def __init__(self,x,y,z):
        self._x=x
        self._y=y
        self._z=z
        self._fxy = interp2d(self._x,self._y,self._z)
        self._fyz = interp2d(self._y, self._z,self._x)
        self._fxz = interp2d(self._x, self._z,self._y)

    def z(self,x,y):
        return self._fxy(x,y)

    def y(self,x,z):
        return self._fxz(x,z)

    def x(self,y,z):
        return self._fyz(y,z)
