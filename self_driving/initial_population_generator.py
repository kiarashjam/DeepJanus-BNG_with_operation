import json

from core.config import Config
from core.folder_storage import SeedStorage
import os, glob, json
from random import shuffle, choice
from shutil import copy
from core.seed_pool_impl import SeedPoolFolder, SeedPoolRandom
from self_driving.edit_distance_polyline import iterative_levenshtein
import random



def get_spine(member):
    print("InitialPopulationGenerator........get_spine.........")
    print("member: ", member)
    with open(member) as json_file:
        spine = json.load(json_file)
        return spine['sample_nodes']

def get_min_distance_from_set(ind, solution):
    print("InitialPopulationGenerator........get_min_distance_from_set.........")
    distances = list()
    # print("ind:", ind)
    # print("solution:", solution)
    ind_spine = get_spine(ind)


    for road in solution:
        road_spine = get_spine(road)
        distances.append(iterative_levenshtein(ind_spine, road_spine))
    distances.sort()
    return distances[0]


def initial_pool_generator(config, problem):
    print("InitialPopulationGenerator........initial_pool_generator.........")
    good_members_found = 0
    attempts = 0
    storage = SeedStorage('initial_pool')

    # while good_members_found < config.POOLSIZE:#40:
    path = storage.get_path_by_index(good_members_found + 1)
    # if path.exists():
    #     print('member already exists', path)
    #     good_members_found += 1
    #     continue
    attempts += 1
    print(f'attempts {attempts} good {good_members_found} looking for {path}')
    member = problem.generate_random_member()
    member.evaluate()
    # if member.distance_to_boundary <= 0:
    #     continue
    member = problem.member_class().from_dict(member.to_dict())
    member.config = config
    member.problem = problem
    member.mutation_type = config.MUTATION_TYPE
    member.surrounding_type = config.SURROUNDING
    #member.clear_evaluation()
    if config.MUTATION_TYPE == 'MUT_FOG':
        member.fog_density = random.uniform(config.FOG_DENSITY_threshold_min, config.FOG_DENSITY_threshold_max)
        member.wet_foam_density = 0
        member.number_drop_rain = 0
        member.wet_ripple_density = 0
        member.number_of_bump = 0
        member.position_of_obstacle = (0, 0, 0)
        member.illumination = 0
    elif config.MUTATION_TYPE == 'MUT_RAIN':
        member.fog_density = 0
        member.wet_foam_density = 0
        member.number_drop_rain = random.randint(config.NUMBER_OF_DROP_RAIN_threshold_min, config.NUMBER_OF_DROP_RAIN_threshold_max)
        member.wet_ripple_density = 0
        member.number_of_bump = 0
        member.position_of_obstacle = (0, 0, 0)
        member.illumination = 0
    elif config.MUTATION_TYPE == 'MUT_WET_FOAM':
        member.fog_density = 0
        member.wet_foam_density = random.randint(config.FOG_DENSITY_threshold_min, config.FOG_DENSITY_threshold_max)
        member.number_drop_rain = 0
        member.wet_ripple_density = 0
        member.number_of_bump = 0
        member.position_of_obstacle = (0, 0, 0)
        member.illumination = 0
    elif config.MUTATION_TYPE == 'MUT_WET_RIPPLE':
        member.fog_density = 0
        member.wet_foam_density = 0
        member.number_drop_rain = 0
        member.wet_ripple_density = random.randint(config.WET_RIPPLE_threshold_min, config.WET_RIPPLE_threshold_max)
        member.number_of_bump = 0
        member.position_of_obstacle = (0, 0, 0)
        member.illumination = 0
    elif config.MUTATION_TYPE == 'MUT_ILLUMINATION':
        member.fog_density = 0
        member.wet_foam_density = 0
        member.number_drop_rain = 0
        member.wet_ripple_density = 0
        member.number_of_bump = 0
        member.position_of_obstacle = (0, 0, 0)
        member.illumination = random.uniform(config.ILLUMINATION_AMOUNT_threshold_min, config.ILLUMINATION_AMOUNT_threshold_max)
    elif config.MUTATION_TYPE == 'MUT_OBSTACLE':
        member.fog_density = 0
        member.wet_foam_density = 0
        member.number_drop_rain = 0
        member.wet_ripple_density = 0
        member.number_of_bump = 0
        member.position_of_obstacle = (0, 0, 0)
        member.illumination = 0
    elif config.MUTATION_TYPE == 'MUT_BUMP':
        member.fog_density = 0
        member.wet_foam_density = 0
        member.number_drop_rain = 0
        member.wet_ripple_density = 0
        member.number_of_bump = random.randint(config.NUMBER_BUMP_threshold_min, config.NUMBER_BUMP_threshold_max)
        member.position_of_obstacle = (0, 0, 0)
        member.illumination = 0




    member.distance_to_boundary = None
    good_members_found += 1
    path.write_text(json.dumps(member.to_dict()))

    return storage.folder

def initial_population_generator(path, config, problem):
    print("InitialPopulationGenerator........initial_population_generator.........")
    all_roads = [filename for filename in glob.glob(str(path)+"\*.json", recursive=True)]
    #all_roads += [filename for filename in glob.glob(path2)]

    shuffle(all_roads)

    roads = all_roads[:40]

    starting_point = choice(roads)

    original_set = list()
    original_set.append(starting_point)

    popsize = config.POPSIZE

    i = 0
    while i < popsize-1:
        max_dist = 0
        for ind in roads:

            dist = get_min_distance_from_set(ind, original_set)
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
        copy(road,dst)

if __name__ == '__main__':
    path = initial_pool_generator()
    #path = r"C:\Users\Aurora\new-DeepJanus\DeepJanus\DeepJanus-BNG\data\member_seeds\initial_pool"
    initial_population_generator(path)