from .rooproc_stat import RooProcStat

class RooProcMin(RooProcStat):
    def _get_func(self, rdf:"ROOT.RDataFrame"):
        return rdf.Min