from typing import Optional

from .rooproc_helper_action import RooProcHelperAction

from quickstats.utils.root_utils import declare_expression

class RooProcDeclare(RooProcHelperAction):
    
    def __init__(self, expression:str, name:Optional[str]=None):
        super().__init__(expression=expression,
                         name=name)
        
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        return cls(expression=main_text)        
    
    def _execute(self, processor:"quickstats.RooProcessor", **params):
        name = params.get("name", None)
        expression = params['expression']
        declare_expression(expression, name)
        return processor