import time
from datetime import timedelta, date

def daterange(start_date, end_date, inclusive=True):
    if inclusive:
        included_dates = 1
    else:
        included_dates = 0
    for n in range(int((end_date-start_date).days+included_dates)):
        yield start_date + timedelta(n)

class timer ():
    def __init__(self,name=None) -> None:
        self.stopwatches = {'name':name,'start_time':time.time(),
                    'stop_time':None,'parent':None,'children':[],
                    'depth':0}
        self.current_stopwatch = self.stopwatches
    
    def reset(self) -> None:

        del self.stopwatches
        self.__init__()

    def start(self,name=None) -> None:
        stopwatch = {'name':name,'start_time':time.time(),'stop_time':None,
                'parent':self.current_stopwatch,'children':[],
                'depth':self.current_stopwatch['depth']+1}
        self.current_stopwatch['children'].append(stopwatch)
        self.current_stopwatch = self.current_stopwatch['children'][-1]

    def stop(self,print=False,units='auto',verbose=0) -> None:
        self.current_stopwatch['stop_time'] = time.time()
        if print:
            self.print(units=units,verbose=verbose)
        self.current_stopwatch = self.current_stopwatch['parent']

    def _print_stopwatch(self,stopwatch,units):
            batting = ""
            if stopwatch['stop_time'] is None:
                t = time.time() - stopwatch['start_time']
                batting = "*"
            else:
                t = stopwatch['stop_time'] - stopwatch['start_time']
            if units == 'seconds':
                t = round(t,2)
            elif units == 'milliseconds':
                t = round(t*1000,2)
            elif units == 'minutes':
                t = round(t/60,2)
            elif units == 'hours':
                t = round(t/3_600,2)
            elif units == 'days':
                t = round(t/86_400,2)
            elif units == 'auto':
                if t <= .1:
                    t = round(t*1000,2)
                    units = 'milliseconds'
                elif t < 60:
                    t = round(t,2)
                    units = 'seconds'
                elif t > 60:
                    t = round(t/60,2)
                    units = 'minutes'
                elif t > 3_600:
                    t = round(t/3_600,2)
                    units = 'hours'
                elif t > 86_400:
                    t = round(t/86_400,2)
                    units = 'days'
            
            print("\t"*stopwatch['depth'],f'''{stopwatch['name']} - {t} {units}{batting}''')

    def _print_stopwatch_and_children(self,stopwatch,units):
        self._print_stopwatch(stopwatch,units=units)
        for children_stopwatch in stopwatch['children']:
            self._print_stopwatch_and_children(children_stopwatch,units=units)

    def print(self,units='auto',verbose=0):
        
        if verbose==0:
            self._print_stopwatch(self.current_stopwatch,units=units)
        elif verbose==1:
            self._print_stopwatch(self.current_stopwatch['parent'],units=units)
            self._print_stopwatch(self.current_stopwatch,units=units)
        elif verbose==2:
            self._print_stopwatch_and_children(self.stopwatches,units=units)

if __name__ == '__main__':
    print("Yes")
    t = timer("Testing timer")
    time.sleep(2)
    t.start("Exterior")
    for i in range(4):
        t.start("i="+str(i))
        time.sleep(1)    
        if i==2:
            for j in range(5):
                t.start("j="+str(j))
                time.sleep(.04)
                t.stop(print=True,verbose=1)
        t.stop(print=True,verbose=1)
    t.stop(print=True,verbose=1)
    # t.print(verbose=2)