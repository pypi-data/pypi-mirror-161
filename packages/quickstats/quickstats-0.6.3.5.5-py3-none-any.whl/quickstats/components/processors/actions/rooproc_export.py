from typing import Optional, List, Dict
import os
import json

from .rooproc_helper_action import RooProcHelperAction

class RooProcExport(RooProcHelperAction):
    def __init__(self, filename:str):
        super().__init__(filename=filename)
        
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        kwargs = cls.parse_as_kwargs(main_text)
        return cls(**kwargs)
    
    def _execute(self, processor:"quickstats.RooProcessor", **params):
        filename = params['filename']
        data = {k:v.GetValue() for k,v in processor.external_variables.items()}
        dirname = os.path.dirname(filename)
        if dirname and (not os.path.exists(dirname)):
            os.makedirs(dirname)
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, indent=2)
        return processor