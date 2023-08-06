from pycalibration.engine import Engine
from pycalibration.gearbox import Gearbox
from pycalibration.resistance import Resistance
import pandas, numpy

# TODO vehicle configuration from JSON file

class Vehicle(object):
    '''
    class to represent a vehicle and basic calulation for the vehicle configuration

    '''
    def __init__(self):
        super().__init__()
        self.name='vehicle'
        self.gearbox=Gearbox()
        self.engine=Engine()
        self.resistance= Resistance(1,1,1)
        self.rar=2.15
        self.dynradius=0.503

    # def coast_down(self,data):
    #     '''
    #     Use Coast Down measurement to determine resistance values
    #     '''
    #     return

    # def driving_resistance_map(self,n_min=600, n_max=4000, gear=1):
    #     data=pandas.DataFrame(numpy.array(range(n_min,n_max+1,1)),columns=['n'])
    #     data['ratio'] = self.gearbox.Y(gear) * self.rar
    #     data['v'] = self.EngineToSpeed(data['n'], data['ratio'])
    #     data = data.loc[data['v']<=50]
    #     data['Fr'] = self.resistance.Y(data['v'])
    #     data['Tr']= self.ForceToTorque(data['Fr'],data['ratio'])
    #     data['Tr_p'] = data['Tr']/self.torque.Z(100,1400)*100
    #     return data

    def energy(self,n,gear,mass):
        return 0.5*mass*self.engine_to_speed(n,gear)**2

    def engine_to_speed(self, engine, gear):
        """
        Returns the vehicle speed from the engine speed and the common powertrain ratio
        :param engine: engine speed in 1/min
        :param gear: gear number
        :return: vehicle speed in m/s
        """
        res = engine / 60 / self.ratio(gear) * self.dynradius * 2 * numpy.pi
        return res.astype(float)

    # def fm(self, mass, alpha):
    #     '''
    #     Returns the normal force, which is perpendicular to the contact surface by entering the mass and the slope
    #     :param mass: total vehicle mass in kg
    #     :param alpha: slope in percentage
    #     :return: normal force in N
    #     '''
    #     res = mass * 9.81 * numpy.cos(numpy.pi/2-numpy.arctan(alpha/100))
    #     return res.astype(float)

    # def fm_to_alpha(self, fm, m):
    #     '''
    #     Returns the slope by entering the normal force and the total vehicle mass
    #     :param fm: normal force in N
    #     :param m: total vehicle mass in kg
    #     :return: slope in percentage
    #     '''
    #     return numpy.arctan(numpy.pi/2-numpy.arccos(fm/m/9.81))*100

    # def ft(self, torque, gear):
    #     """
    #     Returns the traction force from the engine torque and the gearbox ratio
    #     :param torque: engine torque in Nm
    #     :param ratio: gearbox ratio
    #     :return: traction force in N
    #     """
    #     res = torque * self.ratio(gear) * self.dynradius
    #     return res.astype(float)

    def fresist(self, speed, mass, grade=0):
        '''
        Returns the resistance force by entering the vehicle speed and the ratio (default ratio = 1)
        :param speed: vehicle speed in m/s
        :param mass: total vehicle mass in kg
        :param grade: road grade
        :return: resistance force in N
        '''
        return self.resistance.resistance(speed,mass,grade)

    def force_to_torque(self, f, gear):
        """
        Returns the engine torque from the traction force and the common powertrain ratio
        :param f: traction force in N
        :param ratio: common powertrain ratio
        :return: engine torque in Nm
        """
        return f * self.dynradius / self.ratio(gear)

    def ratio(self,gear):
        '''
        return the gear ration from the given gear

        :param gear: gear number
        :return: trans ratio (gear and rear axle ratio)
        '''
        return self.gearbox.ratio(gear)*self.rar

    def speed_to_engine(self, speed, gear):
        """
        Returns the engine speed from the vehicle speed and the common powertrain ratio
        :param speed: vehicle speed in m/s
        :param gear: gear number
        :return: engine speed in 1/min
        """
        res = speed / (2 * numpy.pi * self.dynradius) * self.ratio(gear) * 60
        return res.astype(float)

    # def time_on_gear(self, n_min=600, n_max=2000, gear=1, mass=9000, grade=0, limit=100, offset=0):
    #     data=pandas.DataFrame(numpy.array(range(n_min,n_max+1,1)),columns=['n'])
    #     tmax=self.engine.max_torque()
    #     data['t']=self.engine.torque(data['n'],limit)
    #     #data['tm'] = self.engine.Torque(data['n'], 100)
    #     data['P']=self.engine.power(data['n'])
    #     #data['Pm'] = self.engine.Power(data['n'],100)
    #     data['ratio'] = self.gearbox.ratio(gear) * self.rar
    #     data['v'] = self.engine_to_speed(data['n'], gear)
    #     data['Fr'] = self.resistance.resistance(data['v'],mass)
    #     data['Fr']=data['Fr']+self.fm(mass,grade)+offset
    #     data['acc']=(data['t']*data['ratio']/self.dynradius-data['Fr'])/mass
    #     data['tr']=self.force_to_torque(data['Fr'],gear)
    #     data['te']=data['t']-data['tr']
    #     data['Pr'] = data['tr'] * data['n'] / 60 * 2 * numpy.pi
    #     data['Pe'] = data['P']-data['Pr']
    #     data['dn']=data['acc']/2/numpy.pi/self.dynradius*data['ratio']*60
    #     data['dt'] = 1 / data['dn']
    #     data['dt'].loc[data['dt']<0]=0
    #     data['time'] = data['dt'].cumsum()
    #     #data['rt']=(data['t']-data['tr'])/data['tm']
    #     data['gear']=gear
    #     data['mass']=mass
    #     data['grade']=grade
    #     data['limit']=limit
    #     data['offset']=offset
    #     return data

    def torque(self, n, pedal=100):
        '''
        By default, this function returns the torque at an engine speed with a max percentage torque (100% is full torque)
        :param n: engine speed in rpm
        :param pedal: percentage value of the accelerator pedal; default 100% means full torque
        :return: engine torque in Nm
        '''
        return self.engine.torque(n)

    def torque_to_force(self, t, gear):
        """
        Returns the traction force from the engine torque and the common powertrain ratio
        :param t: engine torque in Nm
        :param ratio: common powertrain ratio
        :return: traction force in N
        """
        return t * self.ratio(gear) * self.dynradius

    