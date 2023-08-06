#  Copyright (c) 2017-2021 Jeorme Douay <jerome@far-out.biz>
#  All rights reserved.

import numpy, pandas #, pwlf #itertools
from scipy.interpolate import interp1d, interp2d

"""
Curve Class
"""
class Curve(object):
    """
    Curve allow the defintion and extroplation of data of a curve

    This class is usually returned by the DCM class after importing a file.
    """

    def __init__(self,x,y):
        #self.data=numpy.array([X,Y])
        self.data=pandas.DataFrame(columns=['x','y'])
        self.data['x']=x
        self.data['y']=y
        self._fx = interp1d(x, y)
#        self.fy = interp1d(Y, X)

    def y(self,x):
        """
        return the y value of a curve given the x value.

        Values are interpolated between the points given
        """
        return self._fx(x)

#    def X(self,Y):
#        return self.fy(Y)

    def insert(self,x,y):
        """
        Insert a point in the curve

        :param x: x value of the point
        :param y: y value of the point
        :return: None
        """
        if x in self.data['x'].values:
            self.data['y'].loc[self.data['x']==x]=y
        else:
            self.data=self.data.append(pandas.DataFrame([[x, y]],columns=['x','y']))
        self.data=self.data.sort_values('x')
        self._fx = interp1d(self.data['x'],self.data['y'])


#    def XMax(self):
#        return self.X.max()

#    def XMin(self):
#        return self.X.min()

#    def YMax(self):
#        return self.Y.max()

#    def YMin(self):
#        return self.Y.min()
