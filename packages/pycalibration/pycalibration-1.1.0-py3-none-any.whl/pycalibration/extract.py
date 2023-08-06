#  Copyright (c) 2017-2021 Jeorme Douay <jerome@far-out.biz>
#  All rights reserved.
# Far-Out extraction
import glob
import pandas
import progressbar
import logging
from .mdf import MDF

class Extract(MDF):
    '''
    Extract class extract channels from single or multiple files
    '''
    def __init__(self):
        super().__init__()
        self.files = []

    def add_file(self, filename):
        '''
        Add single file to the list of files to be processed

        :param file: file name path to the file
        :return: none
        '''
        self.files.append(filename)
        self.files=list(set(self.files)) # remove dual entries just in case

    def add_directory(self, pathname):
        '''
        Add a directory recursively to the files to be processed.
        Files recognize are mdf and mf4 exensions

        :param path: path to be added
        :return: none
        '''
        self.files.extend(glob.glob(pathname + '/**/*.mdf', recursive=True))
        self.files.extend(glob.glob(pathname + '/**/*.mf4', recursive=True))
        self.files.extend(glob.glob(pathname + '/**/*.dat', recursive=True))
        self.files=list(set(self.files)) # remove dual entries just in case

    def get(self):
        '''
        Read the MDF files and retrieved the requested data.

        :return: list of pandas dataframe contaiing the datas.
        '''
        data = pandas.DataFrame()
        count=0
        data=[]
        with progressbar.ProgressBar(max_value=len(self.files)) as bar:
            bar.update(count)
            for filename in self.files:
                self.set_file(filename)
                data.append(self.get_data())
                count+=1
                bar.update(count)
        return data

    def __iter__(self):
        self.index=0
        return self

    def __next__(self):
        if self.index>=len(self.files):
            raise StopIteration
        filename=self.files[self.index]
        self.index+=1
        self.set_file(filename)
        return self.get_data()

