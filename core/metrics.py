from typing import List

import numpy as np
from core.individual import Individual
from core.member import Member
from core.config import  Config


def get_radius_seed(solution: List[Individual]):
    # Calculate the distance between each misclassified digit and the seed (mindist metric)
    if len(solution) == 0:
        return None
    distances_fog = list()
    distances_rain = list()
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
        ## fog distance
        fog_avg = (i.m1.fog_density + i.m2.fog_density) / 2
        distances_fog.append(fog_avg)
        # rain distance
        rain_avg = (i.m1.number_drop_rain + i.m2.number_drop_rain) / 2
        distances_rain.append(rain_avg)
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
        bump_avg= (i.m1.number_of_bump + i.m2.number_of_bump) / 2
        ### previous distance
        distances_bump.append(bump_avg)
        oob_input = i.members_by_sign()[0]
        dist = oob_input.distance(i.seed)
        distances_road_shape.append(dist)
        # the highest angle
        angles.append(i.m1.highest_angles)
        angles.append(i.m2.highest_angles)
    fog_avg =np.mean(distances_fog)
    fog_radius = normalization(fog_avg, Config.FOG_DENSITY_threshold_max,Config.FOG_DENSITY_threshold_min)
    rain_avg =np.mean(distances_rain)
    rain_radius = normalization(rain_avg, Config.NUMBER_OF_DROP_RAIN_threshold_max,Config.NUMBER_OF_DROP_RAIN_threshold_min)
    foam_avg =np.mean(distances_foam)
    foam_radius = normalization(foam_avg, Config.WET_FOAM_threshold_max,Config.WET_FOAM_threshold_min)
    ripple_avg =np.mean(distances_ripple)
    ripple_radius = normalization(ripple_avg, Config.WET_RIPPLE_threshold_max,Config.WET_RIPPLE_threshold_min)
    bump_avg =np.mean(distances_bump)
    bump_radius = normalization(bump_avg, Config.NUMBER_BUMP_threshold_max,Config.NUMBER_BUMP_threshold_min)
    obstacle_avg = np.mean(distances_obstacle)
    obstacle_radius = normalization(obstacle_avg, Config.ADDING_OBSTACLE_max,Config.ADDING_OBSTACLE_min)
    illumination_avg = np.mean(distances_illumination)
    illumination_radius = normalization(illumination_avg, Config.ILLUMINATION_AMOUNT_threshold_max,Config.ILLUMINATION_AMOUNT_threshold_min)
    road_shape_radius = np.mean(distances_road_shape)
    highest_angle = np.mean(angles)
    radius = fog_radius + rain_radius + foam_radius + ripple_radius + bump_radius + obstacle_radius + \
             illumination_radius + road_shape_radius
    return fog_radius, rain_radius , foam_radius , ripple_radius , illumination_radius, bump_radius , \
           obstacle_radius ,road_shape_radius , radius, mutation_type , fog_avg, rain_avg, foam_avg, ripple_avg, \
           bump_avg, obstacle_avg, illumination_avg , highest_angle

def normalization(value, max , min):
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
