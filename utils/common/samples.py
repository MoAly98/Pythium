''' We create a sample class '''
from typing import Dict, Callable, List
from pathlib import Path
class Sample:
    def __init__(self, name, tag, where, branches, selec=None):
        self._name = name
        self._tag = tag if isinstance(tag, list) else [tag]
        self._location = [Path(direc) for direc in where] if isinstance(where, list) else [Path(where)]
        self._branches = branches
        self.selec = selec
        self._data = None
    
    @property
    def name(self: "Sample")-> str :
        return self._name

    @property
    def branches(self: "Sample")->Dict[str, List["Branch"]] :
        return self._branches
    
    @property 
    def location(self: "Sample")->Path:
        return self._location

    @property
    def tag(self:"Sample")->str:
        return self._tag

    @property
    def data(self:"Sample"):
        return self._data

    @data.setter
    def data(self:"Sample", data: dict):
        self._data = data
