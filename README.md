```
# pyPlotter
Python module that provides static and interactive plotting (interactive plotting can be leaky)

# Colors are used in interactive plotting - if pulling up static plots random colors are used 

# Example how to create csv file and plot to it.
from plotter import Plot
import ctypes

colors = []
colors.append([1.0,0,0])
colors.append([0,0,0])
colors.append([0,0,1.0])

plotObj = Plot([{'name': 'OvenTemp', 'x': [], 'y': [], 'color':colors[0], 'linewidth':1},
                {'name': 'StepNumber', 'x': [], 'y': [], 'color':colors[1], 'linewidth':1},
                {'name': 'JumpCnt', 'x': [], 'y': [], 'color':colors[2], 'linewidth':1}],
                  interactive_plot=False, plot_title='OvenPlot')

plotObj.plot('OvenTemp', (ctypes.c_short(val).value / 10.0))
plotObj.plot('JumpCnt', self.oven_state.jumpcnt)
plotObj.plot('StepNumber', self.oven_state.stepnum)

#on app shutdown
plotObj.stopPlot()

# Example how to pull up a static plot using pysimple GUI button
#   while inside a pysimpleGui app
    PLOT_ANALOGS = 'main.plot_analogs'

#  when creating GUI layout 
    sg.Button('Plot Analogs', button_color=('blue'), key=self.PLOT_ANALOGS

#  thread definition
    def _plot(self, csvfile, createPng):
        #Doing this issues warning matplotlib is not launched from main thread
        #  some time later it causes the app to stop running and closes the plot
        #Plot(None, read_csv_file=csvfile, interactive_plot=False, plot_title=csvfile.removesuffix('.csv'))
        #Using this method no warning and very stable - can pull up many plots and close them
        #  and it has no effect on the application
        os.system(f'python tcapp\plotter.py {csvfile} {createPng}')
        pass
        
#  handlers
    def _act_on_handle_Plot_Oven(self, createPng):
        self.printnlog('>>>> Plot_Oven <<<<')
        list_of_files = glob.glob('Oven*.csv')
        latest_file = max(list_of_files, key=os.path.getctime)
        t = Thread(target=self._plot, kwargs={'csvfile':latest_file, 'createPng':createPng})
        t.start()
        pass
    def _handle_Plot_Oven(self, win, event, values):
        self._act_on_handle_Plot_Oven('False')
        pass
    def registerEvents(self):
        self._win.registerHandler(self.PLOT_ANALOGS, self._handle_Plot_Analogs)
        pass
        
#   pull up plot in code without using button
                        #Bring up a Oven Plot
                        self._act_on_handle_Plot_Oven('True')
```
