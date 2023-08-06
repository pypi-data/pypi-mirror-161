import os
from pathlib import Path
from typing import List
import numpy as np
import pandas as pd
import yaml

import matplotlib.pyplot as plt
from steam_sdk.data.DataSignal import DataSignal

from steam_sdk.parsers.ParserMat import get_signals_from_mat
from steam_sdk.parsers.ParserCsv import get_signals_from_csv
from steam_sdk.parsers.ParserTdms import ParserTdms
from steam_sdk.utils.make_folder_if_not_existing import make_folder_if_not_existing
from steam_sdk.utils.unique import unique
from steam_sdk.utils.isNaN import isNaN



class Viewer:
    """
        Class with methods to read and view simulation files
    """

    def __init__(self, file_name_transients: str,
                 list_events: List[int] = [],
                 flag_analyze: bool = True,
                 flag_display: bool = False,
                 flag_save_figures: bool = False,
                 verbose: bool = False):
        '''
            Initialization using the paths to the simulation data

            :param file_name_transients: full path to the input file containing the list of transients to analyze
            :param list_events: list of integers defining the events to process. Index=1 refers to the first event, at row 2 (first line is a header). If left an empty list, all events in the file are processed (default).
            :param flag_analyze: if flag_analyze=True, run the analysis directly during the object initialization
            :param flag_display: If flag_display=True, the figures will be displayed
            :param flag_save_figures: if flag_save_figures=True, figures will be saved in the figure output folder defined in the input file
            :param verbose: If verbose=True, additional information will be displayed during the run

            TO BE CONSIDERED TO ADD
            :param flag_metrics
            :param list_combined_plots: List of lists defining plots that include more than one event

            THESE WILL BE ADDED TO THE INPUT FILE
            :param path_input_simulation_files: folder where the different simulation files are stored (subfolders to be defined)
            :param path_output_simulation_files: root folder where the simulation files will be copied/pasted for semi-public access (suffix will be appended with dedicated key, for example "\LHC\MQY\"), \\eosproject-smb\eos\project\s\steam\STEAM_simulationResults
        '''

        # Assign inputs
        self.verbose = verbose
        self.flag_display = flag_display
        self.flag_save_figures = flag_save_figures
        self.file_name_transients = file_name_transients

        # Initialize empty variables
        self.dict_configs = {}  # this dictionary will contain all configurations, which define which measured and simulated signals are acquired
        self.dict_data    = {}  # this dictionary will contain all event data. Each event includes a combination of measured data, simulated data, or both, including multipliers

        # Initialize by reading the input file
        if self.verbose:
            print(f'Reading file {file_name_transients}')
        data_events_df = pd.read_csv(file_name_transients)  # read file into a dataframe
        self.dict_events = dict(zip(data_events_df, data_events_df.values.T))  # convert dataframe to dictionary
        if self.verbose:
            print('Read dictionary:')
            for key, value in self.dict_events.items():
                print(f'{key}: {value}')
        n_events = len(data_events_df.index)

        # Define the list of events to process
        if list_events == []:
            self.list_events = list(np.linspace(1, n_events, n_events, dtype=int))
        else:
            self.list_events = list_events
        if self.verbose:
            print(f'Selected events: {self.list_events}')

        # Read the configurations for all events
        self.read_configurations()

        # Convert the measurement files, when specified in the event file
        self.convert_meas_files()

        # Convert the simulation files, when specified in the event file

        # Run the analysis directly during initialization (optional)
        if flag_analyze:
            self.run_analysis()


    def read_configurations(self):
        '''
        Read the configurations required for all the events, and store them in the dictionary self.dict_configs
        Note: Known issue If two configurations from different configuration files have the same name, the configuration will be overwritten
        :return: None
        '''
        # Unpack inputs
        verbose = self.verbose
        list_events = self.list_events
        dict_events = self.dict_events

        if verbose: print('### Read configurations. ###')

        # For each selected row of the events file, read the selected data
        for t in list_events:
            event_label = dict_events['Event label'][t-1]
            configuration_file = Path(dict_events['Configuration file'][t-1]).resolve()
            configuration_name = dict_events['Configuration'][t-1]
            if verbose: print(f'Row {t}: Event: {event_label}. Configuration {configuration_name} from file {configuration_file}.')

            # Check that the configuration file exists
            if not os.path.isfile(configuration_file):
                raise Exception(f'Configuration file {configuration_file} missing.')

            # Read configuration file (note: different events can use different configuration files)
            temp_dict_here = yaml.safe_load(open(configuration_file))
            current_configuration_file = DataSignal(**temp_dict_here)
            if not configuration_name in current_configuration_file.ConfigurationList:
                raise Exception(f'Row {t}: Event: {event_label}. Configuration {configuration_name} is not present in file {configuration_file}.')

            # Assign the selected one configuration to the object attribute
            self.dict_configs[configuration_name] = current_configuration_file.ConfigurationList[configuration_name]
            if verbose:
                print('Read signal list:')
                for signal in self.dict_configs[configuration_name].SignalList:
                    print(f'{signal}')


    def convert_meas_files(self):
        '''
        Convert the measurement files, when required from flag_convert_meas_csv (checked for each individual event)
        :return: None
        '''

        # Unpack inputs
        verbose = self.verbose
        dict_configs = self.dict_configs
        list_events = self.list_events
        dict_events = self.dict_events

        if verbose: print('### Check whether measurement files are required to be converted to .csv files. ###')

        for t in list_events:
            # event_label = dict_events['Event label'][t-1]

            # Get flag indicating whether the measurement file should be converted to csv
            flag_convert_meas_csv = dict_events['flag_convert_meas_csv'][t-1]

            if flag_convert_meas_csv == 0 or isNaN(flag_convert_meas_csv):
                if verbose: print(f'Row {t}: flag_convert_meas_csv={flag_convert_meas_csv}: Measurement file not converted to csv.')
                continue  # if flag_convert_meas_csv=0, the file of this event will not be converted: go to the next event

            # Identify measurement file
            measurement_folder = dict_events['Measurement folder'][t-1]
            campaign = dict_events['Test campaign'][t-1]
            meas = dict_events['Test name'][t-1]
            path_output_measurement_files = dict_events['path_output_measurement_files'][t-1]

            if isNaN(measurement_folder) or isNaN(meas) or isNaN(campaign):
                print(f'Row {t}: flag_convert_meas_csv={flag_convert_meas_csv}: WARNING. flag_convert_meas_csv=1, but measurement file (Measurement folder, Test campaign, Test name) not defined.')
                continue  # Measurement file not defined: go to the next event
            if isNaN(path_output_measurement_files):
                print(f'Row {t}: flag_convert_meas_csv={flag_convert_meas_csv}: WARNING. flag_convert_meas_csv=1, but output folder for converted files (path_output_measurement_files) not defined.')
                continue  # Measurement file not defined: go to the next event

            # Compile a list of the signal groups that are requested in the configuration file (only the data of those groups will be converted)
            requested_groups = []
            configuration_name = dict_events['Configuration'][t-1]
            configuration      = dict_configs[configuration_name]

            for signal in configuration.SignalList:
                meas_signals_to_add = signal.meas_signals_to_add_x + signal.meas_signals_to_add_y
                for s, _ in enumerate(meas_signals_to_add):
                    group_name = meas_signals_to_add[s].split('.')[0]  # group where the current signal is located
                    requested_groups.append(group_name)
            requested_groups = unique(requested_groups)  # Delete elements that appear twice in these two lists
            if verbose: print(f'Row {t}: Requested groups: {requested_groups}.')

            # Check that the measurement file exists
            full_path_meas_file     = Path(os.path.join(measurement_folder, campaign, meas + '.tdms')).resolve()
            path_meas_csv_folder    = Path(os.path.join(path_output_measurement_files, campaign)).resolve()  # each subfolder in this folder represents a test campaign
            full_path_meas_csv_file = Path(os.path.join(path_meas_csv_folder, meas + '.csv')).resolve()
            if not os.path.isfile(full_path_meas_file):
                raise Exception(f'Row {t}: flag_convert_meas_csv={flag_convert_meas_csv}: Measurement file {full_path_meas_file} not found.')

            # Convert the requested groups of the .tdms file to separate .csv files
            if flag_convert_meas_csv == 1:
                tdms_file = ParserTdms(full_path_meas_file)
                tdms_file.convertTdmsToCsv(full_path_meas_csv_file, selected_groups= requested_groups, flag_overwrite=False)  # do not overwrite existing files
            elif flag_convert_meas_csv == 2:
                tdms_file = ParserTdms(full_path_meas_file)
                tdms_file.convertTdmsToCsv(full_path_meas_csv_file, selected_groups= requested_groups, flag_overwrite=True)  # overwrite existing files
            else:
                raise Exception(f'Entry flag_convert_meas_csv={flag_convert_meas_csv} in the event file {self.file_name_transients} is not supported.')


    def run_analysis(self):
        '''
        Perform the analysis. This is the core method of the class
        :return: None
        '''
        # Unpack inputs
        verbose = self.verbose
        dict_configs = self.dict_configs
        dict_events = self.dict_events
        list_events = self.list_events


        if verbose: print('### Perform analysis. ###')

        for t in list_events:
            # Acquire configuration for this event
            event_label        = dict_events['Event label'][t-1]
            configuration_name = dict_events['Configuration'][t-1]
            configuration      = dict_configs[configuration_name]
            if verbose: print(f'Row {t}: Event: {event_label}. Configuration: {configuration_name}')

            # Initialize dictionary key
            self.dict_data[event_label] = {}

            # Acquire measurement data for this event and store them in a temporary dictionary (probably more efficient than acquiring one signal at a time)
            path_output_measurement_files = dict_events['path_output_measurement_files'][t-1]
            measurement_folder            = dict_events['Measurement folder'][t-1]
            campaign                      = dict_events['Test campaign'][t-1]
            meas                          = dict_events['Test name'][t-1]
            temp_dict_meas = {}
            for signal in configuration.SignalList:  # a signal can include multiple meas, sim, or both signals/channels
                meas_signals_to_add = signal.meas_signals_to_add_x + signal.meas_signals_to_add_y
                for s, _ in enumerate(meas_signals_to_add):
                    group_name  = meas_signals_to_add[s].split('.')[0]  # group where the current signal is located
                    signal_name = meas_signals_to_add[s].split('.')[1]  # current signal, i.e. channel
                    full_path_csv_file  = Path(os.path.join(path_output_measurement_files, campaign, meas + '_' + group_name + '.csv')).resolve()
                    full_path_tdms_file = Path(os.path.join(measurement_folder,            campaign, meas + '.tdms')).resolve()

                    # If the data from the current group has not been read yet, read it now
                    if group_name not in temp_dict_meas:
                        # Try to read first from the converted .csv files, otherwise from the original .tdms files, otherwise raise an exception
                        if os.path.isfile(full_path_csv_file):
                            if verbose: print(f'Reading file {full_path_csv_file}.')
                            df_meas_data = pd.read_csv(full_path_csv_file)
                        elif os.path.isfile(full_path_tdms_file):
                            if verbose: print(f'Reading file {full_path_tdms_file}.')
                            tdms_file = ParserTdms(full_path_tdms_file)
                            dict_groups_signals = tdms_file.convertTdmsToDict(selected_groups=[group_name])
                            df_meas_data = dict_groups_signals[group_name]
                        else:
                            raise Exception(f'Neither file {full_path_csv_file} nor {full_path_tdms_file} was found.')
                    temp_dict_meas[group_name] = df_meas_data

            # Acquire all simulation data for this event
            sim_folder = dict_events['Simulation folder'][t-1]
            sim_file   = dict_events['Simulation file'][t-1]
            if type(sim_folder) == str and type(sim_file) == str:
                full_path_sim_file = Path(os.path.join(sim_folder, sim_file)).resolve()
                if not os.path.isfile(full_path_sim_file):
                    raise Exception(f'Simulation file {full_path_sim_file} missing.')

                # Identify simulation signals and time vectors required for this event
                signal_list_sim = []
                for signal in configuration.SignalList:
                    if (len(signal.sim_signals_to_add_x) > 0) and (len(signal.sim_signals_to_add_y) > 0):
                        signal_list_sim = signal_list_sim + signal.sim_signals_to_add_x + signal.sim_signals_to_add_y
                # Delete elements that appear twice in these two lists
                signal_list_sim = unique(signal_list_sim)
                if verbose: print(f'signal_list_sim: {signal_list_sim}')

                # If the file is a mat file, read it and convert the csv file to the output csv sim folder
                file_type = str(full_path_sim_file).split('.')[-1]
                if verbose: print(f'Reading file {full_path_sim_file}.')
                if file_type == 'csv':
                    df_sim_data = get_signals_from_csv(full_path_sim_file, signal_list_sim)
                elif file_type == 'mat':
                    df_sim_data = get_signals_from_mat(full_path_sim_file, signal_list_sim)
                else:
                    raise Exception(f'File type {file_type} not supported.')
            else:
                df_sim_data = pd.DataFrame([])
                print(f'Row {t}: Event: {event_label}: Simulation data not requested for this event.')


            # Calculate the desired measured and simulated signals by combining the acquired channels and accounting for the selected multipliers
            for signal in configuration.SignalList:  # a signal can include multiple meas, sim, or both signals/channels
                # Measured signal
                meas_signals_to_add_x = signal.meas_signals_to_add_x
                meas_signals_to_add_y = signal.meas_signals_to_add_y
                meas_multipliers_x    = signal.meas_multipliers_x
                meas_multipliers_y    = signal.meas_multipliers_y
                meas_offsets_x        = signal.meas_offsets_x
                meas_offsets_y        = signal.meas_offsets_y
                # Calculate the sum of signals after applying multipliers (first) and offsets (after)
                combined_signal_meas_x = self._multipliers_offsets_sum(temp_dict_meas, meas_signals_to_add_x, meas_multipliers_x, meas_offsets_x, data_type='dict_groups')
                combined_signal_meas_y = self._multipliers_offsets_sum(temp_dict_meas, meas_signals_to_add_y, meas_multipliers_y, meas_offsets_y, data_type='dict_groups')

                # Simulated signal
                sim_signals_to_add_x = signal.sim_signals_to_add_x
                sim_signals_to_add_y = signal.sim_signals_to_add_y
                sim_multipliers_x    = signal.sim_multipliers_x
                sim_multipliers_y    = signal.sim_multipliers_y
                sim_offsets_x        = signal.sim_offsets_x
                sim_offsets_y        = signal.sim_offsets_y
                # Calculate the sum of signals after applying multipliers (first) and offsets (after)
                combined_signal_sim_x = self._multipliers_offsets_sum(df_sim_data, sim_signals_to_add_x, sim_multipliers_x, sim_offsets_x, data_type='dataframe')
                combined_signal_sim_y = self._multipliers_offsets_sum(df_sim_data, sim_signals_to_add_y, sim_multipliers_y, sim_offsets_y, data_type='dataframe')

                # Assign signals to the main dictionary
                meas_label = signal.meas_label
                sim_label  = signal.sim_label
                if (len(temp_dict_meas) > 0) and (len(combined_signal_meas_x) > 0) and (len(combined_signal_meas_y) > 0):
                    self.dict_data[event_label][meas_label] = {}
                    self.dict_data[event_label][meas_label]['x_meas'] = combined_signal_meas_x
                    self.dict_data[event_label][meas_label]['y_meas'] = combined_signal_meas_y
                if (len(combined_signal_sim_x) > 0) and (len(combined_signal_sim_y) > 0):
                    self.dict_data[event_label][sim_label] = {}
                    self.dict_data[event_label][sim_label]['x_sim']  = combined_signal_sim_x
                    self.dict_data[event_label][sim_label]['y_sim']  = combined_signal_sim_y


                # Plot current signal (meas, or sim, or both) of the current event
                path_output_figures = dict_events['path_output_figures'][t-1]
                if self.flag_save_figures:
                    fig_name    = signal.name
                    figure_name = f'{event_label}_{fig_name}.png'
                    full_path_figure_to_save = os.path.join(path_output_figures, figure_name)
                    if verbose: print(f'Figure {full_path_figure_to_save} will be saved.')
                    fig_options = {
                        'fig_title':   signal.fig_title,
                        'fig_label_x': signal.fig_label_x,
                        'fig_label_y': signal.fig_label_y,
                        'fig_range_x': signal.fig_range_x,
                        'fig_range_y': signal.fig_range_y,
                    }

                else:
                    full_path_figure_to_save = None
                self.plot_signal(event_label, meas_label, sim_label, fig_options, self.flag_display, full_path_figure_to_save)

                ## TODO Analyze metrics


    def plot_signal(self, event_label: str, meas_label: str, sim_label: str, fig_options: dict, flag_display: bool = True, full_path_figure_to_save: str = None):
        '''
        # Plot a selected signal (meas, or sim, or both) of a selected event
        :param event_label: Name identifying the event to plot
        :param meas_label : Name identifying the measurement signal (it might be None)
        :param sim_label  : Name identifying the simulation signal (it might be None)
        :param fig_options: Dictionary of figure options:
                            - fig_title:   Title
                            - fig_label_x: Label of x axis
                            - fig_label_y: Label of y axis
                            - fig_range_x: Pair of float defining the x plot range
                            - fig_range_y: Pair of float defining the y plot range
        :param flag_display: If flag_display=True, the figure is displayed (they can still be saved)
        :param full_path_figure_to_save: Full path of the desired output figure. If None, the figure is not saved
        :return: Handles to the figure and its axis
        '''
        # If the output folder does not exist, make it now
        make_folder_if_not_existing(os.path.dirname(full_path_figure_to_save))

        # Unpack input data
        if meas_label:
            x_meas = self.dict_data[event_label][meas_label]['x_meas']
            y_meas = self.dict_data[event_label][meas_label]['y_meas']
        if sim_label:
            x_sim = self.dict_data[event_label][sim_label]['x_sim']
            y_sim = self.dict_data[event_label][sim_label]['y_sim']
        # Unpack figure options
        if ('fig_title'   in fig_options): fig_title   = fig_options['fig_title']
        if ('fig_label_x' in fig_options): fig_label_x = fig_options['fig_label_x']
        if ('fig_label_y' in fig_options): fig_label_y = fig_options['fig_label_y']
        if ('fig_range_x' in fig_options): fig_range_x = np.array(fig_options['fig_range_x'], dtype=np.float32)
        if ('fig_range_y' in fig_options): fig_range_y = np.array(fig_options['fig_range_y'], dtype=np.float32)

        # Set plot properties
        selectedFont = {'fontname': 'DejaVu Sans', 'size': 14}
        default_figsize = (12, 10)

        # Plot - Circuit current
        fig, ax = plt.subplots(1, 1, figsize=default_figsize)
        if meas_label:
            plt.plot(x_meas, y_meas, '.-', linewidth=1.0, color='r', label=meas_label)
        if sim_label:
            plt.plot(x_sim,  y_sim,  '-',  linewidth=1.0, color='b', label=sim_label)
        # Set figure options
        if fig_title:   plt.title(   fig_title, **selectedFont)
        if fig_label_x: plt.xlabel(fig_label_x, **selectedFont)
        if fig_label_y: plt.ylabel(fig_label_y, **selectedFont)
        if len(fig_range_x) == 2: plt.xlim(fig_range_x)
        if len(fig_range_y) == 2: plt.ylim(fig_range_y)
        plt.grid(True)
        plt.legend(loc='best')
        # plt.tight_layout()
        if flag_display:
            plt.show(block=True)  # show this figure
        if full_path_figure_to_save:
            plt.savefig(full_path_figure_to_save, format='png')  # Save figure
        return fig, ax


    # def plot_ViewerSim(self, data, titles, labels, types, texts, size, legends, style, window, scale, order):
    #     """
    #         Passes prepared inputs to the general plotter in PlotterModel
    #     """
    #     self.PM.plotterModel(data, titles, labels, types, texts, size, legends, style, window, scale, order)




    # Helper functions
    def _multipliers_offsets_sum(self, source_signals: dict, signals_to_add: list, multipliers: list = [], offsets: list = [], data_type: str = 'dataframe'):
        '''
        Calculate the sum of signals from a data source after applying multipliers and offsets (each signal can have different ones)
        :param signals_to_add: List of signals to sum
        :param multipliers: List of multipliers for the signals (applied before the offsets)
        :param offsets: List of offsets for the signals (applied after the multipliers)
        :param data_type: This identifies the way in which the data source is interpreted. Supported types are:
                          - 'dict_groups': Data stored in a dictionary organized in groups of signals
                          - 'dataframe': Data stored in a dataframe
        :return: panda series with the resulting signal
        '''
        # TODO Find a more elegant way to implement a scalar product for a pd.dataframe

        # If the list of signals to add is empty, return an empty pandas series
        n_signals_to_add = len(signals_to_add)
        if n_signals_to_add == 0:
            return pd.Series([], dtype=float)

        # If multipliers or offsets are empty lists, use default values (signals unchanged)
        if len(multipliers) == 0:
            multipliers = [1] * n_signals_to_add
        if len(offsets) == 0:
            offsets = [0] * n_signals_to_add

        # Apply multipliers, offsets, and sum the signals
        for s, _ in enumerate(signals_to_add):
            if data_type == 'dict_groups':
                group_name  = signals_to_add[s].split('.')[0]  # group where the current signal is located
                signal_name = signals_to_add[s].split('.')[1]  # current signal, i.e. channel
                if s == 0:
                    combined_signal = source_signals[group_name][signal_name] * multipliers[s] + offsets[s]
                else:
                    combined_signal = combined_signal + source_signals[group_name][signal_name] * multipliers[s] + offsets[s]
            elif data_type == 'dataframe':
                signal_name = signals_to_add[s]
                if s == 0:
                    combined_signal = source_signals[signal_name] * multipliers[s] + offsets[s]
                else:
                    combined_signal = combined_signal + source_signals[signal_name] * multipliers[s] + offsets[s]
            else:
                raise Exception(f'Data type not supported: data_type = {data_type}')
        return combined_signal