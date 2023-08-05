from typing import Optional, Union, List, Dict

import pandas as pd
import numpy as np

from quickstats.plots import AbstractPlot

class Histo1DPlot(AbstractPlot):
    
    STYLES = {
        'hist':{
            'histtype': 'stepfilled',
            'rwidth': 0,
            'linewidth': 2,
            'edgecolor': 'k'
        }    
    } 
    
    def __init__(self, data:Union[pd.DataFrame, Dict[str, np.ndarray], np.ndarray, List],
                 label_map:Optional[Dict[str, str]]=None,
                 color_cycle:Optional[Union[Dict, str]]="hist_series",
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Dict]=None,
                 config:Optional[Dict]=None):
        
        if not isinstance(data, (list, np.ndarray, pd.DataFrame, dict)):
            raise ValueError(f"unsupported data type: {type(self.data)}")
        self.data = data
        self.label_map = label_map
        
        super().__init__(color_cycle=color_cycle,
                         styles=styles,
                         analysis_label_options=analysis_label_options,
                         config=config)
        
    def draw(self, columns:Optional[Union[str, List[str]]]=None,
             bins:int=None, range=None, stacked:bool=False,
             density:bool=False, ypad:Optional[float]=None,
             xlabel:Optional[str]=None, ylabel:Optional[str]="Events",
             xmin:Optional[float]=None, xmax:Optional[float]=None,
             logy:bool=False):
        
        if isinstance(columns, str):
            columns = [columns]
        
        x_collection = []
        if isinstance(self.data, (list, np.ndarray)):
            if columns is not None:
                raise ValueError("specification of column(s) are not allowed with single data array as input")
            x_collection.append(self.data)
        elif isinstance(self.data, pd.DataFrame):
            for column in columns:
                if column not in self.data.columns:
                    raise RuntimeError(f"dataframe has no column named \"{column}\"")
                x = self.data[column].values
                x = x[np.isfinite(x)]
                x_collection.append(x)
        elif isinstance(self.data, dict):
            for column in columns:
                if column not in self.data:
                    raise RuntimeError(f"data dictionary has no key named \"{column}\"")
                x = self.data[column]
                x = x[np.isfinite(x)]
                x_collection.append(x)
        else:
            raise ValueError(f"unsupported data type: {type(self.data)}")
        
        n_columns = len(x_collection)
        if n_columns > 1:
            if self.label_map is None:
                labels = list(columns)
            else:
                labels = [self.label_map.get(column, column) for column in columns]
        else:
            labels = None
        
        ax = self.draw_frame(logy=logy)
        
        n, bins, patches = ax.hist(x_collection, bins=bins, range=range,
                                   stacked=stacked, density=density,
                                   label=labels, **self.styles["hist"])
        
        if n_columns > 1:
            ax.legend(**self.styles['legend'])
        
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        self.set_axis_range(ax, xmin=xmin, xmax=xmax, ypad=ypad)  
        
        return ax