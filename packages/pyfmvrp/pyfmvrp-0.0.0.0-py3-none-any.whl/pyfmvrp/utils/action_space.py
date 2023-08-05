def default_action_space(env, allow_zero_tour: bool = True):
    action_space = list(env.manager.active_city_idx)

    finish_delivery = len(action_space) == 0
    not_last_agent = env.m - (len(env.manager.to_depot_vehicle_idx) + len(env.manager.completed_vehicle_idx)) > 1

    if allow_zero_tour:
        cond = finish_delivery and not_last_agent
    else:
        c = len(env.manager.target_vehicle.tour) > 1
        cond = finish_delivery and not_last_agent and c

    if cond:
        action_space += list(env.manager.depot_index)

    finished = len(env.manager.completed_city_idx) == env.n
    if finished:
        action_space = list(env.manager.depot_index)

    return action_space
