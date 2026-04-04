from dataclasses import dataclass

@dataclass
class Failure:
    category : str
    error : str
    url : str