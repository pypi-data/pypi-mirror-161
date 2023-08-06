
from . basic_element import BasicElement

class ComputationElement(BasicElement):
    def __init__(self, name, period, data):
        id = None
        super().__init__(id, data)
        self.name = name
        self.period = period
        self.data = data

    def to_ixbrl_elt(self, par, taxonomy):
        return []
        
