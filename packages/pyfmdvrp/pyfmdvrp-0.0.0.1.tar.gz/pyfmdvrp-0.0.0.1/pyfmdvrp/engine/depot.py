import numpy as np

from pyfmdvrp.engine.status import DepotStatus


class Depot:
    def __init__(self,
                 idx: int,
                 loc: list):
        self.status = DepotStatus.ACTIVE
        self.idx = idx
        self.loc = np.array(loc)