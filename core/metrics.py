from typing import List

import numpy as np
from core.individual import Individual
from core.member import Member


def get_radius_seed(solution: List[Individual]):
    # Calculate the distance between each misclassified digit and the seed (mindist metric)
    if len(solution) == 0:
        return None
    distances = list()
    for i in solution:
        if i.seed.mutation_type == 'MUT_FOG':
            fog_avg = (i.m1.fog_density + i.m2.fog_density) / 2
            distances.append(fog_avg)
        elif i.seed.mutation_type == 'MUT_RAIN':
            fog_avg = (i.m1.number_drop_rain + i.m2.number_drop_rain) / 2
            distances.append(fog_avg)
        elif i.seed.mutation_type == 'MUT_WET_FOAM':
            fog_avg = (i.m1.wet_foam_density + i.m2.wet_foam_density) / 2
            distances.append(fog_avg)
        elif i.seed.mutation_type == 'MUT_WET_RIPPLE':
            fog_avg = (i.m1.wet_ripple_density + i.m2.wet_ripple_density) / 2
            distances.append(fog_avg)
        elif i.seed.mutation_type == 'MUT_ILLUMINATION':
            fog_avg = (i.m1.illumination + i.m2.illumination) / 2
            distances.append(fog_avg)
        elif i.seed.mutation_type == 'MUT_OBSTACLE':
            fog_avg = (i.m1.position_of_obstacle + i.m2.position_of_obstacle) / 2
            distances.append(fog_avg)
        elif i.seed.mutation_type == 'MUT_BUMP':
            fog_avg = (i.m1.number_of_bump + i.m2.number_of_bump) / 2
            distances.append(fog_avg)
        elif i.seed.mutation_type == 'MUT_CONTROL_POINTS':
            oob_input = i.members_by_sign()[0]
            dist = oob_input.distance(i.seed)
            distances.append(dist)

    radius = np.mean(distances)
    return radius


def get_diameter(solution: List[Member]):
    # Calculate the distance between each misclassified digit and the farthest element of the solution (diameter metric)
    if len(solution) == 0:
        return None
    max_distances = list()
    for i1 in solution:
        maxdist = float(0)
        for i2 in solution:
            if i1 != i2:
                dist = i1.distance(i2)
                if dist > maxdist:
                    maxdist = dist
        max_distances.append(maxdist)
    diameter = np.mean(max_distances)
    return diameter
