from .rooproc_stat import RooProcStat

class RooProcMax(RooProcStat):
    def _get_func(self, rdf:"ROOT.RDataFrame"):
        return rdf.Max