import os
import pandas as pd
import numpy as np

from pathlib import Path
from steam_sdk.parsers import ParserTdms
from steam_sdk.plotters.PlotterModel import PlotterModel


class ViewerMeas:
    """
        Class with methods to read and view measurement files (TDMS)
    """

    def __init__(self, path_meas: Path, path_output: Path, path_infotestCampaign: Path, list_testCampaigns: [], list_groupnames: [] = ['MF']):
        """
            Initialization using the paths to the measurement data
        """
        self.PM = PlotterModel()
        self.path_meas = path_meas  # where the different testCampaigns are stored
        self.path_infotestCampaign = path_infotestCampaign
        self.list_testCampaigns = list_testCampaigns  #testCampaigns that should be used, but then read_testCampaign has to be looped
        self.data_dict = {}  #structure: {'testCampaign1': {'TDMS_file1': {'Signal1': data (np.array)...
        self.tdms_file_names_dict = {}  # Dictionary of lists. Each dictionary contains a list with all the TDMS files present in a folder
        self.path_output = path_output  #path_output: path were signal_data of each TDMS file is re-written (optional)
        self.list_groupnames = list_groupnames  #list_groupnames: groups that have the desired signals, mostly MF -> ['MF'] #TODO: right now same for all testCampaigns, maybe change so each testCampaign can have their own groups
        if not os.path.isdir(self.path_output):
            os.makedirs(self.path_output)


    def read_testCampaign(self, name_testCampaign: str, flag_save: int = 0, header: int = 0):
        """
            Reads ONE testCampaign described in the infoTestCampaigns.csv file
            flag_save: signal data is stored in a seperate csv file (path_output)
        """

        # Read local information about the test-campaign signals
        path_testCampaign = Path(self.path_meas, name_testCampaign)  #TODO do we want to add the option to have a folder name different from the path_testCampaign?
        print('Test campaign ', name_testCampaign, ' in the folder ', path_testCampaign, '.')

        # Add testCampaign to the local dict to save the data
        self.data_dict[name_testCampaign] = {}

        # Load data
        data_infotestCampaign = pd.read_csv(self.path_infotestCampaign, header=header)

        # Get required signals
        signalsToRead = []
        for i in range(len(self.list_groupnames)):
            signalsToRead.append(self.identify_signals(name_testCampaign, self.list_groupnames[i], data_infotestCampaign))
        signalsToRead = [item for sublist in signalsToRead for item in sublist]  # flatten list

        # Find all .tdms files present in the test-campaign folder
        self.tdms_file_names_dict[name_testCampaign] = ParserTdms.getAllTDMSfiles(path_testCampaign)

        # Save all signals from each TDMS file
        for file in self.tdms_file_names_dict[name_testCampaign]:
            path_tdms = Path(path_testCampaign, file)
            PT = ParserTdms.ParserTdms(path_tdms)

            # dictionary of the signals (with their according group (in most cases MF)) that should be read from the TDMS
            dict_signals_tdms = {self.list_groupnames[0]: signalsToRead}  #TODO: if you have more than one groupname you are using for getting the signals, this needs to be looped to go all group_names, not just the first one
            # Get data
            PT.appendColumnToSignalData(dict_signals_tdms)

            # dictionary with signal_names and according data
            dict_signal_data = dict(zip(signalsToRead, PT.signal_data.T))

            # time-vector using first selected signal
            timeVector = PT.get_timeVector(self.list_groupnames[0], signalsToRead[0])
            dict_signal_data['timeVector'] = timeVector
            PT.signal_data = np.column_stack((PT.signal_data, timeVector))
            dict_signals_tdms[self.list_groupnames[0]].append('timeVector')

            # Store dict with data to dict of class to be accessible
            self.data_dict[name_testCampaign][file] = dict_signal_data

            # Save signals in .csv file
            if flag_save == 1:
                PT.writeTdmsToCsv(Path(self.path_output, file.replace('.tdms', '') + '.csv'), dict_signals_tdms)

            # Remove time_vector-name from dictionary of signal_names which was only there to put it in the csv
            dict_signals_tdms[self.list_groupnames[0]].remove('timeVector')

    def identify_signals(self, name_testCampaign: str, name_group: str, data_infotestCampaign):
        """
            Gets all signalnames of the specified group of testCampaign
            name_group: groups that should be looked inside for the desired signal
        """
        # Identify number of columns with signals to read
        num_col = len(data_infotestCampaign.filter(like='Signal', axis=1).columns)

        # Identify row with the information about this test campaign
        try:
            idx_row_campaign = data_infotestCampaign.index[data_infotestCampaign['Test campaign'] == name_testCampaign][0]
        except:
            raise Exception('Name of testCampaign is not found in the intended file!')

        # Identify names of the signals to read, and assign labels to them
        # Gets rid of group names
        signalsToRead_group = []

        for i in range(1, num_col+1):
            if name_group in data_infotestCampaign.iat[idx_row_campaign, i]:
                temp_str = data_infotestCampaign.iat[idx_row_campaign, i]
                temp_str = temp_str[temp_str.find('.')+1:]
                signalsToRead_group.append(temp_str)

        return signalsToRead_group

    def plot_ViewerMeas(self, data, titles, labels, types, texts, size, legends, style, window, scale, order):
        """
            Passes prepared inputs to the general plotter in PlotterModel
        """
        self.PM.plotterModel(data, titles, labels, types, texts, size, legends, style, window, scale, order)






