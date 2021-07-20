from typing import List

import numpy as np
from core.individual import Individual
from core.member import Member
from core.config import Config


def get_radius_seed(solution: List[Individual]):
    # Calculate the distance between each misclassified digit and the seed (mindist metric)
    if len(solution) == 0:
        return None
    distances_fog = list()
    distances_rain = list()
    distances_size_of_drop = list()
    distances_foam = list()
    distances_ripple = list()
    distances_obstacle = list()
    distances_bump = list()
    distances_illumination = list()
    distances_road_shape = list()
    angles = list()
    for i in solution:
        if i.seed.mutation_type == 'MUT_FOG':
            mutation_type = "changing the fog density"
        elif i.seed.mutation_type == 'MUT_RAIN':
            mutation_type = "changing the amount of rain"
        elif i.seed.mutation_type == 'MUT_DROP_SIZE':
            mutation_type = "changing the size of the drop in rain"
        elif i.seed.mutation_type == 'MUT_WET_FOAM':
            mutation_type = "changing the density of foam in the wet road"
        elif i.seed.mutation_type == 'MUT_WET_RIPPLE':
            mutation_type = "changing the amount of ripple in the wet road"
        elif i.seed.mutation_type == 'MUT_ILLUMINATION':
            mutation_type = "changing the illumination of the road "
        elif i.seed.mutation_type == 'MUT_OBSTACLE':
            mutation_type = "changing the position if the obstacle "
        elif i.seed.mutation_type == 'MUT_BUMP':
            mutation_type = "changing the height of the bump "
        elif i.seed.mutation_type == 'MUT_CONTROL_POINTS':
            mutation_type = "changing the shape of the road"
        elif i.seed.mutation_type == 'MUT_RAIN_WHOLE':
            mutation_type = "changing the number and size of the rain drops in rain"
        elif i.seed.mutation_type == 'MUT_STORM':
            mutation_type = "changing the number of drops and size of the rain drops,amount of  fog density," \
                            " amount of foam in the wet floor , amount of ripple in the wet floor"
        elif i.seed.mutation_type == 'MUT_WHOLE_WET_FLOOR':
            mutation_type = "changing the amount of foam and ripple in the wet floor"


        # fog distance
        fog_avg = (i.m1.fog_density + i.m2.fog_density) / 2
        distances_fog.append(fog_avg)
        # rain distance
        rain_avg = (i.m1.number_drop_rain + i.m2.number_drop_rain) / 2
        distances_rain.append(rain_avg)
        # size of the drop
        size_drop_avg = (i.m1.size_of_drop + i.m2.size_of_drop) / 2
        distances_size_of_drop.append(size_drop_avg)
        # foam distance
        foam_avg = (i.m1.wet_foam_density + i.m2.wet_foam_density) / 2
        distances_foam.append(foam_avg)
        # ripple distance
        ripple_avg = (i.m1.wet_ripple_density + i.m2.wet_ripple_density) / 2
        distances_ripple.append(ripple_avg)
        # illumination distance
        illumination_avg = (i.m1.illumination + i.m2.illumination) / 2
        distances_illumination.append(illumination_avg)
        # obstacle_avg = (i.m1.position_of_obstacle + i.m2.position_of_obstacle) / 2
        obstacle_avg = 0
        distances_obstacle.append(obstacle_avg)
        # bump distance
        bump_avg = (i.m1.number_of_bump + i.m2.number_of_bump) / 2
        distances_bump.append(bump_avg)
        ### previous distance
        oob_input = i.members_by_sign()[0]
        dist = oob_input.distance(i.seed)
        distances_road_shape.append(dist)
        # the highest angle
        angles.append(i.m1.highest_angles)
        angles.append(i.m2.highest_angles)
    # average normalize  distance of fog
    fog_avg = np.mean(distances_fog)
    fog_radius = normalization(fog_avg, Config.FOG_DENSITY_threshold_max,
                               Config.FOG_DENSITY_threshold_min)
    # average normalize  distance of rain
    rain_avg = np.mean(distances_rain)
    rain_radius = normalization(rain_avg, Config.NUMBER_OF_DROP_RAIN_threshold_max,
                                Config.NUMBER_OF_DROP_RAIN_threshold_min)
    # average normalize  distance of drop size
    size_drop_avg = np.mean(distances_size_of_drop)
    drop_size_radius = normalization(size_drop_avg, Config.SIZE_OF_DROP_threshold_max,
                                     Config.SIZE_OF_DROP_threshold_min)

    # average normalize  distance of foam
    foam_avg = np.mean(distances_foam)
    foam_radius = normalization(foam_avg, Config.WET_FOAM_threshold_max,
                                Config.WET_FOAM_threshold_min)
    # average normalize  distance of ripple
    ripple_avg = np.mean(distances_ripple)
    ripple_radius = normalization(ripple_avg, Config.WET_RIPPLE_threshold_max,
                                  Config.WET_RIPPLE_threshold_min)
    # average normalize  distance of bump
    bump_avg = np.mean(distances_bump)
    bump_radius = normalization(bump_avg, Config.NUMBER_BUMP_threshold_max,
                                Config.NUMBER_BUMP_threshold_min)
    # average normalize  distance of obstacle
    obstacle_avg = np.mean(distances_obstacle)
    obstacle_radius = normalization(obstacle_avg, Config.ADDING_OBSTACLE_max,
                                    Config.ADDING_OBSTACLE_min)
    # average normalize  distance of illumination
    illumination_avg = np.mean(distances_illumination)
    illumination_radius = normalization(illumination_avg, Config.ILLUMINATION_AMOUNT_threshold_max,
                                        Config.ILLUMINATION_AMOUNT_threshold_min)
    # average normalize  distance of whole system the operation plus road shape
    road_shape_radius = np.mean(distances_road_shape)
    highest_angle = np.mean(angles)
    radius = road_shape_radius
    return fog_radius, rain_radius,size_drop_avg, foam_radius, ripple_radius, illumination_radius, bump_radius, \
           obstacle_radius, road_shape_radius, radius, mutation_type, fog_avg, rain_avg, size_drop_avg, foam_avg, ripple_avg, \
           bump_avg, obstacle_avg, illumination_avg, highest_angle


def normalization(value, max, min):
    return (value - min) / (max - min)


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
