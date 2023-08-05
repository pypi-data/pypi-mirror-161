from typing import Optional, List, Dict

from .rooproc_base_action import RooProcBaseAction

class RooProcRDFAction(RooProcBaseAction):
    
    def _execute(self, rdf:"ROOT.RDataFrame", **params):
        return rdf
    
    def execute(self, rdf:"ROOT.RDataFrame", global_vars:Optional[Dict]=None):
        params = self.get_formatted_parameters(global_vars)
        rdf_next = self._execute(rdf, **params)
        self.executed = True
        return rdf_next 