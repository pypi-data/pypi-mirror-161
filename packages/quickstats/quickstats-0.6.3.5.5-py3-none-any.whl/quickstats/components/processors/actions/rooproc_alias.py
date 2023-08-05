from typing import Optional
import re

from .rooproc_rdf_action import RooProcRDFAction

class RooProcAlias(RooProcRDFAction):
    
    def __init__(self, alias:str, column_name:str):
        super().__init__(alias=alias, column_name=column_name)
        
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        result = re.search(r"^\s*(\w+)\s*=\s*([\w\.]+)", main_text)
        if not result:
            raise RuntimeError(f"invalid expression {main_text}")
        alias = result.group(1)
        column_name = result.group(2)
        return cls(alias=alias, column_name=column_name)        
        
    def _execute(self, rdf:"ROOT.RDataFrame", **params):
        alias = params['alias']
        column_name = params['column_name']
        rdf_next = rdf.Alias(alias, column_name)
        return rdf_next