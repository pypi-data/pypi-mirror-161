from .rooproc_stat import RooProcStat

class RooProcMean(RooProcStat):
    def _get_func(self, rdf:"ROOT.RDataFrame"):
        return rdf.Mean