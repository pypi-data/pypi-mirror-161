from typing import Optional, List, Dict, Union
import os
import glob
import json
import time
import ROOT

from .builtin_methods import BUILTIN_METHODS
from .actions import *
from .roo_config_parser import RooConfigParser

from quickstats import Timer, AbstractObject
from quickstats.utils.root_utils import declare_expression, close_all_root_files

class RooProcessor(AbstractObject):
    def __init__(self, config_path:Optional[str]=None,
                 flags:Optional[List[str]]=None,
                 multithread:bool=True,
                 cache:bool=False,
                 use_template:bool=False,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)
        self.cache = cache
        self.action_tree = None
        if flags is not None:
            self.flags = list(flags)
        else:
            self.flags = []
        self.rdf_frames = {}
        self.rdf = None
        self.global_variables = {}
        self.external_variables = {}
        self.treename = None
        self.use_template = use_template
        
        self.load_buildin_functions()
        
        if multithread:
            ROOT.EnableImplicitMT()
        
        if config_path is not None:
            self.load_config(config_path)
            
    def set_cache(self, cache:bool=True):
        self.cache = cache
            
    def load_buildin_functions(self):
        for name, definition in BUILTIN_METHODS.items():
            declare_expression(definition, name)
    
    def load_config(self, config_path:Optional[str]=None):
        action_tree = RooConfigParser.parse_file(config_path)
        action_tree.construct_actions()
        if not action_tree.root_node.has_child:
            raise RuntimeError("no actions found in the process card")
        first_action = action_tree.root_node.first_child.action
        if not isinstance(first_action, RooProcTreeName):
            raise RuntimeError("tree name must be specified at the beginning of the process card")
        self.treename = first_action._params['treename']
        self.action_tree = action_tree
        
    def set_global_variables(self, **kwargs):
        self.global_variables.update(kwargs)
    
    def add_flags(self, flags:List[str]):
        self.flags += list(flags)
        
    def set_flags(self, flags:List[str]):
        self.flags = list(flags)        
        
    def cleanup(self):
        close_all_root_files()
        self.rdf_frames = {}
        self.rdf = None
        
    def _get_all_files(self, filename:Union[List[str], str]):
        all_files = []
        if isinstance(filename, str):
            filename = [filename]
        if not isinstance(filename, list):
            raise ValueError("filename must be either string or list of strings")
        for fname in filename:
            if os.path.isdir(fname):
                all_files += glob.glob(os.path.join(fname, "*.root"))
            else:
                all_files += glob.glob(fname)
        if not all_files:
            raise FileNotFoundError(f"file `{filename}` does not exist")
        return all_files
    
    def run_action(self, action:RooProcBaseAction):
        if not self.rdf:
            raise RuntimeError("RDataFrame instance not initialized")
        if isinstance(action, RooProcRDFAction):
            self.rdf = action.execute(self.rdf, self.global_variables)
        elif isinstance(action, RooProcHelperAction):
            action.execute(self, self.global_variables)
        elif isinstance(action, RooProcHybridAction):
            self.rdf, _ = action.execute(self.rdf, self, self.global_variables)
        elif isinstance(action, RooProcNestedAction):
            return_code = action.execute(self, self.global_variables)
            return return_code
        else:
            raise RuntimeError("unknown action type")
        return RooProcReturnCode.NORMAL
            
    def run_all_actions(self, consider_child:bool=True):
        if not self.action_tree:
            raise RuntimeError("action tree not initialized")
        node = self.action_tree.get_next(consider_child=consider_child)
        if node is not None:
            self.stdout.debug(f'DEBUG: Executing node "{node.name}" defined at line {node.data["start_line_number"]}')
            action = node.action
            return_code = self.run_action(action)
            if return_code == RooProcReturnCode.NORMAL:
                self.run_all_actions()
            elif return_code == RooProcReturnCode.SKIP_CHILD:
                self.run_all_actions(consider_child=False)
            else:
                raise RuntimeError("unknown return code")
        else:
            self.stdout.debug(f'DEBUG: All node executed')
            
    def sanity_check(self):
        if not self.action_tree:
            raise RuntimeError("action tree not initialized")        
        if not self.action_tree.root_node.has_child:
            self.stdout.warning("WARNING: No actions to be performed.")
            return None
        if self.treename is None:
            raise RuntimeError("tree name is undefined")
    
    def run(self, filename:Union[List[str], str]):
        self.sanity_check()
        all_files = self._get_all_files(filename)
        if len(all_files) == 1:
            self.stdout.info(f"INFO: Processing file `{all_files[0]}`.")
        else:
            self.stdout.info(f"INFO: Professing files")
            for f in all_files:
                self.stdout.info(f"\t`{f}`")  
        with Timer() as t:
            self.rdf = ROOT.RDataFrame(self.treename, all_files)
            self.action_tree.reset()
            self.run_all_actions()
            self.cleanup()
            
        self.stdout.info(f"INFO: Task finished. Total time taken: {t.interval:.3f} s.")