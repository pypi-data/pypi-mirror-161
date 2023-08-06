import os
from pathlib import Path
from steam_sdk.parsers.ParserMat import getSignalMat
from steam_sdk.parsers.ParserCsv import getSpecificSignalCSV
from steam_sdk.plotters.PlotterModel import PlotterModel

class ViewerSim:
    """
        Class with methods to read and view simulation files
    """

    def __init__(self, path_sim: str, model_name, simNumber, path_output: Path, list_Signals: [], file_type):
        """
            Initialization using the paths to the simulation data
        """
        self.PM = PlotterModel()
        self.path_sim = path_sim
        self.model_name = model_name
        self.simNumber = simNumber
        self.list_Signals = list_Signals
        self.path_output = path_output
        self.file_type = file_type
        if not os.path.isdir(self.path_output):
            os.makedirs(self.path_output)

    def read_simulationSignals(self):

        if self.file_type == 'mat':
            self.simulationSignalsToPlot = getSignalMat(self.path_sim, self.simNumber, self.list_Signals)
        elif self.file_type == 'csv':
            self.simulationSignalsToPlot = getSpecificSignalCSV(self.path_sim, self.model_name, self.simNumber, self.list_Signals)
        else:
            print('File type not supported')

        return self.simulationSignalsToPlot

    def plot_ViewerSim(self, data, titles, labels, types, texts, size, legends, style, window, scale, order):
        """
            Passes prepared inputs to the general plotter in PlotterModel
        """
        self.PM.plotterModel(data, titles, labels, types, texts, size, legends, style, window, scale, order)




