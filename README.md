```
# pyPlotter
Python module that provides static and interactive plotting (interactive plotting can be leaky)

# Colors are used in interactive plotting - if pulling up static plots random colors are used 

# Example how to create csv file and plot to it.
See Interactive plot example commented out at bottom of main.
Change interactive_plot=False.
It will create csv main-test-X (X number that increments with new csv)
When not interactive no need to do pli.plot(None, None, finished=True)

# To display csv file
python plotter.py 'main-test*.csv' False

# When used in pysimple GUI it needs to be threaded
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

```
