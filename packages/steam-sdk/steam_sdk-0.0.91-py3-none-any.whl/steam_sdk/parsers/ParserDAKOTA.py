import os
from pathlib import Path

import numpy as np
import ruamel.yaml

from steam_sdk.parsers.dict_to_in import dict_to_in
from steam_sdk.data import DataDAKOTA as dDAKOTA


class ParserDAKOTA:
    """
        Class with methods to read/write FiQuS information from/to other programs
    """

    def __init__(self, input_DAKOTA_data: dDAKOTA.DAKOTA = dDAKOTA.DAKOTA):
        """
            Initialization using a BuilderDAKOTA object containing DAKOTA parameter structure
        """

        self.dakota_data: dDAKOTA.DAKOTA = input_DAKOTA_data

    def readFromYaml(self, file_name: str, verbose: bool = True):
        """
        Read the DAKOTA input variables from a .yaml file and parse into the object

        """

        # Load yaml keys into DataModelMagnet dataclass
        with open(file_name + '.yaml', "r") as stream:
            dictionary_yaml = ruamel.yaml.safe_load(stream)
            self.dakota_data = dDAKOTA.DAKOTA(**dictionary_yaml)

        if verbose:
            print('File {} was loaded.'.format(file_name))

    def writeDAKOTA2in(self, full_path_file_name: str, verbose: bool = False):
        """
        Writes the DAKOTA object into a respective .in file according to the format
        """

        # If the output folder is not an empty string, and it does not exist, make it
        output_path = os.path.dirname(full_path_file_name)
        if verbose:
            print('output_path: {}'.format(output_path))
        if output_path != '' and not os.path.isdir(output_path):
            print("Output folder {} does not exist. Making it now".format(output_path))
            Path(output_path).mkdir(parents=True)

        dict_to_in(self.dakota_data.DAKOTA_analysis.dict(), full_path_file_name + '.in')
