from typing import Optional, Dict

from .rooproc_base_action import RooProcBaseAction

class RooProcHybridAction(RooProcBaseAction):
    
    def _execute(self, rdf:"ROOT.RDataFrame", processor:"quickstats.RooProcessor", **params):
        return rdf, processor
    
    def execute(self, rdf:"ROOT.RDataFrame", processor:"quickstats.RooProcessor", global_vars:Optional[Dict]=None):
        params = self.get_formatted_parameters(global_vars)
        rdf_next, processor_next = self._execute(rdf, processor, **params)
        self.executed = True
        return rdf_next, processor_next