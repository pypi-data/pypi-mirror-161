import numpy as np

from pyfmdvrp.engine.status import CityStatus


class City:

    def __init__(self,
                 idx: int,
                 loc: np.array):
        self.idx = idx
        self.loc = np.array(loc)
        self.status = CityStatus.ACTIVE
        self.assigned_by = None

    def __repr__(self):
        msg = "City {} | Coord: {} | Status: {}".format(self.idx, self.loc, self.status)
        return msg
