import pandas as pd
import bluebelt.analysis.performance

def performance(cls):
    def summary(self, values=None, **kwargs):
        check_attr(self, values)
        return bluebelt.analysis.performance.Summary(eval(f"self.{values}"), **kwargs)        

    def control_chart(self, values=None, **kwargs):
        check_attr(self, values)
        return bluebelt.analysis.performance.ControlChart(eval(f"self.{values}"), **kwargs)
        
    def run_chart(self, values=None, **kwargs):
        check_attr(self, values)
        return bluebelt.analysis.performance.RunChart(eval(f"self.{values}"), **kwargs)
    
    def process_capability(self, values=None, **kwargs):
        check_attr(self, values)
        return bluebelt.analysis.performance.ProcessCapability(eval(f"self.{values}"), **kwargs)
    
    def check_attr(self, values):
        attributes = []
        for attr, value in self.__dict__.items():
            if isinstance(value, pd.Series):
                attributes += ["'"+attr+"'"]
        attributes = ", ".join(attributes)
            
        if not values:
            raise ValueError(f"you must provide a 'values' parameter, please choose from {attributes}")
        if not hasattr(self, values):
           
            if len(attributes)>0:
                raise ValueError(f"'{values}' is not a valid attribute, please choose from {attributes}")
            else:
                raise ValueError(f"there are no valid attributes available, the performance function will not work...")
        
    setattr(cls, "summary", summary)
    setattr(cls, "control_chart", control_chart)
    setattr(cls, "run_chart", run_chart)
    setattr(cls, "process_capability", process_capability)
    
    return cls
