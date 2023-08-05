import numpy as np


def get_uniform_problem(n: int, m: int, nd: int) -> dict:
    coords = np.random.uniform(0.0, 1.0, size=(n, 2))
    depot_coords = np.random.uniform(0.0, 1.0, size=(nd, 2))
    v_pos_idx = np.random.choice(nd, size=m)

    problem = dict()
    problem["coordinate"] = coords
    problem['depot_coordinate'] = depot_coords
    problem["vehicle_position_idx"] = v_pos_idx
    problem["vehicle_position"] = depot_coords[v_pos_idx, :]
    problem["num_vehicles"] = m
    problem["num_cities"] = n
    problem["num_depots"] = nd

    return problem