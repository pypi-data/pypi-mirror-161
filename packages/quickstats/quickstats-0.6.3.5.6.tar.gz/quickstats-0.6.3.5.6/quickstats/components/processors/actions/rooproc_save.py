from typing import Optional, List
import fnmatch

from .rooproc_hybrid_action import RooProcHybridAction

from quickstats.utils.common_utils import is_valid_file

class RooProcSave(RooProcHybridAction):
    
    def __init__(self, treename:str, filename:str, 
                 columns:Optional[List[str]]=None,
                 frame:Optional[str]=None):
        super().__init__(treename=treename,
                         filename=filename,
                         columns=columns,
                         frame=frame)
        
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        kwargs = cls.parse_as_kwargs(main_text)
        return cls(**kwargs)
    
    def _execute(self, rdf:"ROOT.RDataFrame", processor:"quickstats.RooProcessor", **params):
        treename = params['treename']
        filename = params['filename']
        if processor.cache and is_valid_file(filename):
            processor.stdout.info(f'INFO: Cached output from "{filename}".')
            return rdf, processor
        columns = params.get('columns', None)
        if columns is None:
            if processor.use_template:
                from quickstats.utils.root_utils import templated_rdf_snapshot
                rdf_next = templated_rdf_snapshot(rdf)(treename, filename)
            else:
                rdf_next = rdf.Snapshot(treename, filename)
        else:
            all_columns = [str(c) for c in rdf.GetColumnNames()]
            save_columns = []
            for column in columns:
                save_columns += [c for c in all_columns if fnmatch.fnmatch(c, column)]
            save_columns = list(set(save_columns))
            self.makedirs(filename)
            if processor.use_template:
                from quickstats.utils.root_utils import templated_rdf_snapshot 
                rdf_next = templated_rdf_snapshot(rdf, save_columns)(treename, filename, save_columns)
            else:
                rdf_next = rdf.Snapshot(treename, filename, save_columns)
        processor.stdout.info(f'INFO: Writing output to "{filename}".')
        return rdf_next, processor