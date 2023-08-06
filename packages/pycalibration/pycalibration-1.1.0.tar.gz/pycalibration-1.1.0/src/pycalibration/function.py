from fileinput import filename
from .extract import Extract
import logging, pandas, os.path
import progressbar
from threading import Thread
from tabulate import tabulate

class Function(Extract):
    '''
    Base class to define function in module

    Based on Extract, it supoprt all the extract method. It is necessary to set the files or directory to process before calling the process method.
    
    Evaluate method should be overwritten for data evaluation related to the function beeing developed.
    '''
    def __init__(self):
        self.parameters=[]
        super().__init__()
        self.module=self.__class__.__module__

    def process(self):
        '''
        Retrieve the necessary information from the measurment files.

        :return: list containing files processed results
        '''
        amount=0
        res=[]
        with progressbar.ProgressBar(max_value=len(self.files)) as bar:
            count=0
            for data in self:
                if len(data.index)==0:
                    logging.info('No data found in file')
                else:
                    amount+=len(data.index)
                    res.append(self.evaluate(data))
                count+=1
                bar.update(count)
        logging.info('Processed %i rows' % amount)
        return res

    def evaluate(self,data):
        '''
        Using the data retrieved from the measurement file, generate calibration
        This method should be over writen by the derivative class and returns what ever the evaluation is producing.

        :return: should return the evaluation data
        '''
        return data

    def lab(self):
        '''
        Write the labels and parameters in a lab file

        :return: None
        '''
        f = open('%s.lab' % self.module, 'w', encoding="utf-8")
        f.write('[RAMCELL]\n')
        for index,row in self.channels.iterrows():
            f.write('%s\n' % row['channel'])
        f.write('\n')

        # if self.parameters!=[]:
        #     f.write('[LABEL]\n')
        #     for param in self.parameters:
        #         f.write('%s\n' % param)
        f.close()

    # def csv(self):
    #     '''
    #     Write the data in csv file

    #     :return: None
    #     '''
    #     self.data.to_csv('%s.csv' % self.module)

    # def _pretty(self,data):
    #     logging.info("%s\n%s" %(self.module, tabulate(data,headers=data.columns,tablefmt="pretty")))
        
    # def _queued(self, q):
    #     while True:
    #         try:
    #             filename= q.get()
    #             q.task_done()
    #             self.set_file(filename)
    #             data=self.evaluate(self.get_data())
    #             self._pretty(data)
    #         except Exception as e:
    #             logging.error('%s' %str(e))

    # def worker(self,q):
    #     worker = Thread(target=self._queued, args=(q,))
    #     worker.setDaemon(True)
    #     worker.start()
    #     return worker