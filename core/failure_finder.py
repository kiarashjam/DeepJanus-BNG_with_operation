
import random

import numpy
from deap import base
from deap import creator
from deap import tools
from datetime import datetime

from core.log_setup import get_logger
from core.problem import Problem
from core.config import Config

log = get_logger(__file__)
def main(problem: Problem = None,start_time=None, seed=None):

    config = problem.config
    random.seed(seed)
    creator.create("FitnessMulti", base.Fitness, weights=config.fitness_weights)
    creator.create("Individual", problem.deap_individual_class(), fitness=creator.FitnessMulti)
    toolbox = base.Toolbox()
    problem.toolbox = toolbox
    toolbox.register("individual", problem.deap_generate_individual_binary_search)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    log.info("### Initializing population....")
    pop = toolbox.population(n=config.POPSIZE)
    i = 0
    all_statuses =[]
    while i < len(pop):


        dict_already_done = {0: True}
        counter = 0
        if config.MUTATION_TYPE == "MUT_ILLUMINATION":
            pop[i].m1.illumination = config.ILLUMINATION_AMOUNT_threshold_min
            pop[i].m2.illumination = config.ILLUMINATION_AMOUNT_threshold_max / config.FAILURE_FINDER_PRECISE
        elif config.MUTATION_TYPE == "MUT_FOG":
            pop[i].m1.fog_density = config.FOG_DENSITY_threshold_min
            pop[i].m2.fog_density = config.FOG_DENSITY_threshold_max / config.FAILURE_FINDER_PRECISE
        elif config.MUTATION_TYPE == "MUT_DROP_SIZE":
            pop[i].m1.size_of_drop = config.SIZE_OF_DROP_threshold_min
            pop[i].m2.size_of_drop = config.SIZE_OF_DROP_threshold_max / config.FAILURE_FINDER_PRECISE
        elif config.MUTATION_TYPE == 'MUT_WET_FOAM':
            pop[i].m1.wet_foam_density = config.WET_FOAM_threshold_min
            pop[i].m2.wet_foam_density = config.WET_FOAM_threshold_max / config.FAILURE_FINDER_PRECISE
        elif config.MUTATION_TYPE == 'MUT_WET_RIPPLE':
            pop[i].m1.wet_ripple_density = config.WET_RIPPLE_threshold_min
            pop[i].m2.wet_ripple_density = config.WET_RIPPLE_threshold_max / config.FAILURE_FINDER_PRECISE
        while counter < config.FAILURE_FINDER_PRECISE:
            if config.MUTATION_TYPE == "MUT_ILLUMINATION":
                pop[i].m1.illumination = pop[i].m1.illumination + \
                                         (config.ILLUMINATION_AMOUNT_threshold_max / config.FAILURE_FINDER_PRECISE)
                pop[i].m2.illumination = pop[i].m2.illumination + \
                                         (config.ILLUMINATION_AMOUNT_threshold_max  / config.FAILURE_FINDER_PRECISE)
                if pop[i].m2.illumination > config.ILLUMINATION_AMOUNT_threshold_max  :
                    pop[i].m2.illumination = config.ILLUMINATION_AMOUNT_threshold_max
            elif config.MUTATION_TYPE == "MUT_FOG":
                pop[i].m1.fog_density = pop[i].m1.fog_density +\
                                        (config.FOG_DENSITY_threshold_max / config.FAILURE_FINDER_PRECISE)
                pop[i].m2.fog_density = pop[i].m2.fog_density +\
                                        (config.FOG_DENSITY_threshold_max / config.FAILURE_FINDER_PRECISE)
                if pop[i].m2.fog_density > config.FOG_DENSITY_threshold_max:
                    pop[i].m2.fog_density = config.FOG_DENSITY_threshold_max

            elif config.MUTATION_TYPE == 'MUT_DROP_SIZE':
                pop[i].m1.size_of_drop = pop[i].m1.size_of_drop +\
                                         (config.SIZE_OF_DROP_threshold_max / config.FAILURE_FINDER_PRECISE)
                pop[i].m2.size_of_drop = pop[i].m2.size_of_drop +\
                                         (config.SIZE_OF_DROP_threshold_max / config.FAILURE_FINDER_PRECISE)
                if pop[i].m2.size_of_drop > config.SIZE_OF_DROP_threshold_max:
                    pop[i].m2.size_of_drop = config.SIZE_OF_DROP_threshold_max

            elif config.MUTATION_TYPE == 'MUT_WET_FOAM':
                pop[i].m1.wet_foam_density = pop[i].m1.wet_foam_density +\
                                         (config.WET_FOAM_threshold_max  / config.FAILURE_FINDER_PRECISE)
                pop[i].m2.wet_foam_density = pop[i].m2.wet_foam_density +\
                                         (config.WET_FOAM_threshold_max  / config.FAILURE_FINDER_PRECISE)
                if pop[i].m2.wet_foam_density > config.WET_FOAM_threshold_max :
                    pop[i].m2.wet_foam_density = config.WET_FOAM_threshold_max

            elif config.MUTATION_TYPE == 'MUT_WET_RIPPLE':
                pop[i].m1.wet_ripple_density = pop[i].m1.wet_ripple_density +\
                                         (config.WET_RIPPLE_threshold_max / config.FAILURE_FINDER_PRECISE)
                pop[i].m2.wet_ripple_density = pop[i].m2.wet_ripple_density +\
                                         (config.WET_RIPPLE_threshold_max / config.FAILURE_FINDER_PRECISE)
                if pop[i].m2.wet_ripple_density > config.WET_RIPPLE_threshold_max:
                    pop[i].m2.wet_ripple_density = config.WET_RIPPLE_threshold_max
            result  = problem.pre_evaluate_members_binary_search(pop[i], dict_already_done)
            dict_already_done.update(result)
            print(dict_already_done)
            counter = counter + 1
        all_statuses.append(dict_already_done)
        i = i + 1
    problem.failure_finder_save_data(all_statuses)