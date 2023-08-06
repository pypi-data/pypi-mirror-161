#  Copyright (c) 2017-2021 Jeorme Douay <jerome@far-out.biz>
#  All rights reserved.

class Trigger(object):
    '''
    Generate Table at the time of the event. The event shall be generated from a digital
    signal
    '''

    def __init__(self):
        super().__init__()
        self.signals = []
        self.trigger = ''
        self.up = True  # determine direction of trigger

    def set_trigger(self, name, up=True):
        '''
        Set the name of the trigger signal

        :param name: name of the signal to be used as trigger ( digital )
        :param up: True if the event is rising
        :return: None
        '''
        self.trigger = name
        self.up = up

    def process(self, data):
        '''
        Process the data and returns the events in a pandas dataframe

        :param data: data to be analysed
        :return: pandas dataframe with all the signals and events
        '''
        self.__change(self.trigger, data)

        if self.up:
            trigs = data.loc[data['%s_mod' % (self.trigger)] > 0]
        else:
            trigs = data.loc[data['%s_mod' % (self.trigger)] < 0]

        trigs.drop('%s_mod' % (self.trigger),axis=1,inplace=True)
        trigs.drop('%s' % (self.trigger),axis=1,inplace=True)
        return trigs

    def __change(self, name, data):
        dest = '%s_mod' % (name)
        data[dest] = data[name].shift(-1) - data[name]
        data.dropna()
