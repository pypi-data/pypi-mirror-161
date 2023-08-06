from typing import List

from .rooproc_nested_action import RooProcBaseAction, RooProcNestedAction
from .auxiliary import RooProcReturnCode

class RooProcIfNotDefined(RooProcNestedAction):
    
    def __init__(self, flag:str):
        super().__init__(flag=flag)
        
    @classmethod
    def parse(cls, main_text:str, block_text:str):
        if not block_text:
            raise ValueError("missing flag name in IFDEF action")
        return cls(flag=block_text)
     
    def _execute(self, processor:"quickstats.RooProcessor", **params):
        flag = params['flag']
        if flag not in processor.flags:
            return RooProcReturnCode.NORMAL
        return RooProcReturnCode.SKIP_CHILD