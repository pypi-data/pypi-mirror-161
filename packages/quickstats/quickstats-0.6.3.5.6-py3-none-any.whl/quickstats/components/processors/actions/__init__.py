from .rooproc_base_action import RooProcBaseAction
from .rooproc_rdf_action import RooProcRDFAction
from .rooproc_helper_action import RooProcHelperAction
from .rooproc_hybrid_action import RooProcHybridAction
from .rooproc_nested_action import RooProcNestedAction
from .rooproc_treename import RooProcTreeName
from .rooproc_declare import RooProcDeclare
from .rooproc_global_variables import RooProcGlobalVariables
from .rooproc_alias import RooProcAlias
from .rooproc_safe_alias import RooProcSafeAlias
from .rooproc_define import RooProcDefine
from .rooproc_safe_define import RooProcSafeDefine
from .rooproc_redefine import RooProcRedefine
from .rooproc_filter import RooProcFilter
from .rooproc_sum import RooProcSum
from .rooproc_max import RooProcMax
from .rooproc_min import RooProcMin
from .rooproc_mean import RooProcMean
from .rooproc_save import RooProcSave
from .rooproc_report import RooProcReport
from .rooproc_export import RooProcExport
from .rooproc_save_frame import RooProcSaveFrame
from .rooproc_load_frame import RooProcLoadFrame
from .rooproc_as_numpy import RooProcAsNumpy
from .rooproc_if_defined import RooProcIfDefined
from .rooproc_if_not_defined import RooProcIfNotDefined
from .auxiliary import *

ACTION_MAP = {
    "TREENAME": RooProcTreeName,
    "DECLARE": RooProcDeclare,
    "GLOBAL": RooProcGlobalVariables,
    "ALIAS": RooProcAlias,
    "SAFEALIAS": RooProcSafeAlias,
    "DEFINE": RooProcDefine,
    "SAFEDEFINE": RooProcSafeDefine,    
    "REDEFINE": RooProcRedefine,
    "FILTER": RooProcFilter,
    "GETSUM": RooProcSum,
    "GETMAX": RooProcMax,
    "GETMIN": RooProcMin,
    "GETMEAN": RooProcMean,
    "SAVE": RooProcSave,
    "REPORT": RooProcReport,    
    "EXPORT": RooProcExport,
    "SAVE_FRAME": RooProcSaveFrame,
    "LOAD_FRAME": RooProcLoadFrame,
    "AS_NUMPY": RooProcAsNumpy,
    "IFDEF": RooProcIfDefined,
    "IFNDEF": RooProcIfNotDefined    
}

def get_action(action_name:str):
    return ACTION_MAP.get(action_name, None)