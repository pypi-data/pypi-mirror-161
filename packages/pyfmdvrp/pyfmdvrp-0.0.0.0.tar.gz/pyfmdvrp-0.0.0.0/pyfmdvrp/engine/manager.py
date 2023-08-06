from copy import deepcopy

import numpy as np

from pyfmdvrp.engine.city import City
from pyfmdvrp.engine.depot import Depot
from pyfmdvrp.engine.status import VehicleStatus, CityStatus
from pyfmdvrp.engine.vehicle import Vehicle, calc_dist


class FMDVRPManager:

    def __init__(self, problem):
        self.n = problem['num_cities']  # number of requests (the pair of pickup and delivery)
        self.m = problem['num_vehicles']  # number of vehicles
        self.nd = problem['num_depots']  # number of depots

        self.depots = {i: Depot(idx=i, loc=problem['depot_coordinate'][i]) for i in range(self.nd)}
        self.cities = {i + self.nd: City(idx=i + self.nd,
                                         loc=problem['coordinate'][i]) for i in range(self.n)}

        self.vehicles = {self.n + self.nd + i: Vehicle(idx=self.n + self.nd + i) for i in range(self.m)}
        for i, v in enumerate(self.vehicles.values()):
            initial_depot = self.depots[problem['vehicle_position_idx'][i]]
            v.set_initial_task(initial_depot)

        self.problem = problem

        self.depot_index = set(self.depots.keys())

        self.active_vehicle_idx = set(self.vehicles.keys())
        self.assigned_vehicle_idx = set()
        self.to_depot_vehicle_idx = set()
        self.completed_vehicle_idx = set()

        self.active_city_idx = set(self.cities.keys())
        self.assigned_city_idx = set()
        self.completed_city_idx = set()

        self.target_vehicle = None
        self.target_vehicle_idx = None
        self.time = 0
        self.done = False
        self.set_target_vehicle()

    def set_target_vehicle(self):
        idle_vehicle_idx = list(self.get_idle_vehicle_indices())
        target_idx = np.random.choice(idle_vehicle_idx)
        self.vehicles[target_idx].is_target = True
        self.target_vehicle = self.vehicles[target_idx]
        self.target_vehicle_idx = target_idx

    def get_idle_vehicle_indices(self):
        return deepcopy(self.active_vehicle_idx)

    def set_next_task(self, vehicle_idx, task_idx):
        vehicle = self.vehicles[vehicle_idx]
        assert vehicle.status == VehicleStatus.ACTIVE

        if task_idx in self.depot_index:  # when the task is the depot.
            vehicle.status = VehicleStatus.TO_DEPOT
            vehicle.next_task = self.depots[task_idx]
            vehicle.next_task_idx = task_idx

            # adjust "active vehicle idx"
            self.active_vehicle_idx.remove(vehicle_idx)
            self.to_depot_vehicle_idx.add(vehicle_idx)

        else:  # when the task is city
            vehicle.status = VehicleStatus.ASSIGNED

            city = self.cities[task_idx]
            city.status = CityStatus.ASSIGNED
            city.assigned_by = vehicle_idx

            self.active_city_idx.remove(task_idx)
            self.assigned_city_idx.add(task_idx)

            vehicle.next_task = city
            vehicle.next_task_idx = city.idx

            # adjust "active vehicle idx"
            self.active_vehicle_idx.remove(vehicle_idx)
            self.assigned_vehicle_idx.add(vehicle_idx)

        vehicle.remaining_distance = calc_dist(vehicle.loc, vehicle.next_task.loc)

    def transit(self):
        assert len(self.get_idle_vehicle_indices()) == 0
        assert len(self.assigned_vehicle_idx) + len(self.to_depot_vehicle_idx) >= 1

        if len(self.assigned_vehicle_idx) == 0:  # all agents are returning to the depot
            dt = -1e10
            for vehicle_idx in list(self.to_depot_vehicle_idx):
                dt = max(dt, self.vehicles[vehicle_idx].remaining_distance)

            # simulate the "to-depot" vehicles
            for vehicle_idx in list(self.to_depot_vehicle_idx):
                _dt = min(self.vehicles[vehicle_idx].remaining_distance, dt)
                self.vehicles[vehicle_idx].travel(_dt, self)
            self.done = True
            self.time += dt
        else:
            dt = 1e10
            for vehicle_idx in list(self.assigned_vehicle_idx):
                dt = min(dt, self.vehicles[vehicle_idx].remaining_distance)

            # simulate the "assigned" vehicles
            for vehicle_idx in list(self.assigned_vehicle_idx):
                self.vehicles[vehicle_idx].travel(dt, self)

            # simulate the "to-depot" vehicles
            for vehicle_idx in list(self.to_depot_vehicle_idx):
                _dt = min(self.vehicles[vehicle_idx].remaining_distance, dt)
                self.vehicles[vehicle_idx].travel(_dt, self)
            self.time += dt
