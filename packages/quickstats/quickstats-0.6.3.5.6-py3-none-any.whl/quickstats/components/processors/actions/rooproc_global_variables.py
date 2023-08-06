from typing import Optional, List, Dict
import re

from .rooproc_helper_action import RooProcHelperAction

class RooProcGlobalVariables(RooProcHelperAction):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        main_text = re.sub(r"\s*", "", main_text)
        tokens = main_text.split(",")
        global_variables = {}
        for token in tokens:
            result = re.match("^(\w+)=(.*)", token)
            if not result:
                raise RuntimeError(f"invalid expression {token}")
            global_variables[result[1]] = result[2]
        return cls(**global_variables)
    
    def _execute(self, processor:"quickstats.RooProcessor", **params):
        processor.global_variables.update(params)
        return processor