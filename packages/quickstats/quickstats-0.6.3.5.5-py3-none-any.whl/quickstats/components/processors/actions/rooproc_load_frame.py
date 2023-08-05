from typing import Optional

from .rooproc_helper_action import RooProcHelperAction

class RooProcLoadFrame(RooProcHelperAction):
    def __init__(self, name:str):
        super().__init__(name=name)

    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        return cls(name=main_text)
    
    def _execute(self, processor:"quickstats.RooProcessor", **params):
        frame_name = params['name']
        if frame_name not in processor.rdf_frames:
            raise RuntimeError(f"failed to load rdf frame `{frame_name}`: frame does not exist.")
        processor.rdf = processor.rdf_frames[frame_name]