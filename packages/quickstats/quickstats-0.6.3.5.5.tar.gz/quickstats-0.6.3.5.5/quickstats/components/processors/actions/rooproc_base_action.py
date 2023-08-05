from typing import Optional, List, Dict
import os
import re

class RooProcBaseAction(object):
    def __init__(self, **params):
        self._params = params
        self.executed = False
        self.status   = None
    
    def get_formatted_parameters(self, global_vars:Optional[Dict]=None):
        if global_vars is None:
            global_vars = {}
        formatted_parameters = {}
        for k,v in self._params.items():
            if v is None:
                formatted_parameters[k] = None
                continue
            k_literals = re.findall(r"\${(\w+)}", k)
            is_list = False
            if isinstance(v, list):
                v = '__SEPARATOR__'.join(v)
                is_list = True
            v_literals = re.findall(r"\${(\w+)}", v)
            all_literals = set(k_literals).union(set(v_literals))
            for literal in all_literals:
                if literal not in global_vars:
                    raise RuntimeError(f"the global variable `{literal}` is undefined")
            for literal in k_literals:
                substitute = global_vars[literal]
                k = k.replace("${" + literal + "}", str(substitute))
            for literal in v_literals:
                substitute = global_vars[literal]
                v = v.replace("${" + literal + "}", str(substitute))
            if is_list:
                v = v.split("__SEPARATOR__")
            formatted_parameters[k] = v
        return formatted_parameters
    
    def makedirs(self, fname:str):
        dirname = os.path.dirname(fname)
        if dirname and (not os.path.exists(dirname)):
            os.makedirs(dirname)
    
    def execute(self, **params):
        raise NotImplementedError
    
    @classmethod
    def parse_as_kwargs(cls, text:str):
        kwargs = {}
        text = re.sub(r"\s*", "", text)
        list_attributes = re.findall(r"(\w+)=\[([^\[\]]+)\]", text)
        for attribute in list_attributes:
            kwargs[attribute[0]] = attribute[1].split(",")
            text = text.replace(f"{attribute[0]}=[{attribute[1]}]","")
        attributes = re.findall(r"(\w+)=([^,]+)", text)
        for attribute in attributes:
            kwargs[attribute[0]] = attribute[1]
        return kwargs
    
    @classmethod
    def parse(cls, main_text:str, block_text:Optional[str]=None):
        raise NotImplementedError