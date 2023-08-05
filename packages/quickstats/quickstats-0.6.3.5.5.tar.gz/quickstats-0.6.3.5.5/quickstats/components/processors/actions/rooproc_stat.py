from typing import Optional
import re

from .rooproc_hybrid_action import RooProcHybridAction

class RooProcStat(RooProcHybridAction):
    def __init__(self, ext_var_name:str, column_name:str):
        super().__init__(ext_var_name=ext_var_name,
                         column_name=column_name)
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        name_literals = re.findall(r"@{([^{}]+)}", main_text)
        if len(name_literals) == 1:
            ext_var_name = name_literals[0]
            column_name = main_text.replace("@{" + ext_var_name + "}", "").strip()
        else:
            raise RuntimeError(f"unspecified external variable name (format:@{{ext_var_name}}): {main_text}")
        return cls(ext_var_name=ext_var_name, column_name=column_name)
    
    def _get_func(self, rdf:"ROOT.RDataFrame"):
        raise NotImplementedError
        
    def _execute(self, rdf:"ROOT.RDataFrame", processor:"quickstats.RooProcessor", **params):
        ext_var_name = params['ext_var_name']
        column_name = params['column_name']
        processor.external_variables[ext_var_name] = self._get_func(rdf)(column_name)
        return rdf, processor