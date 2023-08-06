from typing import Optional, List

import numpy as np

from .rooproc_hybrid_action import RooProcHybridAction

from quickstats.utils.common_utils import is_valid_file

class RooProcAsNumpy(RooProcHybridAction):
    
    def __init__(self, filename:str, 
                 columns:Optional[List[str]]=None):
        super().__init__(filename=filename,
                         columns=columns)
        
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        kwargs = cls.parse_as_kwargs(main_text)
        return cls(**kwargs)
    
    def _execute(self, rdf:"ROOT.RDataFrame", processor:"quickstats.RooProcessor", **params):
        filename = kwargs['filename']
        if processor.cache and is_valid_file(filename):
            processor.stdout.info(f"INFO: Cached output `{filename}`.")
            return rdf, processor
        columns = kwargs.get('columns', None)
        if columns is None:
            data = rdf.AsNumpy()
        else:
            data = rdf.AsNumpy(columns)
        np.save(filename, data)
        return rdf, processor