import json

from core.config import Config
from core.folder_storage import SeedStorage
import math, glob, json
from random import shuffle, choice
from shutil import copy
from core.seed_pool_impl import SeedPoolFolder, SeedPoolRandom
from self_driving.edit_distance_polyline import iterative_levenshtein
from self_driving.beamng_member import BeamNGMember


def get_member(member):
    with open(member) as json_file:
        data = json.load(json_file)
        return BeamNGMember.from_dict(data)


def distance(road1, road2, config):
    fog_distances = road1.normalize(abs(road1.fog_density - road2.fog_density), config.FOG_DENSITY_threshold_max,
                                    config.FOG_DENSITY_threshold_min)
    rain_distance = road1.normalize(abs(road1.number_drop_rain - road2.number_drop_rain),
                                    config.NUMBER_OF_DROP_RAIN_threshold_max, config.NUMBER_OF_DROP_RAIN_threshold_min)
    size_drop_distance = road1.normalize(abs(road1.size_of_drop - road2.size_of_drop),
                                         config.SIZE_OF_DROP_threshold_min,
                                         config.SIZE_OF_DROP_threshold_max)
    foam_distance = road1.normalize(abs(road1.wet_foam_density - road2.wet_foam_density), config.WET_FOAM_threshold_max,
                                    config.WET_FOAM_threshold_min)
    illumination_distance = road1.normalize(abs(road1.illumination - road2.illumination),
                                            config.ILLUMINATION_AMOUNT_threshold_max,
                                            config.ILLUMINATION_AMOUNT_threshold_min)
    ripple_distance = road1.normalize(abs(road1.wet_ripple_density - road2.wet_ripple_density),
                                      config.WET_RIPPLE_threshold_max, config.WET_RIPPLE_threshold_min)
    bump_distance = road1.normalize(abs(road1.number_of_bump - road2.number_of_bump), config.NUMBER_BUMP_threshold_max,
                                    config.NUMBER_BUMP_threshold_min)
    road_shape_distance = iterative_levenshtein(road1.sample_nodes, road2.sample_nodes)
    obstacle_distance = math.sqrt(((road1.position_of_obstacle[0] - road2.position_of_obstacle[0]) ** 2) +
                                  ((road1.position_of_obstacle[1] - road2.position_of_obstacle[1]) ** 2))
    distances = fog_distances + rain_distance + size_drop_distance + foam_distance + illumination_distance + \
                ripple_distance + bump_distance + road_shape_distance + obstacle_distance
    return distances


def get_min_distance_from_set(ind, solution, config):
    distances = list()
    road = get_member(ind)
    for s in solution:
        member = get_member(s)
        distances.append(distance(member, road, config))
    distances.sort()
    return distances[0]


def initial_pool_generator(config, problem):
    good_members_found = 0
    attempts = 0
    storage = SeedStorage('initial_pool')

    while good_members_found < config.POOLSIZE:  # 40:
        path = storage.get_path_by_index(good_members_found + 1)
        attempts += 1
        print(f'attempts {attempts} good {good_members_found} looking for {path}')
        member = problem.generate_random_member()
        member.evaluate()
        if member.distance_to_boundary <= 0:
            continue
        member = problem.member_class().from_dict(member.to_dict())
        member.config = config
        member.problem = problem
        # member.clear_evaluation()

        member.distance_to_boundary = None
        good_members_found += 1
        path.write_text(json.dumps(member.to_dict()))

    return storage.folder


def initial_population_generator(path, config, problem):
    all_roads = [filename for filename in glob.glob(str(path) + "\*.json", recursive=True)]
    # all_roads += [filename for filename in glob.glob(path2)]

    shuffle(all_roads)

    roads = all_roads[:40]

    starting_point = choice(roads)

    original_set = list()
    original_set.append(starting_point)

    popsize = config.POPSIZE

    i = 0
    while i < popsize - 1:
        max_dist = 0
        for ind in roads:
            dist = get_min_distance_from_set(ind, original_set, config)
            if dist > max_dist:
                max_dist = dist
                best_ind = ind
        original_set.append(best_ind)
        i += 1

    base = config.initial_population_folder
    storage = SeedStorage(base)
    for index, road in enumerate(original_set):
        path = storage.get_path_by_index(index + 1)
        dst = path
        copy(road, dst)


if __name__ == '__main__':
    path = initial_pool_generator()
    # path = r"C:\Users\Aurora\new-DeepJanus\DeepJanus\DeepJanus-BNG\data\member_seeds\initial_pool"
    initial_population_generator(path)
