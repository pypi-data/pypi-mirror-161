from steam_sdk.data import DataDAKOTA as dDAKOTA
from steam_sdk.parsers.ParserDAKOTA import ParserDAKOTA
import os

class BuilderDAKOTA:
    '''

    '''


    def __init__(self, input_DAKOTA_yaml: str = None, verbose: bool = True):
            """
            Object is initialized by defining DAKOTA variable structure and file template.
            If verbose is set to True, additional information will be displayed
            """
            # Unpack arguments
            self.verbose: bool = verbose
            self.Parser_DAKOTA: ParserDAKOTA = ParserDAKOTA()
            self.Parser_DAKOTA.readFromYaml(input_DAKOTA_yaml)
            self.DAKOTA_data = self.Parser_DAKOTA.dakota_data

            self.DAKOTA_folder = self.DAKOTA_data.WorkingFolders.output_path
            self.Parser_DAKOTA.writeDAKOTA2in(os.path.join(self.DAKOTA_folder, f'{self.DAKOTA_data.STEAMmodel.name}_Analysis'))
            return

