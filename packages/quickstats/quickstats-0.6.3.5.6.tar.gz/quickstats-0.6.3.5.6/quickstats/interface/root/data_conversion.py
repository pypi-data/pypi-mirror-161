from typing import Optional, Dict, List

import ROOT
import time
import numpy as np

from .helper import RMultithreadEnv
from .TFile import TFile
from quickstats.interface.cppyy.vectorize import np_type_str_maps, as_np_array

root_datatypes = ["bool", "Bool_t", "Byte_t", "char", "char*", "Char_t", 
                  "double", "Double32_t", "Double_t", "float",
                  "Float16_t", "Float_t", "int", "Int_t", 
                  "long", "long long", "Long_t", "Long64_t",
                  "short", "Short_t", "Size_t", "UChar_t",
                  "UInt_t", "ULong64_t", "ULong_t",
                  "unsigned", "unsigned char", "unsigned int",
                  "unsigned long", "unsigned long long",
                  "unsigned short", "UShort_t"]

uproot_datatypes = ["double", "float", "int", "int64_t", "char*", "int32_t"]

def array2root(array_data:Dict[str, np.ndarray], fname:str, tree_name:str, multithread:bool=True):
    
    with RMultithreadEnv(multithread):
        columns = list(array_data.keys())
        snapshot_templates = []
        for column in columns:
            template_type = np_type_str_maps.get(array_data[column].dtype, None)
            if template_type is None:
                raise ValueError(f"unsupported array type \"{array_data[column].dtype}\"")
            snapshot_templates.append(template_type)
        snapshot_templates = tuple(snapshot_templates)
        df = ROOT.RDF.MakeNumpyDataFrame(array_data)
        df.Snapshot.__getitem__(snapshot_templates)(tree_name, fname, columns)
        
numpy2root = array2root

def dataframe2numpy(df:"pandas.DataFrame", columns:Optional[List[str]]=None):
    if columns is not None:
        return dict(zip(columns, df[columns].to_numpy().T))
    return dict(zip(df.columns.values, df.to_numpy().T))


def dataframe2root(df:"pandas.DataFrame", fname:str, tree_name:str,
                   columns:Optional[List[str]]=None, multithread:bool=True):
    array_data = dataframe2numpy(df, columns)
    array2root(array_data, fname, tree_name, multithread=multithread)
    
def uproot_get_standard_columns(uproot_tree):
    typenames = uproot_tree.typenames()
    columns = list(typenames.keys())
    column_types = list(typenames.values())
    return np.array(columns)[np.where(np.isin(column_types, uproot_datatypes))]
    
def root2numpy(filename:str, treename:str, columns:List[str]=None,
               remove_non_standard_types:bool=True, library:str="uproot"):
    if library.lower() == "root":
        rfile = TFile._open(filename)
        tree  = rfile.Get(treename)
        if (not tree) or (not isinstance(tree, ROOT.TTree)):
            raise RuntimeError(f'no TTree with name "{treename}" was found')
        rdf = ROOT.RDataFrame(tree)
        if (columns is None) and (not remove_non_standard_types):
            return rdf.AsNumpy()
        else:
            all_columns = as_np_array(rdf.GetColumnNames())
            if columns is not None:
                columns = np.array(columns)
                missing_columns = np.setdiff1d(columns, all_columns)
                if len(missing_columns) > 0:
                    raise RuntimeError(f'missing column(s): {", ".join(missing_columns)}')
            else:
                columns = all_columns
            if remove_non_standard_types:
                column_types = np.array([rdf.GetColumnType(column) for column in columns])
                columns = columns[np.where(np.isin(column_types, root_datatypes))]
            return rdf.AsNumpy(list(columns))
    elif library.lower() == "uproot":
        import uproot
        f = uproot.open(filename)
        t = f[treename]
        if remove_non_standard_types:
            standard_columns = uproot_get_standard_columns(t)
            if columns is None:
                columns = standard_columns
            else:
                columns = [column for column in columns if column in standard_columns]
        return f[treename].arrays(columns, library="numpy")    
    else:
        raise RuntimeError(f'unknown library "{library}" for root data conversion')
        
def root2dataframe(filename:str, treename:str, columns:List[str]=None,
                   remove_non_standard_types:bool=True, library:str="uproot"):
    if library.lower() == "root":
        numpy_data = root2numpy(filename, treename, columns=columns,
                                remove_non_standard_types=remove_non_standard_types)
        import pandas as pd
        return pd.DataFrame(numpy_data)
    elif library.lower() == "uproot":
        import uproot
        f = uproot.open(filename)
        t = f[treename]
        if remove_non_standard_types:
            standard_columns = uproot_get_standard_columns(t)
            if columns is None:
                columns = standard_columns
            else:
                columns = [column for column in columns if column in standard_columns]
        return f[treename].arrays(columns, library="pd")