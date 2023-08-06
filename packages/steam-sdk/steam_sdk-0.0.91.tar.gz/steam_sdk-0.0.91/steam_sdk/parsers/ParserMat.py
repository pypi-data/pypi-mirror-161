import os
import numpy as np
import pandas as pd
import h5py


def getSignalMat(path_sim, simNumber, list_Signals):

    simulationSignalsToPlot = pd.DataFrame()

    for i in range(len(simNumber)):
        path_simulationSignals = os.path.join(path_sim + str(simNumber[i]) + '.mat')
        with h5py.File(path_simulationSignals, 'r') as simulationSignals:
            for n in range(len(list_Signals)):
                simulationSignal = np.array(simulationSignals[list_Signals[n]])
                simulationSignal = simulationSignal.flatten().tolist()
                simulationSignal.insert(0, list_Signals[n]+'_'+str(simNumber[i]))
                simulationSignal = [simulationSignal]
                temp_frame = pd.DataFrame(simulationSignal)
                temp_frame.set_index(0, inplace=True)
                simulationSignalsToPlot = simulationSignalsToPlot.append(temp_frame)
    return simulationSignalsToPlot


def get_signals_from_mat(full_name_file: str, list_signals):
    '''
    Reads a mat file and returns a dataframe with the selected signals

    Note: The selected signals can also be define with a special syntax that allows accessing one certain row or column (1-indexed).
          Example: U_CoilSections(:,2) allows reading the 2nd column of the variable named U_CoilSections
          Example: U_CoilSections(3,:) allows reading the 3rd row of the variable named U_CoilSections
          Multiple columns/rows selection not currently supported  #TODO it would be nice to add

    :param full_name_file: full path to the mat file
    :param list_signals: list of signals to read
    :return: dataframe with the selected signals
    '''

    with h5py.File(full_name_file, 'r') as simulationSignals:
        df_signals = pd.DataFrame()
        for label_signal in list_signals:
            if ('(' in label_signal) and (')' in label_signal):
                # Special case: Only certain columns will be read
                label_signal_split = label_signal.split('(')
                signal = label_signal_split[0]
                rows_columns = label_signal_split[1].rstrip(')').split(',')
                label_rows    = rows_columns[0]
                label_columns = rows_columns[1]

                # Find slice of selected rows
                if label_rows == ':':
                    rows = slice(0, simulationSignals[signal].shape[1] - 1)
                elif ':' in label_rows:
                    raise Exception('Multiple rows selection not currently supported.')
                    # label_rows_split = label_rows.split(':')
                    # rows = slice(int(label_rows_split[0]) - 1, int(label_rows_split[1]) - 1)
                else:
                    rows = int(label_rows)

                # Find slice of selected columns
                if label_columns == ':':
                    columns = slice(0, simulationSignals[signal].shape[0]-1)
                elif ':' in label_columns:
                    raise Exception('Multiple columns selection not currently supported.')
                    # label_columns_split = label_columns.split(':')
                    # columns = slice(int(label_columns_split[0])-1, int(label_columns_split[1])-1)
                else:
                    columns = int(label_columns)-1

                # Apply slices
                simulationSignal = np.array(simulationSignals[signal][rows][columns])
            else:
                # Regular case: One-column signal is read
                signal = label_signal
                simulationSignal = np.array(simulationSignals[signal])

            simulationSignal = simulationSignal.flatten().tolist()
            df = pd.DataFrame({label_signal: simulationSignal})
            df_signals = pd.concat([df_signals, df], axis=1)
    return df_signals
