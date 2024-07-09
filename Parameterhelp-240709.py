import numpy as np
import time
from qcodes.instrument.parameter import MultiParameter, Parameter, ScaledParameter, ManualParameter
from qcodes.utils.validators import Numbers
from typing import Optional, List


class GateParameter(Parameter):
    def __init__(self, param, name, value_range, unit: Optional[str]='V', 
                 scaling: Optional[float]=1, offset: Optional[float]=0):
        
        super().__init__(name=name, instrument=param.instrument, unit=unit,
                         vals=Numbers(value_range[0], value_range[1]))
    
        self.param = param
        self.scaling = scaling
        self.offset = offset
        self.vals = Numbers(value_range[0], value_range[1])
        
    def get_raw(self):
        return self.param.get()
    
    def set_raw(self,val):
        dacval = self.scaling*val+self.offset
        self.vals.validate(dacval)
        self.param.set(dacval)
        
    def range(self, value_range):
        self.vals = Numbers(value_range[0], value_range[1])
        

class VirtualGateParameter(Parameter):
    def __init__(self, name, params, set_scaling, 
                 offsets: Optional[List[float]]=None, 
                 get_scaling: Optional[float]=1 ):
        
        super().__init__(name=name, instrument=params[0].instrument, 
                         unit=params[0].unit)
        
        self.params = params
        self.set_scaling = set_scaling
        self.get_scaling = get_scaling
        
        if offsets is None:
            self.offsets = np.zeros(len(params))
        else:
            self.offsets = offsets
            
    def get_raw(self):
        return self.get_scaling*self.params[0].get()
        
    def set_raw(self, val):
        for i in range(len(self.params)):
            dacval = self.set_scaling[i]*val+self.offsets[i]
            self.params[i].set(dacval)
            
    def get_all(self):
        values = []
        keys = []
        for param in self.params:
            values.append(param.get())
            keys.append(param.name)
        return dict(zip(keys, values))   
        

      
