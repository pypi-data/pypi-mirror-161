from pydantic import BaseModel, PrivateAttr, Field
from typing import (Deque, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple, Union, Type, Literal)
import ruamel.yaml
from steam_sdk.data.DataRoxieParser import RoxieData


class RibbonFiQuS(BaseModel):
    """
        Rutherford cable type
    """
    type: Literal['Ribbon']
    bare_cable_width: float = None
    bare_cable_height_mean: float = None


class RutherfordFiQuS(BaseModel):
    """
        Rutherford cable type
    """
    type: Literal['Rutherford']
    bare_cable_width: float = None
    bare_cable_height_mean: float = None


class ConductorFiQuS(BaseModel):
    """
        Class for conductor type
    """
    cable: Union[RutherfordFiQuS, RibbonFiQuS] = {'type': 'Rutherford'}


class GeneralSetting(BaseModel):
    """
        Class for general information on the case study
    """
    I_ref: List[float] = None


class ModelDataSetting(BaseModel):
    """
        Class for model data
    """
    general_parameters: GeneralSetting = GeneralSetting()
    conductors: Dict[str, ConductorFiQuS] = {}

#######################################################################################################################


class Threshold(BaseModel):
    SizeMin: float = None
    SizeMax: float = None
    DistMin: float = None
    DistMax: float = None


class AdvancedOption(BaseModel):
    from_brep: bool = None
    from_msh: bool = None


class Option(BaseModel):
    # run_type: str = None
    iron_yoke: bool = None
    compare_to_ROXIE: bool = None
    choose_mesh: bool = None
    plot_all: bool = None
    launch_gui: bool = None
    advanced: AdvancedOption = AdvancedOption()


class Mesh(BaseModel):
    mesh_iron: Threshold = Threshold()
    mesh_coil: Threshold = Threshold()
    MeshSizeMin: float = None  # sets gmsh Mesh.MeshSizeMin
    MeshSizeMax: float = None  # sets gmsh Mesh.MeshSizeMax
    MeshSizeFromCurvature: float = None  # sets gmsh Mesh.MeshSizeFromCurvature
    Algorithm: int = None  # sets gmsh Mesh.Algorithm
    AngleToleranceFacetOverlap: float = None  # sets gmsh Mesh.AngleToleranceFacetOverlap
    ElementOrder: int = None  # sets gmsh Mesh.ElementOrder
    Optimize: int = None  # sets gmsh Mesh.Optimize


class Solve(BaseModel):
    pro_template: str = None  # file name of .pro template file


class PostProc(BaseModel):
    variables: List[str] = None  # Name of variables to post-process, like "b" for magnetic flux density
    volumes: List[str] = None  # Name of domains to post-process, like "powered"
    file_exts: List[str] = None  # Name of file extensions to output to, like "pos"
    additional_outputs: List[str] = None  # Name of software specific input files to prepare, like "LEDET3D"


class OptionFiQuS(BaseModel):
    options: Option = Option()
    mesh: Mesh = Mesh()
    solve: Solve = Solve()
    post_proc: PostProc = PostProc()


class PowerSupplyFiQuS(BaseModel):
    I_initial: List[float] = None


class GeneralFiQuS(BaseModel):
    magnet_name: str = None


class ModelData(BaseModel):
    general_parameters: GeneralFiQuS = GeneralFiQuS()
    power_supply: PowerSupplyFiQuS = PowerSupplyFiQuS()

#######################################################################################################################


class FiQuSGeometry(BaseModel):
    """
        Class for Roxie data
    """
    Roxie_Data: RoxieData = RoxieData()


class FiQuSSettings(BaseModel):
    """
        Class for FiQuS model
    """
    Model_Data_GS: ModelDataSetting = ModelDataSetting()


class FiQuSData(BaseModel):
    Model_Data: ModelData = ModelData()
    Options_FiQuS: OptionFiQuS = OptionFiQuS()


