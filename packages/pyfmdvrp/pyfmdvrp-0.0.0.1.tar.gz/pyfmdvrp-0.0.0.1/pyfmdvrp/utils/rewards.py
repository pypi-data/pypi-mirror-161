def makespan_reward(env):
    makespan = 0 if not env.manager.done else env.manager.time
    reward = -1.0 * makespan
    return reward