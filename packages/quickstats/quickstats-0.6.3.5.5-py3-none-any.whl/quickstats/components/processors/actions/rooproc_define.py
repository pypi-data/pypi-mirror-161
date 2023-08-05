from typing import Optional
import re

from .rooproc_rdf_action import RooProcRDFAction

class RooProcDefine(RooProcRDFAction):
    
    def __init__(self, name:str, expression:str):
        super().__init__(name=name, expression=expression)
        
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        result = re.search(r"^\s*(\w+)\s*=(.*)", main_text)
        if not result:
            raise RuntimeError(f"invalid expression {main_text}")
        name = result.group(1)
        expression = result.group(2)
        return cls(name=name, expression=expression)        
        
    def _execute(self, rdf:"ROOT.RDataFrame", **params):
        name = params['name']
        expression = params['expression']
        rdf_next = rdf.Define(name, expression)
        return rdf_next