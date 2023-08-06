import numpy

class Resistance(object):
    '''
    This class calculates the vehicle driving resistance
    '''
    def __init__(self, cx=0, fr=0, ro=0):
        '''
        Initialization of parameters for the driving resistance
        :param cx: drag coefficient * front surface in m^2
        :param fr: rolling resistance coefficient
        :param ro: air density in kg/m^2
        '''
        super().__init__()
        self.cx = cx
        self.fr = fr
        self.ro = ro

    def resistance(self, v, m, grade=0):
        '''
        Return the sum of air, pitch and rolling resisting force
        :param v: vehicle speed in m/s
        :param m: total vehicle mass in kg
        :param grade: slope in percentage
        :return: total resisting force in N
        '''
        return self.fair(v) + self.frolling(m, grade) + self.fpitch(m, grade)

    def fair(self, v):
        '''
        Return the air resisting force
        :param v: vehicle speed in m/s
        :return: air resisting force in N
        '''
        return self.cx * self.ro / 2 * (v) ** 2

    def frolling(self, m, grade):
        '''
        Return the rolling resisting force
        :param m: total vehicle mass in kg
        :param pitch: slope in percentage
        :return: rolling resisting force in N
        '''
        return self.fr * m * 9.81 * numpy.cos(numpy.arctan(grade / 100))

    def fpitch(self, m, grade):
        '''
        Return the pitch resisting force at a specified pitch
        :param m: total vehicle mass in kg
        :param pitch: slope in percentage
        :return: pitch resisting force in N
        '''
        return m * 9.81 * numpy.cos(numpy.pi / 2 - numpy.arctan(grade / 100))
