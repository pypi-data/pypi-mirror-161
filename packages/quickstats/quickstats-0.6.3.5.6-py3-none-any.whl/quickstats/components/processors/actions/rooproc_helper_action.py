from typing import Optional, List, Dict

from .rooproc_base_action import RooProcBaseAction

class RooProcHelperAction(RooProcBaseAction):
    
    def _execute(self, processor:"quickstats.RooProcessor", **params):
        return processor
    
    def execute(self, processor:"quickstats.RooProcessor", global_vars:Optional[Dict]=None):
        params = self.get_formatted_parameters(global_vars)
        processor = self._execute(processor, **params)
        self.executed = True
        return processor