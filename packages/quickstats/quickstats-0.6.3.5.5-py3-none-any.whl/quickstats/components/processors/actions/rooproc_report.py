from typing import Optional

import pandas as pd

from .rooproc_hybrid_action import RooProcHybridAction

from quickstats.utils.common_utils import is_valid_file

class RooProcReport(RooProcHybridAction):
    def __init__(self, display:bool=False, filename:Optional[str]=None):
        super().__init__(display=display,
                         filename=filename)
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        kwargs = cls.parse_as_kwargs(main_text)
        return cls(**kwargs)
    
    def _execute(self, rdf:"ROOT.RDataFrame", processor:"quickstats.RooProcessor", **params):
        display = params['display']
        filename = params['filename']
        if processor.cache and is_valid_file(filename):
            processor.stdout.info(f"INFO: Cached output `{filename}`.")
            return rdf, processor        
        cut_report = rdf.Report()
        result = []
        cumulative_eff  = 1
        for report in cut_report:
            data = {}
            data['name'] = report.GetName()
            data['all']  = report.GetAll()
            data['pass'] = report.GetPass()
            data['efficiency'] = report.GetEff()
            cumulative_eff *= data['efficiency']/100
            data['cumulative_efficiency'] = cumulative_eff*100
            result.append(data)
        df = pd.DataFrame(result)
        if int(display):
            processor.stdout.info(df)
        if filename is not None:
            self.makedirs(filename)
            df.to_csv(filename)
        return rdf, processor