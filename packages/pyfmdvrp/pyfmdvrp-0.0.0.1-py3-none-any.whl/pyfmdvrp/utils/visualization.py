import matplotlib.pyplot as plt

from pyfmdvrp.engine.manager import FMDVRPManager
from pyfmdvrp.engine.status import CityStatus


def get_color(city):
    status = city.status
    if status == CityStatus.ACTIVE:
        color = 'gray'
    elif status == CityStatus.ASSIGNED:
        color = 'C{}'.format(city.assigned_by)
    elif status == CityStatus.COMPLETED:
        color = 'C{}'.format(city.assigned_by)
    else:
        raise RuntimeError("Not defined status")
    return color


def visualize_solution(manager_or_env):
    if isinstance(manager_or_env, FMDVRPManager):
        manager = manager_or_env
    else:
        manager = manager_or_env.manager

    city_pos = manager.problem['coordinate']
    depot_pos = manager.problem['depot_coordinate']

    city_clrs = [get_color(city) for city in manager.cities.values()]

    fig, ax = plt.subplots(1, 1, figsize=(5, 5))
    ax.scatter(city_pos[:, 0], city_pos[:, 1], c=city_clrs, label='city')
    ax.scatter(depot_pos[:, 0], depot_pos[:, 1], c='C2', marker='^', label='depot')

    for idx, sm in manager.vehicles.items():
        tour_x, tour_y = [], []
        for t_id in sm.tour_idx:
            if t_id <= manager.nd - 1:  # depot
                x, y = manager.depots[t_id].loc[0], manager.depots[t_id].loc[1]
            else:
                x, y = manager.cities[t_id].loc[0], manager.cities[t_id].loc[1]
            tour_x.append(x), tour_y.append(y)

        # tour_x, tour_y = city_pos[:, 0][sm.tour_idx], city_pos[:, 1][sm.tour_idx]
        ax.plot(tour_x, tour_y,
                color='C{}'.format(idx))

        ax.scatter(sm.loc[0], sm.loc[1],
                   label='Agent {}'.format(idx),
                   marker='*',
                   color='C{}'.format(idx))

        # visualizing current tour
        if sm.next_task is not None:
            cur_city_loc = sm.prev_task.loc
            next_city_loc = sm.next_task.loc
            cur_loc = sm.loc
            ax.plot([cur_city_loc[0], next_city_loc[0]],
                    [cur_city_loc[1], next_city_loc[1]],
                    ls='--', color='gray')
            ax.plot([cur_city_loc[0], cur_loc[0]],
                    [cur_city_loc[1], cur_loc[1]],
                    color='C{}'.format(sm.idx))

    plt.legend(loc='best')
    ax.legend()


if __name__ == '__main__':
    from pyfmdvrp.env import FMDVRPenv

    env = FMDVRPenv(2, 5, 3)
    visualize_solution(env)

    while True:
        _, _, done, _ = env.step()
        visualize_solution(env)
        if done: break
