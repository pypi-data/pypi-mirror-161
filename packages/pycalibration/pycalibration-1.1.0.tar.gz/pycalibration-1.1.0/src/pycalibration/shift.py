#  Copyright (c) 2017-2021 Jeorme Douay <jerome@far-out.biz>
#  All rights reserved.

import pandas, datetime, logging
from .trigger import Trigger

class Shift(object):
    '''
    Generate Table bevore and after shifting
    All the columns supplied in the data for process will be used. At the beginning of the shift, the columns will be added '_pre', at the end of the shift '_post'.
    '''

    def __init__(self):
        super().__init__()
        self.pre = Trigger()
        self.post = Trigger()

    def set_pre(self,pre,up=True):
        '''
        Set the pre channel used for trigger

        :param pre: Channel name to be used as trigger
        :param up: Determine the signal direction ( up/down, up by default )
        '''
        self.pre.set_trigger(pre,up)

    def set_post(self,post,up=False):
        '''
        Set the post channel used for trigger

        :param pre: Channel name to be used as trigger
        :param up: Determine the signal direction ( up/down, up by default )
        '''
        self.post.set_trigger(post,up)

    def process(self, data):
        '''
        Process the data and return the table containing the shifts.

        :param data: pandas Dataframe containing the data, inclusive the channel to be used to detect the shift
        :return: Pandas dataframe containing the pre and post shifts data.
        '''
        pre=self.pre.process(data.copy())
        #pre=pre.reset_index(drop=False)
        pre=pre.add_suffix('_pre')

        post=self.post.process(data.copy())
        #post=post.reset_index(drop=True)
        post=post.add_suffix('_post')

        results = pandas.concat([pre, post], axis=1)
        for col in post.columns:
            results[col]=results[col].shift(-1)
        #results = results.dropna(subset=['gear_pre'])
        results= results.dropna()
        results.drop('filename_post',axis=1,inplace=True)
        results.rename(columns={'filename_pre':'filename'},inplace=True)
        #logging.info('%i shifts detected' % len(results.index))
        return (results)
