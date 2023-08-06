import os
import datetime
import ntpath
import shutil
import textwrap
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
from scipy.interpolate import interp1d
import pandas as pd
import numpy as np

import yaml

from steam_sdk.data.DataModelCircuit import DataModelCircuit, Component
from steam_sdk.parsers.dict_to_yaml import dict_to_yaml


class ParserPSPICE:
    """
        Class with methods to read/write PSPICE information from/to other programs
    """

    def __init__(self, circuit_data: DataModelCircuit, path_input: Path = None, output_path: str = ''):
        """
            Initialization using a DataModelCircuit object containing circuit netlist structure
        """

        self.circuit_data: DataModelCircuit = circuit_data
        self.path_input: str = path_input
        self.output_path: str = output_path


    def read_netlist(self, full_path_file_name: str, flag_acquire_auxiliary_files: bool = False, verbose: bool = False):
        '''
        ** Reads a PSPICE netlist file **

        :param full_path_file_name:
        :param flag_acquire_auxiliary_files: If True, add list of additional files to circuit_data
        :param verbose:
        :return: ModelCircuit dataclass with filled keys
        '''

        # Initialize
        self.circuit_data = DataModelCircuit()
        self.circuit_data.InitialConditions.initial_conditions = {}
        # Set flags indicating that the last read line corresponds to an item that might span to the next line
        self._set_all_flags_to_false()

        with open(full_path_file_name) as file:
            for row, line in enumerate(file):
                if verbose: print(line.rstrip())

                # Reset all flags to False if the line does not contain '+' in first position (excluding whitespaces)
                # Note: When one of these flags is set to True it indicates that this line might contain additional parameters from the previous line
                if (not '+' in line) and (not line.strip(' ')[0] == '+'):
                    self._set_all_flags_to_false()

                # If the line is a comment, skip to the next
                if '*' in line and line[0] == '*':
                    continue
                # If the line is empty, skip to the next
                if line == [] or line == [''] or line == '\n':
                    continue
                # If the line is the ending command, skip to the next
                if '.END' in line:
                    continue

                # Remove spaces before and after the "=" equal sign to make the parser more robust
                line = line.replace(' =', '=')
                line = line.replace('= ', '=')

                # Read stimuli
                if '.STMLIB' in line:
                    line_split = line.rstrip('\n').split(' ')  # Note: .rstrip('\n') removes the endline. .spolit(' ') makes a list of space-divided strings
                    value = line_split[1].strip('"')  # Note: .strip('"') removes all " sybmbols from the string
                    self.circuit_data.Stimuli.stimulus_files.append(str(value))
                    continue

                # Read libraries
                if '.LIB' in line:
                    line_split = line.rstrip('\n').split(' ')
                    value = line_split[1].strip('"')
                    self.circuit_data.Libraries.component_libraries.append(str(value))
                    continue

                # Read global parameters
                if '.PARAM' in line:  # it also covers the case where ".PARAMS" is written
                    self.flag_read_global_parameters = True
                    self.circuit_data.GlobalParameters.global_parameters = {}
                    continue
                if self.flag_read_global_parameters and '+ ' in line:
                    line_split = line.rstrip('\n').split(' ')
                    line_split = line_split[1].split('=')
                    name  = line_split[0].strip('"')
                    value = line_split[1].strip('{').strip('}')
                    self.circuit_data.GlobalParameters.global_parameters[str(name)] = str(value)
                    continue

                # Read initial conditions
                # TODO: Known issue: this logic will not work if multiple initial conditions are defined in the same line
                if '.IC ' in line:
                    line_split = line.rstrip('\n').split('.IC ')
                    line_split = line_split[1].strip(' ').split(' ')  # remove whitespaces at the beginning and end of the string, then divide it at the internal whitespace
                    name  = line_split[0]
                    value = line_split[1].strip('{').strip('}')
                    self.circuit_data.InitialConditions.initial_conditions[str(name)] = str(value)
                    continue

                # Read options
                if '.OPTION' in line:  # it also covers the case where ".OPTIONS" is written
                    self.flag_read_options = True
                    self.circuit_data.Options.options_simulation = {}
                    continue
                if self.flag_read_options and '+ ' in line:
                    line_split = line.rstrip('\n').strip(' ').split(' ')
                    line_split = line_split[1].split('=')
                    name  = line_split[0].strip('"')
                    value = line_split[1].strip('{').strip('}')
                    self.circuit_data.Options.options_simulation[str(name)] = str(value)
                    continue

                # Read options
                if '.AUTOCONVERGE' in line:
                    self.flag_read_autoconverge = True
                    self.circuit_data.Options.options_autoconverge = {}
                    continue
                if self.flag_read_autoconverge and '+ ' in line:
                    line_split = line.rstrip('\n').strip(' ').split(' ')
                    line_split = line_split[1].split('=')
                    name  = line_split[0].strip('"')
                    value = line_split[1].strip('{').strip('}')
                    self.circuit_data.Options.options_autoconverge[str(name)] = str(value)
                    continue

                # Read analysis
                if '.TRAN' in line:
                    self.circuit_data.Analysis.analysis_type = 'transient'
                    line_split = line.rstrip('\n').split(' ')
                    self.circuit_data.Analysis.simulation_time.time_start = str(line_split[1])
                    self.circuit_data.Analysis.simulation_time.time_end = str(line_split[2])
                    if len(line_split) > 3:
                        self.circuit_data.Analysis.simulation_time.min_time_step = str(line_split[3])
                    continue
                elif '.AC' in line:
                    self.circuit_data.Analysis.analysis_type = 'frequency'
                    continue
                elif '.STEP' in line:
                    # TODO. Parametric analysis
                    continue

                # Read time schedule
                if '+ {SCHEDULE(' in line:
                    self.flag_read_time_schedule = True
                    self.circuit_data.Analysis.simulation_time.time_schedule = {}
                    continue
                # If the line is the end of the time schedule section, skip to the next
                if '+ )}' in line or '+)}' in line:
                    continue
                if self.flag_read_time_schedule and '+ ' in line:
                    line_split = line.rstrip('\n').split('+ ')
                    line_split = line_split[1].split(',')
                    name  = line_split[0].strip(' ').strip('\t').strip(' ')
                    value = line_split[1].strip(' ').strip('\t').strip(' ')
                    self.circuit_data.Analysis.simulation_time.time_schedule[str(name)] = str(value)
                    continue

                # Read probe
                if '.PROBE' in line:
                    if '/CSDF' in line:
                        self.circuit_data.PostProcess.probe.probe_type = 'CSDF'
                    else:
                        self.circuit_data.PostProcess.probe.probe_type = 'standard'
                    self.flag_read_probe = True
                    # TODO: Known issue: If probe variables are defined in this same line, they are ignored
                    continue
                if self.flag_read_probe and '+ ' in line:
                    line_split = line.rstrip('\n').split(' ')
                    value = line_split[1]
                    self.circuit_data.PostProcess.probe.variables.append(str(value))
                    continue

                # Read additional files
                if '.INC' in line:
                    line_split = line.rstrip('\n').split(' ')
                    value = line_split[1].strip('"')
                    self.circuit_data.AuxiliaryFiles.files_to_include.append(str(value))
                    continue

                    # TODO delete
                # # Read netlist - If this part of the code is reached without hitting "continue", it means that this
                # # line does not define a special command, and hence it defines a component of the netlist
                # if (not self.circuit_data.Netlist[0].name == None) and (not self.flag_read_parametrized_component):  # Append a new component (unless it is the first component)
                #     self.circuit_data.Netlist.append(Component_OLD())

                # Special case: Stimulus-controlled component
                if 'STIMULUS=' in line.replace(' ', ''):  # this covers the cases "STIMULUS = ", "STIMULUS=", etc
                    line_split = line.rstrip('\n').split('(')  # TODO: Improve the logic, which now fails if the value includes the character "("
                    name = str(line_split[0].strip(' '))
                    line_split = line_split[1].rstrip('\n').split(')')
                    nodes = line_split[0].split(' ')
                    line_split = line_split[1].split('=')
                    value = line_split[1].strip(' { } ')  # Strip spaces and bracket at the extremities
                    new_Component = Component()
                    new_Component.type = 'stimulus-controlled component'
                    new_Component.nodes = nodes
                    new_Component.value = str(value)
                    self.circuit_data.Netlist.__setattr__(name, new_Component)
                    continue

                # Special case: Pulsed power source
                if 'PULSE' in line.replace(' ', ''):
                    # Note: The following logic works for three different syntaxes: "PULSE(value)", "PULSE (value)" and "PULSE value"
                    line_before, _, line_after = line.rstrip('\n').partition('(')  # Take the part of the string before and after the first "(" char
                    name = str(line_before.strip(' '))
                    line_before, _, line_after = line_after.rstrip(' ').partition(')')  # Take the part of the string before and after the first ")" char
                    nodes = line_before.split(' ')
                    line_after = line_after.partition('PULSE')[2]  # Take the part of the string after the first "VALUE " chars
                    value = line_after.strip(' ( ) ')  # Strip spaces and bracket at the extremities
                    new_Component = Component()
                    new_Component.type = 'pulsed-source component'
                    new_Component.nodes = nodes
                    new_Component.value = str(value)
                    self.circuit_data.Netlist.__setattr__(name, new_Component)
                    continue

                # Special case: Controlled-source component
                # E: Voltage-controlled voltage source
                # F: Current-controlled current source
                # G: Voltage-controlled current source
                # H: Current-controlled voltage source
                # TODO Known issue: it fails to read correctly the nodes/parameters if the nodes contain brakets
                # TODO Known issue: it fails to read correctly E/F/G/H where "VALUE" is not present
                if ('VALUE' in line) and ((line[0] == 'E') or (line[0] == 'F') or (line[0] == 'G') or (line[0] == 'H')):
                    # Find the correct delimiter to cover multiple syntaxes
                    if 'VALUE = ' in line: delimiter_value = 'VALUE = '
                    elif 'VALUE =' in line: delimiter_value = 'VALUE ='
                    elif 'VALUE= ' in line: delimiter_value = 'VALUE= '
                    elif 'VALUE=' in line: delimiter_value = 'VALUE='
                    elif 'VALUE ' in line: delimiter_value = 'VALUE '

                    line_before, _, line_after = line.rstrip('\n').partition('(')  # Take the part of the string before and after the first "(" char
                    name = str(line_before.strip(' '))
                    line_before, _, line_after = line_after.rstrip(' ').partition(')')  # Take the part of the string before and after the first ")" char
                    nodes = line_before.split(' ')
                    line_after = line_after.partition(delimiter_value)[2]  # Take the part of the string after the first "delimiter_value" chars
                    value = line_after.strip(' { } ')  # Strip spaces and bracket at the extremities
                    new_Component = Component()
                    new_Component.type = 'controlled-source component'
                    new_Component.nodes = nodes
                    new_Component.value = str(value)
                    self.circuit_data.Netlist.__setattr__(name, new_Component)
                    continue

                # Special case: Parametrized component
                if ('x' in line and line[0] == 'x') or ('X' in line and line[0] == 'X'):
                    self.flag_read_parametrized_component = True
                    line_before, _, line_after = line.rstrip('\n').partition('(')  # Take the part of the string before and after the first "(" char
                    name = str(line_before.strip(' '))
                    line_before, _, line_after = line_after.rstrip(' ').partition(')')  # Take the part of the string before and after the first ")" char
                    nodes = line_before.split(' ')
                    value = line_after.strip(' { } ')  # Strip spaces and bracket at the extremities
                    self.name_last_component = name
                    new_Component = Component()
                    new_Component.type = 'parametrized component'
                    new_Component.nodes = nodes
                    new_Component.value = str(value)
                    self.circuit_data.Netlist.__setattr__(self.name_last_component, new_Component)
                    continue

                # Special case: Parameters of a parametrized component
                if self.flag_read_parametrized_component and '+ PARAM' in line:  # This line defines parameters of the component
                    # Reminder: This type of line looks like this: + PARAMS: name1={value1} name2={value2} name3={value3}
                    line_split = line.rstrip('\n').partition(':')[2]  # Take the part of the string after the first "+" char
                    # line_split = line.rstrip('\n').split(':')  # Split line in two, before and after the "+ PARAMS:" command
                    # line_split = line_split[1].strip(' ')      # Take the second element and remove whitespaces at its extremities
                    line_split = line_split.split(' ')         # Split into different parameters

                    continue_Component = getattr(self.circuit_data.Netlist, self.name_last_component)
                    for par in line_split:                     # Loop through the parameters
                        par_split = par.split('=')             # Split into name and value of the parameter
                        if len(par_split) == 2:                # Only take into account entries with two elements (for example, avoid None)
                            name_par = str(par_split[0].strip(' '))
                            value_par = str(par_split[1].strip(' { } '))  # Strip spaces and bracket at the extremities
                            continue_Component.parameters[str(name_par)] = str(value_par)
                    self.circuit_data.Netlist.__setattr__(self.name_last_component, continue_Component)
                    continue
                elif self.flag_read_parametrized_component and '+' in line and line[0] == '+':  # This line defines additional parameters of the component
                    # Reminder: This type of line looks like this: + PARAMS: name1={value1} name2={value2} name3={value3}
                    line_split = line.rstrip('\n').partition('+')[2]        # Take the part of the string after the first "+" char
                    line_split = line_split.split(' ')                      # Split into different parameters
                    continue_Component = getattr(self.circuit_data.Netlist, self.name_last_component)
                    for par in line_split:                                  # Loop through the parameters
                        par_split = par.split('=')                          # Split into name and value of the parameter
                        if len(par_split) == 2:                             # Only take into account entries with two elements (for example, avoid None)
                            name_par  = str(par_split[0].strip(' '))
                            value_par = str(par_split[1].strip(' { } '))  # Strip spaces and bracket at the extremities
                            continue_Component.parameters[str(name_par)] = str(value_par)
                    self.circuit_data.Netlist.__setattr__(self.name_last_component, continue_Component)
                    continue

                # If this part of the code is reached, the line defines standard component
                line_before, _, line_after = line.rstrip('\n').partition('(')  # Take the part of the string before and after the first "(" char
                name = line_before.strip(' ')
                line_before, _, line_after = line_after.rstrip(' ').partition(')')  # Take the part of the string before and after the first ")" char
                nodes = line_before.split(' ')
                value = line_after.strip(' { } ')  # Strip spaces and bracket at the extremities
                new_Component = Component()
                new_Component.type = 'standard component'
                new_Component.nodes = nodes
                new_Component.value = str(value)
                self.circuit_data.Netlist.__setattr__(name, new_Component)

        # Simplify options keys if they have default values
        if self.circuit_data.Options.options_simulation == get_default_options():
            print('Default simulation options are applied.')
            self.circuit_data.Options.options_simulation = {'all options': 'default'}
        if self.circuit_data.Options.options_autoconverge == get_default_autoconverge_options():
            print('Default simulation autoconvergence options are applied.')
            self.circuit_data.Options.options_autoconverge = {'all options': 'default'}

        if flag_acquire_auxiliary_files:
            # Read entries of required additional files and add them to the yaml dictionary
            # Add stimulus files (defined with ".STMLIB" option)
            for file in self.circuit_data.Stimuli.stimulus_files:
                self.circuit_data.GeneralParameters.additional_files.append(file)
            # Add component library files (defined with ".LIB" option)
            for file in self.circuit_data.Libraries.component_libraries:
                self.circuit_data.GeneralParameters.additional_files.append(file)
            # Add files to include (defined with ".INC" option)
            for file in self.circuit_data.AuxiliaryFiles.files_to_include:
                self.circuit_data.GeneralParameters.additional_files.append(file)
            if verbose:
                print('Option flag_acquire_auxiliary_files set to {}'.format(flag_acquire_auxiliary_files))
                for file in self.circuit_data.GeneralParameters.additional_files:
                    print('File {} added to the list of files to add to the model.'.format(file))

        return self.circuit_data

    def _set_all_flags_to_false(self):
        '''
            # Set flags indicating that the last read line corresponds to an item that might span to the next line
        '''
        self.flag_read_global_parameters = False
        self.flag_read_parametrized_component = False
        self.flag_read_options = False
        self.flag_read_autoconverge = False
        self.flag_read_time_schedule = False
        self.flag_read_probe = False
        self.name_last_component = None  # this is used to have the name of the latest added component (used to read the parameters of parametrized component over multiple rows)


    def write2pspice(self, full_path_file_name: str, verbose: bool = False):
        '''
        ** Writes a PSPICE netlist file **

        :param full_path_file_name:
        :param verbose:
        :return:
        '''

        # Prepare header
        time_start = datetime.datetime.now()
        rows_header = [
            add_comment('PSPICE Netlist Simulation File'),
            add_comment('Generated at {} at CERN using STEAM_SDK'.format(time_start)),
            add_comment('Authors: STEAM Team'),
        ]

        # Prepare stimuli
        rows_stimuli = []
        rows_stimuli.append(add_comment('**** Stimulus files ****'))  # Add header of this section
        if self.circuit_data.Stimuli.stimulus_files:
            for s in self.circuit_data.Stimuli.stimulus_files:
                rows_stimuli.append(add_stimulus(s))

        # Prepare libraries
        rows_libraries = []
        if self.circuit_data.Libraries.component_libraries:
            rows_libraries.append(add_comment('**** Component libraries ****'))  # Add header of this section
            for s in self.circuit_data.Libraries.component_libraries:
                rows_libraries.append(add_library(s))

        # Prepare global parameters
        rows_global_parameters = []
        if self.circuit_data.GlobalParameters.global_parameters:
            # Add comment and .PARAM command before the first entry
            rows_global_parameters.append(add_comment('**** Global parameters ****'))  # Add header of this section
            rows_global_parameters.append('.PARAM')  # Add header of this section
            # Add global parameter entries
            for name, value in self.circuit_data.GlobalParameters.global_parameters.items():
                rows_global_parameters.append(add_global_parameter(name, value))

        # Prepare initial conditions
        rows_initial_conditions = []
        if self.circuit_data.InitialConditions.initial_conditions:
            # Add comment and .PARAM command before the first entry
            rows_initial_conditions.append(add_comment('**** Initial conditions ****'))  # Add header of this section
            # Add initial condition entries
            for name, value in self.circuit_data.InitialConditions.initial_conditions.items():
                rows_initial_conditions.append(add_initial_condition(name, value))

        # Prepare netlist
        rows_netlist = []
        rows_netlist.append(add_comment('**** Netlist ****'))  # Add header of this section
        for s, name in enumerate(self.circuit_data.Netlist.__dict__.keys()):
            # Read keys
            type        = getattr(getattr(self.circuit_data.Netlist, name), 'type')
            nodes       = getattr(getattr(self.circuit_data.Netlist, name), 'nodes')
            value       = getattr(getattr(self.circuit_data.Netlist, name), 'value')
            parameters  = getattr(getattr(self.circuit_data.Netlist, name), 'parameters')
            # name, nodes, value, parameters, type = component.name, component.nodes, component.value, component.parameters, component.type

            # Check inputs
            if not type:
                raise Exception('At least one netlist entry of known type must be added. Supported component types:\n' +
                                '- comment\n' +
                                '- standard component\n'
                                '- stimulus-controlled component\n'
                                '- controlled-source component\n'
                                '- pulsed-source component\n'
                                '- parametrized component\n'
                                'Netlist cannot be generated.')

            # Add the relevant row depending on the component type
            if type == 'comment':
                if verbose: print('Netlist entry {} in position #{} is treated as a comment.'.format(name, s + 1))
                rows_netlist.append(add_comment(value))
            elif type == 'standard component':
                if name == None or nodes == None or value == None:
                    raise Exception('Netlist component in position #{} is of type {} and requires name, nodes, and value.'.format(s+1, type))
                if verbose: print('Netlist entry {} in position #{} is treated as a standard component.'.format(name, s + 1))
                rows_netlist.append(add_standard_component(name, nodes, value))
            elif type == 'stimulus-controlled component':
                if name == None or nodes == None or value == None:
                    raise Exception('Netlist component in position #{} is of type {} and requires name, nodes, and value.'.format(s+1, type))
                if verbose: print('Netlist entry {} in position #{} is treated as a stimulus-controlled component.'.format(name, s + 1))
                rows_netlist.append(add_stimulus_controlled_component(name, nodes, value))
            elif type == 'pulsed-source component':
                if name == None or nodes == None or value == None:
                    raise Exception('Netlist component in position #{} is of type {} and requires name, nodes, and value.'.format(s+1, type))
                if verbose: print('Netlist entry {} in position #{} is treated as a pulsed-source component.'.format(name, s + 1))
                rows_netlist.append(add_pulsed_source_component(name, nodes, value))
            elif type == 'controlled-source component':
                if name == None or nodes == None or value == None:
                    raise Exception('Netlist component in position #{} is of type {} and requires name, nodes, and value.'.format(s+1, type))
                if verbose: print('Netlist entry {} in position #{} is treated as a controlled-source component.'.format(name, s + 1))
                rows_netlist.append(add_controlled_source_component(name, nodes, value))
            elif type == 'parametrized component':
                if name == None or nodes == None or value == None:
                    raise Exception('Netlist component in position #{} is of type {} and requires name, nodes, and value.'.format(s+1, type))
                if verbose: print('Netlist entry {} in position #{} is treated as a parametrized component.'.format(name, s + 1))
                rows_netlist.append(add_parametrized_component(name, nodes, value, parameters))
            else:
                raise Exception ('Netlist entry {} in position #{} has an unknown type: {}.'.format(name, s+1, type))

        # Prepare options - Simulation options
        rows_options = []
        options = self.circuit_data.Options.options_simulation
        if options == {'all options': 'default'}:
            print('Default simulation options are applied.')
            options = get_default_options()
        if options:
            # Add comment and .OPTIONS command before the first entry
            rows_options.append(add_comment('**** Simulation parameters ****'))  # Add header of this section
            rows_options.append('.OPTIONS')  # Add header of this section
            # Add option entries
            for name, value in options.items():
                rows_options.append(add_option(name, value))

        # Prepare options - Autoconverge simulation options
        options_autoconverge = self.circuit_data.Options.options_autoconverge
        if options_autoconverge == {'all options': 'default'}:
            print('Default autoconverge simulation options_autoconverge are applied.')
            options_autoconverge = get_default_autoconverge_options()
        if options_autoconverge:
            # Add comment and .AUTOCONVERGE command before the first entry
            rows_options.append(add_comment('**** Simulation autoconverge options ****'))  # Add header of this section
            rows_options.append('.AUTOCONVERGE')  # Add header of this section
            # Add option entries
            for name, value in options_autoconverge.items():
                rows_options.append(add_option(name, value))

        # Prepare analysis settings
        rows_analysis = []
        analysis_type = self.circuit_data.Analysis.analysis_type
        if analysis_type == 'transient':
            # Unpack inputs
            time_start = self.circuit_data.Analysis.simulation_time.time_start
            time_end = self.circuit_data.Analysis.simulation_time.time_end
            min_time_step = self.circuit_data.Analysis.simulation_time.min_time_step
            time_schedule = self.circuit_data.Analysis.simulation_time.time_schedule
            # Check inputs
            if time_start == None:
                time_start = '0'
                print('Parameter time_start set to {} by default.'.format(time_start))
            if not time_end:
                raise Exception('When "transient" analysis is selected, parameter Analysis.simulation_time.time_end must be defined.')
            if not min_time_step:
                print('Parameter min_time_step was missing and it will not be written.')
            # Add analysis entry
            rows_analysis.append(add_transient_analysis(time_start, time_end, min_time_step))
            # If defined, add time schedule (varying minimum time stepping) entry
            if time_schedule and len(time_schedule) > 0:
                rows_analysis.append(add_transient_time_schedule(time_schedule))
        elif analysis_type == 'frequency':
            # TODO: frequency analysis. EXAMPLE: .AC DEC 50 1Hz 200kHz
            # TODO: DC analysis
            # TODO: parametric analysis. EXAMPLE: .STEP PARAM C_PARALLEL LIST 100n 250n 500n 750n 1u
            pass
        elif analysis_type == None:
            pass  # netlists can exist that do not have analysis set (for example, it could be defined in an auxiliary file)
        else:
            raise Exception('Analysis entry has an unknown type: {}.'.format(analysis_type))

        # Prepare post-processing settings
        rows_post_processing = []
        probe_type = self.circuit_data.PostProcess.probe.probe_type
        probe_variables = self.circuit_data.PostProcess.probe.variables
        if probe_type:
            rows_post_processing.append(add_probe(probe_type, probe_variables))

        # Prepare additional files to include
        rows_files_to_include = []
        for s in self.circuit_data.AuxiliaryFiles.files_to_include:
            rows_files_to_include.append(add_auxiliary_file(s))

        # Prepare file end
        rows_file_end = [add_end_file()]

        # Assemble all rows to write
        rows_to_write = \
            rows_header + \
            rows_stimuli + \
            rows_libraries + \
            rows_global_parameters + \
            rows_initial_conditions + \
            rows_netlist + \
            rows_options + \
            rows_analysis + \
            rows_post_processing + \
            rows_files_to_include + \
            rows_file_end

        # Write netlist file
        with open(full_path_file_name, 'w') as f:
            for row in rows_to_write:
                if verbose: print(row)
                f.write(row)
                f.write('\n')

        # Display time stamp
        time_written = datetime.datetime.now()
        if verbose:
            print(' ')
            print('Time stamp: ' + str(time_written))
            print('New file ' + full_path_file_name + ' generated.')


    def readFromYaml(self, full_path_file_name: str, verbose: bool = False):
        # Load yaml keys into DataModelCircuit dataclass
        with open(full_path_file_name, "r") as stream:
            dictionary_yaml = yaml.safe_load(stream)
            self.circuit_data = DataModelCircuit(**dictionary_yaml)
            for key in dictionary_yaml['Netlist'].keys():
                new_Component = Component(**dictionary_yaml['Netlist'][key])
                self.circuit_data.Netlist.__setattr__(key, new_Component)
        if verbose:
            print('File ' + full_path_file_name + ' read.')


    def write2yaml(self, full_path_file_name: str, verbose: bool = False):
        '''
        ** Write netlist to yaml file **
        :param full_path_file_name:
        :param verbose:
        :return:
        '''
        # This hard-coded list defines the keys that will NOT be written in a single row in the output yaml file
        list_exceptions = [
            'additional_files',
            'files_to_include',
            'stimulus_files',
            'component_libraries',
            'variables',
            ]

        all_data_dict = {**self.circuit_data.dict()}
        dict_to_yaml(all_data_dict, full_path_file_name, list_exceptions=list_exceptions)
        if verbose:
            print('New file ' + full_path_file_name + ' generated.')


    def copy_additional_files(self, verbose: bool = False):
        '''
            Copy additional files
        :return: Number of copied files
        '''
        for file_to_copy in self.circuit_data.GeneralParameters.additional_files:
            if not os.path.isabs(file_to_copy) and self.path_input:
                # If the provided path is relative, use the path_input as the root folder (if available)
                file_to_copy_relative = os.path.join(self.path_input, file_to_copy)
                file_to_copy = file_to_copy_relative
                if verbose:
                    print('Relative path changed from {} to {}.'.format(file_to_copy, file_to_copy_relative))

            file_name = ntpath.basename(file_to_copy)
            file_to_write = os.path.join(self.output_path, file_name)
            if os.path.isfile(os.path.join(file_to_copy)):
                print('File {} exists'.format(file_to_copy))
            else:
                print('File {} does not exist. Skipped.'.format(file_to_copy))
                continue
            if os.path.isdir(self.output_path):
                print('Dir {} exists'.format(self.output_path))
            else:
                print('Dir {} does not exist. Skipped.'.format(self.output_path))
                continue
            shutil.copyfile(Path(file_to_copy), Path(file_to_write))

            if verbose:
                print('Additional file copied from {} to {}.'.format(file_to_copy, file_to_write))
        return len(self.circuit_data.GeneralParameters.additional_files)


#######################  Helper functions - START  #######################
def add_comment(text: str):
    ''' Format comment row '''
    if text[0] == '*':
        return text  # If the input string starts with a "*", leave it unchanged (it is already a comment)
    formatted_text = '* ' + text
    return formatted_text

def add_stimulus(text: str):
    ''' Format stimulus row '''
    formatted_text = '.STMLIB ' + text
    return formatted_text

def add_library(text: str):
    ''' Format library row '''
    formatted_text = '.LIB \"' + text + '\"'
    return formatted_text

def add_global_parameter(name: str, value: str):
    ''' Format global parameters row '''
    formatted_text = '+ ' + name + '={' + str(value) + '}'
    return formatted_text

def add_initial_condition(name: str, value: str):
    ''' Format initial condition row '''
    formatted_text = '.IC ' + name + ' {' + str(value) + '}'
    return formatted_text

def add_standard_component(name: str, nodes: list, value: str):
    ''' Format standard component netlist row '''
    str_nodes = " ".join(nodes)  # string with space-separated nodes
    formatted_text = name + ' (' + str_nodes + ') ' + '{' + str(value) + '}'
    return formatted_text

def add_stimulus_controlled_component(name: str, nodes: list, value: str):
    ''' Format stimulus-controlled component netlist row '''
    str_nodes = " ".join(nodes)  # string with space-separated nodes
    str_stimulus = 'STIMULUS = ' + value
    formatted_text = name + ' (' + str_nodes + ') ' + str_stimulus
    return formatted_text

def add_pulsed_source_component(name: str, nodes: list, value: str):
    ''' Format pulsed-source component netlist row '''
    str_nodes = " ".join(nodes)  # string with space-separated nodes
    str_pulse = 'PULSE(' + str(value) + ')'
    formatted_text = name + ' (' + str_nodes + ') ' + str_pulse
    return formatted_text

def add_controlled_source_component(name: str, nodes: list, value: str):
    ''' Format controlled-source component netlist row '''
    str_nodes = " ".join(nodes)  # string with space-separated nodes
    str_stimulus = 'VALUE ' + '{' + value + '}'
    formatted_text = name + ' (' + str_nodes + ') ' + str_stimulus
    return formatted_text

def add_parametrized_component(name: str, nodes: list, value: str, parameters: dict):
    ''' Format parametrized component netlist row '''
    str_nodes = " ".join(nodes)  # string with space-separated nodes
    formatted_component = name + ' (' + str_nodes + ') ' + value  # First row, which defines the component
    if parameters:
        formatted_component = formatted_component + '\n'
        formatted_parameters = '+ PARAMS:'  # First part of the string in the second row, which defines the component parameters
        # for parameter in parameters:
        #     if len(parameter) != 2:
        #         raise Exception ('All parameters entries in a parametrized element must have 2 elements (name, value), but parameter {} has {} elements.'.format(name, len(parameter)))
        #     name_parameters, value_parameters = parameter[0], parameter[1]
        #     formatted_parameters = formatted_parameters + ' ' + name_parameters + '={' + value_parameters + '}'
        for name_parameters, value_parameters in parameters.items():
            # if len(parameter) != 2:
            #     raise Exception ('All parameters entries in a parametrized element must have 2 elements (name, value), but parameter {} has {} elements.'.format(name, len(parameter)))
            formatted_parameters = formatted_parameters + ' ' + name_parameters + '={' + value_parameters + '}'

        # Make sure the maximum number of characters in each row does not exceed 132, which is the maximum that PSPICE supports
        N_MAX_CHARS_PER_ROW = 130
        formatted_parameters = textwrap.fill(formatted_parameters, N_MAX_CHARS_PER_ROW)
        formatted_parameters = formatted_parameters.replace('\n', '\n+ ')  # Add "+ " at the beginning of each new line
    else:
        formatted_parameters = ''  # If no parameters are defined, empty string

    formatted_text = formatted_component + formatted_parameters  # Concatenate the two rows
    return formatted_text

def add_option(name: str, value: str):
    ''' Format option row '''
    formatted_text = '+ ' + name + '=' + value
    return formatted_text

def add_transient_analysis(time_start, time_end, min_time_step = None):
    ''' Format transient analysis row '''
    formatted_text = '.TRAN ' + str(time_start) + ' ' + str(time_end)
    if not min_time_step == None:
        formatted_text = formatted_text + ' ' + str(min_time_step)
    return formatted_text

def add_transient_time_schedule(time_schedule):
    ''' Format transient time schedule rows '''
    # If time_schedule is not defined, output will be None
    if time_schedule == None or len(time_schedule) == 0:
        return None

    formatted_text = '+ {SCHEDULE(\n'
    for time_window_start, time_step_in_window in time_schedule.items():
        if time_window_start == list(time_schedule.keys())[-1]:
            formatted_text = formatted_text + '+ ' + time_window_start + ', ' + time_step_in_window + '\n'  # the last entry must not have the comma
        else:
            formatted_text = formatted_text + '+ ' + time_window_start + ', ' + time_step_in_window + ',' + '\n'
    formatted_text = formatted_text + '+)}'
    return formatted_text

def add_probe(probe_type: str, probe_variables: list):
    ''' Format probe row '''
    if probe_type == 'standard':
        formatted_text = '.PROBE'
    elif probe_type == 'CSDF':
        formatted_text = '.PROBE/CSDF'
    elif not probe_type:
        return None
    else:
        raise Exception('Probe entry has an unknown type: {}.'.format(probe_type))

    for var in probe_variables:
        formatted_text = formatted_text + '\n' + '+ ' + var
    return formatted_text

def add_auxiliary_file(file_to_add: str):
    ''' Format auxiliary file rows '''
    formatted_text = '.INC ' + file_to_add
    return formatted_text

def add_end_file():
    formatted_text = '.END'
    return formatted_text

def get_default_options():
    options = {
        'RELTOL': '0.0001',
        'VNTOL': '0.00001',
        'ABSTOL': '0.0001',
        'CHGTOL': '0.000000000000001',
        'GMIN': '0.000000000001',
        'ITL1': '150',
        'ITL2': '20',
        'ITL4': '10',
        'TNOM': '27',
        'NUMDGT': '8',
    }
    return options

def get_default_autoconverge_options():
    options_autoconverge = {
        'RELTOL': '0.05',
        'VNTOL': '0.0001',
        'ABSTOL': '0.0001',
        'ITL1': '1000',
        'ITL2': '1000',
        'ITL4': '1000',
        'PIVTOL': '0.0000000001',
    }
    return options_autoconverge

def ComparePSPICEParameters(fileA, fileB):
    '''
        Compare all the variables imported from two PSPICE netlists
    '''

    pp_a = ParserPSPICE(None)
    pp_a.read_netlist(fileA, verbose=False)
    pp_b = ParserPSPICE(None)
    pp_b.read_netlist(fileB, verbose=False)
    print("Comparing File A: ({}) and File B: ({})".format(fileA, fileB))

    flag_equal = pp_a.circuit_data == pp_b.circuit_data
    return flag_equal

#######################  Helper functions - END  #######################

#######################  Interpolating Resistance ######################
def InterpolateResistance(current_level: float, path_resources: str, n_apertures: int = 2, Type: str = 'Linear', plot_interpolation: bool = False):
    '''
    Function to interpolate a resistance based on given, pre-calculated resistance values at different current level.
    2 different options are available: Linear or Spline interpolation. Interpolation is done at each timestep, with all
    available resistance values

    :param current_level: float, current level to be interpolated
    :param path_resources: str, path to the file with pre-calculated values
    :param n_apertures: int, Number of apertures to calculate a resistance for
    :param Type: str, either Linear or Spline, type of interpolation
    :param plot_interpolation: bool
    :return [time, new_R1, new_R2]: list of np.array, [time vector, resistance values for Ap. 1, Ap. 2]
    '''

    if Type not in ['Linear', 'Spline']:
        raise Exception(f'Type not understood. Chosen {Type} but only "Linear", "Spline" available.')

    ## Read the resistance values from a given file
    Intp_file = path_resources
    Intp_data = pd.read_csv(Intp_file, low_memory=False)
    col_t = []
    col_r1 = []
    col_r2 = []

    for col in Intp_data.columns:
        try:
            _ = int(col)
            idx = Intp_data.columns.get_loc(col)
            col_t.append(Intp_data.columns[idx]) # Time
            col_r1.append(Intp_data.columns[idx + 1]) # Aperture 1
            if n_apertures == 2: col_r2.append(Intp_data.columns[idx + 2]) # Aperture 2
        except:
            pass
    data_R1 = Intp_data[col_r1].drop([0]).to_numpy().astype(float)
    if n_apertures == 2:
        data_R2 = Intp_data[col_r2].drop([0]).to_numpy().astype(float)
    time = Intp_data[col_t[-1]].drop([0]).to_numpy().astype(float)

    ## Interpolate new current level based on given values
    new_R1 = []
    new_R2 = []
    current_level = np.array([current_level]).reshape(-1, 1)

    x = np.array(col_t).astype(float).reshape(-1, 1)

    # Loop through all time values, to obtain an interpolation for each time value
    for k in range(time.shape[0]):
        ## Start with interpolating values for R1 (aperture 1)
        # Obtain all resistance values of R1, available in the current time step (drop NaN)
        new_y = data_R1[k][~np.isnan(data_R1[k])].reshape(-1, )
        # Obtain the respective current values to the resistances
        new_x = x[~np.isnan(data_R1[k])].reshape(-1, )

        # 1. Available option: Spline interpolation (deprecated as poor performance)
        if Type == 'Spline':
            new_x = new_x[::-1]
            new_y = new_y[::-1]

            if len(new_x) <= 3:
                new_R1 = np.append(new_R1, np.nan)
            else:
                spl = UnivariateSpline(new_x, new_y)
                new_R1 = np.append(new_R1, spl(current_level))
        # 2. option: Linear interpolation
        elif Type == 'Linear':
            if current_level <= max(new_x):
                f = interp1d(new_x, new_y)
                new_R1 = np.append(new_R1, f(current_level))
            else:
                new_R1 = np.append(new_R1, np.nan)

        if n_apertures == 2:
            ## Repeat procedure for R2 (aperture 2)
            new_y = data_R2[k][~np.isnan(data_R2[k])].reshape(-1, )
            new_x = x[~np.isnan(data_R2[k])].reshape(-1, )
            if Type == 'Spline':
                new_x = new_x[::-1]
                new_y = new_y[::-1]

                if len(new_x) <= 3:
                    new_R1 = np.append(new_R1, np.nan)
                else:
                    spl = UnivariateSpline(new_x, new_y)
                    new_R2 = np.append(new_R2, spl(current_level))
            elif Type == 'Linear':
                try:
                    f = interp1d(new_x, new_y)
                    new_R2 = np.append(new_R2, f(current_level))
                except:
                    new_R2 = np.append(new_R2, np.nan)

    # Plot interpolation if wanted
    if plot_interpolation:
        f = plt.figure(figsize=(17, 8))
        plt.subplot(1, 2, 1)
        plt.plot(time, new_R1)
        leg = ["Interpolated-" + str(current_level)]
        for i in range(data_R1.shape[1]):
            plt.plot(time, data_R1[:, i])
            leg.append(x[i][0])
        plt.legend(leg)
        plt.xlabel('Time [s]')
        plt.ylabel('Resistance [Ohm]')
        plt.title('R_CoilSection 1')
        if n_apertures == 2:
            plt.subplot(1, 2, 2)
            plt.plot(time, new_R2)
            leg = ["Interpolated-" + str(current_level)]
            for i in range(data_R2.shape[1]):
                plt.plot(time, data_R2[:, i])
                leg.append(x[i][0])
            plt.legend(leg)
            plt.xlabel('Time [s]')
            plt.ylabel('Resistance [Ohm]')
            plt.title('R_CoilSection 2')
        f.suptitle(str(current_level[0][0]) + 'A', fontsize=16)
        plt.show()
    if n_apertures == 2:
        return [time, new_R1, new_R2]
    else:
        return [time, new_R1]


def writeStimuliFromInterpolation(current_level: list, n_total_magnets: int, n_apertures: int, magnets: list, tShift: list, Outputfile: str, path_resources: str,
                                  InterpolationType: str = 'Linear', type_stl: str = 'a', sparseTimeStepping: int = 100):
    '''
    Function to write a resistance stimuli for n apertures of a magnet for any current level. Resistance will be interpolated
    from pre-calculated values (see InterpolateResistance for closer explanation). Stimuli is then written in a .stl file for PSPICE

    :param current_level: list, all current level that shall be used for interpolation (each magnet has 1 current level)
    :param n_total_magnets: int, Number of total magnets in the circuit (A stimuli will be written for each, non-quenching = 0)
    :param n_apertures: int, Number of apertures per magnet. A stimuli will be written for each aperture for each magnet
    :param magnets: list, magnet numbers for which the stimuli shall be written
    :param tShift: list, time shift that needs to be applied to each stimuli
    (e.g. if magnet 1 quenches at 0.05s, magnet 2 at 1s etc.), so that the stimuli are applied at the correct time in the simulation
    :param Outputfile: str, name of the stimuli-file
    :param path_resources: str, path to the file with pre-calculated values
    :param Type: str, either Linear or Spline, type of interpolation
    :param type_stl: str, how to write the stimuli file (either 'a' (append) or 'w' (write))
    :param sparseTimeStepping: int, every x-th time value only a stimuli point is written (to reduce size of stimuli)
    :return:
    '''
    if n_apertures>2: raise Exception('Maximum of 2 apertures supported yet.')
    # Ensure consistency of inputs
    if len(magnets) != len(tShift): raise Exception(f'Please provide a time shift for each magnet. '
                                                    f'Size of magnet list is {len(magnets)}, but size of tShift is {len(tShift)}')

    R1 = np.array([])
    R2 = np.array([])
    print("Interpolating Coil-Resistances")
    # Interpolate data for each current level and ensure correct data format
    for k in current_level:
        if n_apertures == 2:
            [time, data_R1, data_R2] = InterpolateResistance(k, path_resources, n_apertures=n_apertures, Type = InterpolationType)
        else:
            [time, data_R1] = InterpolateResistance(k, path_resources, n_apertures=n_apertures, Type=InterpolationType)
        if not R1.size > 0:
            R1 = data_R1[np.newaxis, ...]
        else:
            R1 = np.vstack((R1, data_R1))
        if n_apertures == 2:
            if not R2.size > 0:
                R2 = data_R2[np.newaxis, ...]
            else:
                R2 = np.vstack((R2, data_R2))
    stlString = ''

    # Loop through all current level
    for k in range(1, n_total_magnets+1):
        if k in magnets:
            index = magnets.index(k)
            timeShift = tShift[index]
            if timeShift < 0: timeShift = 0

            # Start with generating stimulus for first aperture
            stlString = stlString + f'\n.STIMULUS R_coil_{str(1)}_M{str(magnets[index])} ' \
                                    f'PWL \n+ TIME_SCALE_FACTOR = 1 \n+ VALUE_SCALE_FACTOR = 1 \n'
            stlString = stlString + "+ ( 0s, 0.0 )\n"
            count = 0
            # Set a resistance value in the stimuli for each sparseTimeStepping * TimeValue
            for l in range(1, R1.shape[1] - 1):
                if np.isnan(R1[index, l]): continue
                # Ensure starting at 0 (No negative time in PSPICE allowed
                if float(time[l]) < 0:  timeShift = timeShift + abs(float(time[l])) - 0.03
                if float(time[l]) + timeShift < 0:
                    tt = 0
                else:
                    tt = float(time[l]) + timeShift
                # If every sparseTimeStepping* time value reached, write an entry
                if count >= sparseTimeStepping:
                    stlString = stlString + "+ ( " + str(tt) + "s, " + str(R1[index, l]) + " )\n"
                    count = 0
                count = count + 1
            # Write last time value to be 10000 s, with last resistance (resistance is assumed to stay constant)
            R1_last = R1[index]
            R1_last = R1_last[~np.isnan(R1_last)]
            stlString = stlString + "+ ( " + str(10000) + "s," + str(R1_last[-1]) + " ) \n"
            stlString = stlString + " \n"

            if n_apertures == 2:
                # Repeat procedure for second aperture
                stlString = stlString + f'\n.STIMULUS R_coil_{str(2)}_M{str(magnets[index])} ' \
                                        f'PWL \n+ TIME_SCALE_FACTOR = 1 \n+ VALUE_SCALE_FACTOR = 1 \n'
                stlString = stlString + "+ ( 0s, 0.0 )\n"
                count = 0
                for l in range(1, R2.shape[1] - 1):
                    if np.isnan(R2[index, l]): continue
                    if float(time[l]) < 0:  timeShift = timeShift + abs(float(time[l])) - 0.03
                    if float(time[l]) + timeShift < 0:
                        tt = 0
                    else:
                        tt = float(time[l]) + timeShift
                    if count >= sparseTimeStepping:
                        stlString = stlString + "+ ( " + str(tt) + "s, " + str(R2[index, l]) + " )\n"
                        count = 0
                    count = count + 1
                R2_last = R2[index]
                R2_last = R2_last[~np.isnan(R2_last)]
                stlString = stlString + "+ ( " + str(10000) + "s," + str(R2_last[-1]) + " ) \n"
                stlString = stlString + " \n"
        else:
            stlString = stlString + f'\n.STIMULUS R_coil_{str(1)}_M{str(k)} ' \
                                    f'PWL \n+ TIME_SCALE_FACTOR = 1 \n+ VALUE_SCALE_FACTOR = 1 \n'
            stlString = stlString + "+ ( 0s, 0.0 )\n"
            stlString = stlString + "+ ( 10000s, 0.0 )\n"

            if n_apertures == 2:
                stlString = stlString + f'\n.STIMULUS R_coil_{str(2)}_M{str(k)} ' \
                                        f'PWL \n+ TIME_SCALE_FACTOR = 1 \n+ VALUE_SCALE_FACTOR = 1 \n'
                stlString = stlString + "+ ( 0s, 0.0 )\n"
                stlString = stlString + "+ ( 10000s, 0.0 )\n"

    # Write the stimuli as a txt(stl) file
    with open(Outputfile, type_stl) as ofile:
        ofile.write(stlString)
