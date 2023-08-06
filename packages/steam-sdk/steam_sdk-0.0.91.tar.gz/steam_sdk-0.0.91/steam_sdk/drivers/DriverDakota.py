import os
import dakota.interfacing as di
import shutil
from pathlib import Path

from steam_sdk.builders.BuilderDAKOTA import BuilderDAKOTA
from steam_sdk.analyses.AnalysisSTEAM import AnalysisSTEAM
from steam_sdk.data.DataAnalysis import ModifyModel, AddAuxiliaryFile

class DriverDAKOTA:

    def __init__(self, input_DAKOTA_yaml: str):
        self.Builder = BuilderDAKOTA(input_DAKOTA_yaml)
        self.STEAM_Analysis = AnalysisSTEAM(relative_path_settings='..', input_dictionary=self.Builder.DAKOTA_data.dict(), verbose=True)
        self.variables = self.Builder.DAKOTA_data.DAKOTA_analysis.variables
        self.global_run_counter = 0


    def __prepareSteps(self, params):
        counter = 0
        additional_step_names = []

        step_modify_magnets = 'makeModel_Ref'
        self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[step_modify_magnets] = ModifyModel(type='MakeModel')
        self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[step_modify_magnets].model_name = 'BM'
        self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[step_modify_magnets].file_model_data = self.Builder.DAKOTA_data.STEAMmodel.file_model_data
        self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[step_modify_magnets].case_model = self.Builder.DAKOTA_data.STEAMmodel.case_model
        self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[step_modify_magnets].flag_build = True
        additional_step_names.append(step_modify_magnets)

        for variable in self.variables.variable_arguments['descriptors']:
            step_modify_magnets = 'modifyModel_magnets'
            self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[step_modify_magnets] = ModifyModel(
                type='ModifyModel')
            self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[step_modify_magnets].model_name = 'BM'
            self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[
                step_modify_magnets].variable_to_change = variable
            self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[step_modify_magnets].variable_value = params[counter]
            additional_step_names.append(step_modify_magnets)
            counter = counter + 1

        # Include last steps
        step_modify_magnets = 'modifyModel_last'
        self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[step_modify_magnets] = ModifyModel(type='ModifyModel')
        self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[step_modify_magnets].model_name = 'BM'
        self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[
            step_modify_magnets].simulation_name = self.Builder.DAKOTA_data.STEAMmodel.name
        self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[
            step_modify_magnets].software = self.Builder.DAKOTA_data.STEAMmodel.software
        additional_step_names.append(step_modify_magnets)
        ##
        step_modify_magnets = 'RunSimulation'
        self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[step_modify_magnets] = ModifyModel(
            type='RunSimulation')
        self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[
            step_modify_magnets].software = self.Builder.DAKOTA_data.STEAMmodel.software
        self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[
            step_modify_magnets].simulation_name = self.Builder.DAKOTA_data.STEAMmodel.name
        self.STEAM_Analysis.data_analysis.AnalysisStepDefinition[
            step_modify_magnets].simulation_numbers = self.global_run_counter
        additional_step_names.append(step_modify_magnets)
        self.global_run_counter = self.global_run_counter + 1
        return additional_step_names


    def __returnOutputFile(self):
        output_folder = self.STEAM_Analysis.output_path
        if self.Builder.DAKOTA_data.STEAMmodel.software == 'PSPICE':
            output_file = os.path.join(output_folder, f'{self.Builder.DAKOTA_data.STEAMmodel.name}.csd')
        elif self.Builder.DAKOTA_data.STEAMmodel.software == 'LEDET':
            raise Exception('Not implemented yet.')
        elif self.Builder.DAKOTA_data.STEAMmodel.software == 'FiQuS':
            raise Exception('Not implemented yet.')
        elif self.Builder.DAKOTA_data.STEAMmodel.software == 'PyBBQ':
            raise Exception('Not implemented yet.')
        else:
            raise Exception('Software not understood.')
        return output_file


    def __CalculateOutput_PSPICE(self, outputfile: str):
        return 1


    def __CalculateOutput_LEDET(self, outputfile: str):
        raise Exception('Not implemented yet.')


    def __CalculateOutput_FiQuS(self, outputfile: str):
        raise Exception('Not implemented yet.')


    def __CalculateOutput_PyBBQ(self, outputfile: str):
        raise Exception('Not implemented yet.')


    def __CalculateOutput(self, outputfile: str):
        if self.Builder.DAKOTA_data.STEAMmodel.software == 'PSPICE':
            self.__CalculateOutput_PSPICE(outputfile)
        elif self.Builder.DAKOTA_data.STEAMmodel.software == 'LEDET':
            self.__CalculateOutput_LEDET(outputfile)
        elif self.Builder.DAKOTA_data.STEAMmodel.software == 'FiQuS':
            self.__CalculateOutput_FiQuS(outputfile)
        elif self.Builder.DAKOTA_data.STEAMmodel.software == 'PyBBQ':
            self.__CalculateOutput_PyBBQ(outputfile)
        else:
            raise Exception('Software not understood.')


    def Driver_DAKOTA(self):
        params, result_for_dakota = di.read_parameters_file()

        ## Run steps and change the model
        additional_step_names = self.__prepareSteps(params)

        ## Run the model
        self.STEAM_Analysis.run_analysis()
        outputfile = self.__returnOutputFile()
        sim_result = self.__CalculateOutput(outputfile)

        # Write back to DAKOTA
        for i, label in enumerate(result_for_dakota):
            if result_for_dakota[label].asv.function:
                result_for_dakota[label].function = sim_result[label]

        return 1
