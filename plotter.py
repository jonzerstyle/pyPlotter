import multiprocessing as mp
import fileutils
import time
import matplotlib.pyplot as plt
import numpy as np
from pubsub import pub
from datetime import datetime
import csv
import glob
import os
import sys
#import ctypes

# signals needs to be of the form:
# [{'name': 'Signal1', 'x': [], 'y': [], 'color':'r', 'linewidth':1},
#  {'name': 'Signal2', 'x': [], 'y': [], 'color':'b', 'linewidth':3},
#  {'name': 'Signal3', 'x': [], 'y': [], 'color':'k', 'linewidth':2}]

class ProcessPlotter:
    def __init__(self, signals, plot_title='NA'):
        self.signals = signals
        self.plot_title = plot_title
        self.lastastime = time.time()

    def terminate(self):
        plt.close('all')

    def legend_without_duplicate_labels(self):
        handles, labels = self.ax.get_legend_handles_labels()
        unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
        self.ax.legend(*zip(*unique), fontsize = 'xx-small')

    def call_back(self):
        while self.pipe.poll():
            command = self.pipe.recv()
            if command is None:
                self.terminate()
                return False
            else:
                #command is of form ['signalName', [datetime.now(), newsample]]
                for _ in self.signals:
                        if _['name'] == command[0]:
                                _['x'].append(command[1][0])
                                _['y'].append(command[1][1])
                                #print(_)
                                self.ax.plot_date(_['x'], _['y'],
                                                  color=_['color'],
                                                  linewidth=_['linewidth'],
                                                  linestyle='solid',
                                                  label=_['name'])
                self.legend_without_duplicate_labels()
                #after 60 seconds autoscale no matter what
                #  is going on - in case user zoomed or scrolled
                if (time.time() - self.lastastime) > 60.0:
                        self.lastastime = time.time()
                        self.ax.autoscale()
        self.fig.canvas.draw()
        return True

    def onClick(self, event):
            #print('click')
            #if user clicks reset the autoscale timeout timer
            self.lastastime = time.time()

    def onClose(self, event):
            #print('plotter closed event!!!')
            self.queue.put(True)

    def __call__(self, pipe, queue):
        #print('starting plotter...')

        self.pipe = pipe
        self.queue = queue
        self.fig, self.ax = plt.subplots()
        self.fig.autofmt_xdate(rotation=45)
        self.ax.grid(True)
        self.ax.set_title(self.plot_title)
        self.fig.canvas.mpl_connect('button_press_event', self.onClick)
        self.fig.canvas.mpl_connect('close_event', self.onClose)
        self.fig.canvas.manager.set_window_title(self.plot_title)
        timer = self.fig.canvas.new_timer(interval=1000)
        timer.add_callback(self.call_back)
        timer.start()

        #print('...done')
        plt.show()

class Plot:
    def __init__(self, signals, interactive_plot=False, plot_title='NA',
                 read_csv_file='', createFile='False'):
        if interactive_plot == True:
           self.plot_pipe, plotter_pipe = mp.Pipe()
           self.plotter = ProcessPlotter(signals, plot_title=plot_title)
           self.queue = mp.Queue()
           self.plot_process = mp.Process(
               target=self.plotter, args=(plotter_pipe,self.queue,), daemon=True)
           self.plot_process.start()

        self.interactive_plot = interactive_plot
        self.closed_status = False

        if read_csv_file:
            with open(read_csv_file, newline='') as csvfile:
                signalList = []
                #commented out code was used to create a new csv file
                #  for the oven with the unsigned temperature converted
                #  to signed so that negative temperatures are represented
                #  correctly - leaving in as an example of how to use the
                #  the python to change the csv data
                #csvfile_conv = open("conv.csv", 'w', newline='')
                #csvwriter = csv.writer(csvfile_conv, delimiter=',')
                csvreader = csv.reader(csvfile, delimiter=',')
                for i, row in enumerate(csvreader):
                    #if row[0] == 'OvenTemp':
                    #   fnum = float(row[2]) * 10
                    #   inum = int(fnum)
                    #   snum = ctypes.c_short(inum).value
                    #   print(f'snum {snum}')
                    #   row[2] = snum / 10.0 
                    #csvwriter.writerow(row)
                    #print(row)
                    if i > 1:
                        found = False
                        for _ in signalList:
                            if row[0] == _['name']:  
                                #append values
                                _['x'].append(datetime.strptime(row[1], '%Y-%m-%d-%H:%M:%S'))
                                _['y'].append(float(row[2]))
                                found = True
                        if not found:
                            # To help avoid a white color keep picking random numbers
                            #   until one of the rgb elements is significantly lower than the other two
                            whiteVal = True
                            # Matplotlib colors are [0,1] not [0,255]
                            colorThresh = 15.0 / 255.0
                            while whiteVal:
                                r = np.round(np.random.rand(),1)
                                g = np.round(np.random.rand(),1)
                                b = np.round(np.random.rand(),1)
                                rgTb = (abs(r - g) < colorThresh)
                                rbTb = (abs(r - b) < colorThresh)
                                grTb = (abs(g - r) < colorThresh)
                                gbTb = (abs(r - b) < colorThresh)
                                brTb = (abs(b - r) < colorThresh)
                                bgTb = (abs(b - g) < colorThresh)
                                if rgTb and rbTb and grTb and gbTb and brTb and bgTb:
                                   # Colors don't meet threshold spec re-roll
                                   whiteVal = True
                                else:
                                   whiteVal = False

                            signalList.append({'name':row[0],'x':[datetime.strptime(row[1], '%Y-%m-%d-%H:%M:%S')],
                                               'y':[float(row[2])],'color':[r,g,b]})

            fig, ax = plt.subplots()
            fig.autofmt_xdate(rotation=45)
            ax.grid(True)
            ax.set_title(plot_title)
            for _ in signalList:
                ax.plot_date(_['x'], _['y'],
                             color=_['color'],
                             linewidth=1,
                             linestyle='solid',
                             label=_['name'])
            plt.legend()
            if createFile == 'True':
                plt.savefig(f'{plot_title}.png')
            plt.show()
        else:
            self._logfile=f'{plot_title}.csv'.replace(" ", "")
            self._openLogFile()
            self.csvwriter = csv.writer(self._file)
            self.csvwriter.writerow(['SignalName', 'DateTime', 'Value'])

    def plot(self, signalName, newsample, finished=False):
        if self.interactive_plot:
           send = self.plot_pipe.send

           if not self.queue.empty():
               self.closed_status = self.queue.get()

           if finished:
               send(None)
           elif self.closed_status == True:
               #print('plotter closed')
               #if self._file:
               #    self._file.close()
               #even if plot is closed keep logging
               pass
           else:
               #data = np.random.random(2)
               #print(data)
               data = [datetime.now(), newsample]
               #print(data)
               send([signalName, data])

        if self._file:
            data = [datetime.now(), newsample]
            #print(data)
            self.csvwriter.writerow([signalName,
                                     data[0].strftime("%Y-%m-%d-%H:%M:%S"),
                                     data[1]])
            self._file.flush()

    def stopPlot(self):
        self.closed_status = True
        #print('plotter closed')
        if self._file:
            self._file.close()
        pass

    def _openLogFile(self):
        # open the log file
        if self._logfile:
            self._file = fileutils.safeopenwrite(self._logfile, 'w')
        pass


def main():
    #Static plot example
    print(f'Number of args: {len(sys.argv)}')
    print(f'arguments: {str(sys.argv)}')
    if (len(sys.argv) > 2) and sys.argv[1]:
        list_of_files = glob.glob(sys.argv[1])
        latest_file = max(list_of_files, key=os.path.getctime)
        pl = Plot(None, read_csv_file=latest_file, interactive_plot=False, plot_title=latest_file.removesuffix('.csv'), 
                  createFile=sys.argv[2])
    else:
        print('Specify csv file pattern to plot latest file in arg1')
        print("  examples: 'Oven*.csv' 'SAAnlalogs*.csv' 'SBAnlalogs*.csv' 'SCAnlalogs*.csv' 'Thermo*.csv'")
        print("Specify arg2 as 'True' to create a png file otherwise 'False'")

    #Interactive plot example
    #signals = [{'name': 'Signal1', 'x': [], 'y': [], 'color':'r', 'linewidth':1},
    #           {'name': 'Signal2', 'x': [], 'y': [], 'color':'b', 'linewidth':3},
    #           {'name': 'Signal3', 'x': [], 'y': [], 'color':'k', 'linewidth':2}]
    #pli = Plot(signals, interactive_plot=True, plot_title='main-test')
    #for _ in range(10):
    #    pli.plot('Signal1', _ + 1)
    #    pli.plot('Signal2', _ + 2)
    #    pli.plot('Signal3', _ + 3)
    #    time.sleep(3.0)
    #pli.plot(None, None, finished=True)
    #pli.stopPlot()

if __name__ == '__main__':
    if plt.get_backend() == "MacOSX":
        mp.set_start_method("forkserver")
    main()
