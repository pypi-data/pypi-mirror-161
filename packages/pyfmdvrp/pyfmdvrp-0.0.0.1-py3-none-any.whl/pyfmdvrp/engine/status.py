from enum import Enum


class DepotStatus(Enum):
    ACTIVE = 0


class CityStatus(Enum):
    ACTIVE = 1  # Not visited/assigned to a salesman
    ASSIGNED = 2  # assigned to some salesman; the assigned salesmen is about to leave the tour/ or on the tour
    COMPLETED = 3  # already visited


class VehicleStatus(Enum):
    ACTIVE = 8  # ready to be assigned
    ASSIGNED = 9  # in transit
    TO_DEPOT = 10  # in depot transit
    COMPLETED = 11  # already return to the depot
