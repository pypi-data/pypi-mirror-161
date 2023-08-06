from .rooproc_define import RooProcDefine

class RooProcSafeDefine(RooProcDefine):
        
    def _execute(self, rdf:"ROOT.RDataFrame", **params):
        name = params['name']
        expression = params['expression']
        all_column_names = [str(i) for i in rdf.GetColumnNames()]
        # already defined, skipping
        if name in all_column_names:
            return rdf
        rdf_next = rdf.Define(name, expression)
        return rdf_next