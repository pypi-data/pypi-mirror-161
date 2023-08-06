from typing import Optional, List, Dict

from .rooproc_base_action import RooProcBaseAction
from .auxiliary import RooProcReturnCode

class RooProcNestedAction(RooProcBaseAction):
    
    def __init__(self, **params):
        super().__init__(**params)

    def _execute(self, processor:"quickstats.RooProcessor", **params):
        return RooProcReturnCode.NORMAL
    
    def execute(self, processor:"quickstats.RooProcessor", global_vars:Optional[Dict]=None):
        params = self.get_formatted_parameters(global_vars)
        return_code = self._execute(processor, **params)
        self.executed = True
        return return_code