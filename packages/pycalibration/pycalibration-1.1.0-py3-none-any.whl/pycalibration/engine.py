import numpy
from scipy.interpolate import interp1d

# TODO engine configuration from JSON file
class Engine(object):
    '''
    Class engine offers support for engine calculation and estimation.
    '''

    def __init__(self,n=[600,1000,2000,4000,6000],t=[100,500,1000,800,100]):
        super().__init__()
        self.t = interp1d(n, t)
        self.tmax=max(t)
        p= [n[i]*t[i]/ 60 * 2 * numpy.pi for i in range(len(n))]
        self.pmax=max(p)
        ppos=p.index(max(p))
        self.p=interp1d(n[0:ppos+1], p[0:ppos+1])
        self.np = interp1d(p[0:ppos+1], n[0:ppos+1])
        tpos=t.index(max(t))
        self.nt = interp1d(t[0:tpos+1], n[0:tpos+1])

    def npower(self,power):
        return self.np(power)

    def power(self,speed,limit=100):
        '''
        Return the Power at a given engine speed and a percentage torque
        :param speed: engine speed in rpm
        :param limit: max percentage torque
        :return: engie power in watts
        '''
        return self.p(speed)

    def torque(self,speed,limit=100):
        '''
        Return the torque at an engine speed with a max percentage torque ( 100% is full torque)
        :param speed: engine speed in rpm
        :param limit: maximum percent torque from curve
        :return: engine torque in Nm
        '''
        return self.t(speed)*limit/100

