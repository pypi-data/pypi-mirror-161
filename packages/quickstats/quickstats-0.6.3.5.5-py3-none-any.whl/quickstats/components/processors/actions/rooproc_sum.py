from .rooproc_stat import RooProcStat

class RooProcSum(RooProcStat):
    def _get_func(self, rdf:"ROOT.RDataFrame"):
        return rdf.Sum