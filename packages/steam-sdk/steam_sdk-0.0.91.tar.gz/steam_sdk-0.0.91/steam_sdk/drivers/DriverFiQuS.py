import os
import subprocess
from pathlib import Path


class DriverFiQuS:
    """
        Class to drive FiQuS models
    """

    def __init__(self, path_exe=None, path_folder_FiQuS=None, path_folder_FiQuS_input=None, verbose=False):
        # Unpack arguments
        self.path_exe = path_exe
        self.path_folder_FiQuS = path_folder_FiQuS
        self.path_folder_FiQuS_input = path_folder_FiQuS_input
        self.verbose = verbose
        if verbose:
            print('path_exe =          {}'.format(path_exe))
            print('path_folder_FiQuS = {}'.format(path_folder_FiQuS))

    def run_FiQuS(self, simFileName: str, outputDirectory: str = 'output'):
        """
        ** Run FiQuS model **
        :param simFileName: Name of the simulation file to run
        :param outputDirectory: Name of the output directory
        :return:
        """
        # Unpack arguments
        path_exe = self.path_exe
        path_folder_FiQuS = self.path_folder_FiQuS
        path_folder_FiQuS_input = self.path_folder_FiQuS_input
        verbose = self.verbose

        full_path_input = os.path.join(path_folder_FiQuS_input, simFileName)
        full_path_output = os.path.join(path_folder_FiQuS, outputDirectory)

        model_data_path = os.path.join(full_path_input + '.yaml')
        geo_path = os.path.join(full_path_input + '.geom')
        set_path = os.path.join(full_path_input + '.set')

        if not os.path.isdir(full_path_output):
            print("Output folder {} does not exist. Making it now".format(full_path_output))
            Path(full_path_output).mkdir(parents=True)

        if verbose:
            print('path_exe =             {}'.format(path_exe))
            print('path_folder_FiQuS =    {}'.format(path_folder_FiQuS))
            print('simFileName =          {}'.format(simFileName))
            print('outputDirectory =      {}'.format(outputDirectory))
            print('full_path_input =      {}'.format(full_path_input))
            print('full_path_output =     {}'.format(full_path_output))

        # Run model
        return subprocess.call(['py', path_exe, model_data_path, geo_path, set_path])

