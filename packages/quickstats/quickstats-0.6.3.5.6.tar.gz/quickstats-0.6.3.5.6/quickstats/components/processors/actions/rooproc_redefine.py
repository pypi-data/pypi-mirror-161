from .rooproc_define import RooProcDefine

class RooProcRedefine(RooProcDefine):
    
    def _execute(self, rdf, **params):
        name = params['name']
        expression = params['expression']
        if not hasattr(rdf, "Redefine"):
            raise RuntimeError("RDF.Redefine action requires ROOT version >= 6.26/00")
        rdf_next = rdf.Redefine(name, expression)
        return rdf_next