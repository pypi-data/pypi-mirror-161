import math
import pandas as pd

from steam_sdk.data import DataModelMagnet as dM
from steam_sdk.data import DataRoxieParser as dR
from steam_sdk.data import DataFiQuS as dF


class BuilderFiQuS:
    """
        Class to generate FiQuS models
    """

    def __init__(self,
                 input_model_data: dM.DataModelMagnet = None,
                 input_roxie_data: dR.RoxieData = None,
                 flag_build: bool = True,
                 flag_plot_all: bool = False,
                 verbose: bool = True):
        """
            Object is initialized by defining FiQuS variable structure and file template.
            If verbose is set to True, additional information will be displayed
        """
        # Unpack arguments
        self.verbose: bool = verbose
        self.flag_plot_all: bool = flag_plot_all
        self.model_data: dM.DataModelMagnet = input_model_data
        self.roxie_data: dR.RoxieData = input_roxie_data

        # TODO build different objects according to self.model_data.GeneralParameters.magnet_type

        # Data structure
        self.data_FiQuS_geo = dF.FiQuSGeometry()
        self.data_FiQuS_set = dF.FiQuSSettings()
        self.data_FiQuS = dF.FiQuSData()

        if not self.model_data and flag_build:
            raise Exception('Cannot build model instantly without providing DataModelMagnet')

        if flag_build:
            # Build data structures
            self.buildData()

    def buildData(self):
        """
            Load selected conductor data from DataModelMagnet keys, check inputs, calculate and set missing variables
        """

        self.data_FiQuS_geo.Roxie_Data = dR.RoxieData(**self.roxie_data.dict())

        self.data_FiQuS_set.Model_Data_GS.general_parameters.I_ref =\
            [self.model_data.Options_LEDET.field_map_files.Iref] * len(self.data_FiQuS_geo.Roxie_Data.coil.coils)
        for cond in self.model_data.Conductors:
            if cond.cable.type == 'Rutherford':
                self.data_FiQuS_set.Model_Data_GS.conductors[cond.name] =\
                    dF.ConductorFiQuS(cable=dF.RutherfordFiQuS(type=cond.cable.type))
            elif cond.cable.type == 'Ribbon':
                self.data_FiQuS_set.Model_Data_GS.conductors[cond.name] =\
                    dF.ConductorFiQuS(cable=dF.RibbonFiQuS(type=cond.cable.type))
            conductor = self.data_FiQuS_set.Model_Data_GS.conductors[cond.name]
            conductor.cable.bare_cable_width = cond.cable.bare_cable_width
            conductor.cable.bare_cable_height_mean = cond.cable.bare_cable_height_mean

        self.data_FiQuS.Model_Data.general_parameters.magnet_name = self.model_data.GeneralParameters.magnet_name
        self.data_FiQuS.Model_Data.power_supply.I_initial =\
            [self.model_data.Power_Supply.I_initial] * len(self.data_FiQuS_geo.Roxie_Data.coil.coils)
        self.data_FiQuS.Options_FiQuS = self.model_data.Options_FiQuS
        self.data_FiQuS.Options_FiQuS.options.plot_all = self.flag_plot_all
