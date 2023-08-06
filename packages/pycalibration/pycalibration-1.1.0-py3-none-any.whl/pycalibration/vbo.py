import pandas, logging, datetime, numpy

class VBO():
    def __init__(self) -> None:
        self.header=[]
        self.colnames=[]
        self.units=[]
        self.comments=[]
        self.modules=[]
        self.data=[]
        self.df=pandas.DataFrame()
        self.start=None

    def read(self,filename):
        lines=[]
        with open(filename, encoding="utf-8") as f:
            line=f.readline()
            while line!='':
                lines.append(line)
                line=f.readline()

            f.close()
   
        start=lines.pop(0).split(' ')[3].replace('/','-')
        self.start="%s-%s-%s" %(start.split('-')[2],start.split('-')[1],start.split('-')[0])
        self.__sorting(lines)
        self.__columns_name()
        self.__data()
        return self.df

    def __columns_name(self):
        logging.info('Converting Column names')
        self.colnames=self.colnames[0].replace(' \n','')
        cols=self.colnames.split(' ')
        self.colnames=[col for col in cols]

    def __data(self):
        logging.info('Converting data')
        rows=[]
        index=[]
        timecol=self.colnames.index('time')
        for line in self.data:
            line=line.replace(' \n','')
            line=line.split(' ')
            line=[item for item in line]
            index.append(datetime.datetime.fromisoformat("%s %s:%s:%s.%s" %(
                self.start,
                line[timecol][0:2],
                line[timecol][2:4],
                line[timecol][4:6],
                line[timecol].split('.')[1])))
            line=numpy.array(line).astype(numpy.float)
            rows.append(line)
        df=pandas.DataFrame(rows,columns=self.colnames)
        df['time']=index

        # changing the time to datetime
        df['time']=pandas.to_datetime(df['time'])
        df.set_index('time',drop=True, inplace=True)
        df['offset']=df.index.astype('int64')/10**9
        df['offset']=df['offset'].diff()
        df['offset'].iloc[0]=0
        df['offset']=df['offset'].cumsum()
        self.df=df
        # TODO convert time zone
        #data.index=data.index.tz_localize('UTC').tz_convert('US/Central')

    def __sorting(self,lines):
        try:
            current=[]
            while True:
                line=lines.pop(0)
                #if line=='':
                #    continue
                if line=='\n':
                    continue           
                match line:
                    case '[column names]\n':
                        logging.info('Processing column names')
                        current=self.colnames
                    case '[data]\n':
                        print('Processing data section')
                        current=self.data
                    case _:
                        current.append(line)
        except Exception as e:
            print(str(e))
