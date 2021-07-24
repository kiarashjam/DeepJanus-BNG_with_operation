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
    start_process_time = datetime.now()
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
    initial_population_time = datetime.now() - start_time
    start2 = datetime.now()
    i = 0
    every_evaluation_time = []

    while i < len(pop):
        dict_already_done = {0: True}
        start3 = datetime.now()
        counter = 0
        if config.MUTATION_TYPE == "MUT_FOG":
            min_amount = config.FOG_DENSITY_threshold_min
            max_amount = config.FOG_DENSITY_threshold_max
            middle = (max_amount + min_amount) / 2
            pop[i].m1.fog_density = min_amount
            pop[i].m2.fog_density = middle
            while counter < config.NUM_ITERATIONS_BINARY_SEARCH:
                result = problem.pre_evaluate_members_binary_search(pop[i], dict_already_done)
                dict_already_done.update(result)
                if result[pop[i].m1.fog_density] != result[pop[i].m2.fog_density]:
                    max_amount = middle
                    middle = (min_amount + max_amount)/2
                    pop[i].m2.fog_density = middle
                    print("one success one failure")
                    counter = counter + 1
                elif result[pop[i].m1.fog_density] == result[pop[i].m2.fog_density] and result[pop[i].m1.fog_density] == True:
                    print("both are the same")
                    min_amount = middle
                    pop[i].m1.fog_density = min_amount
                    middle = (min_amount + max_amount) / 2
                    pop[i].m2.fog_density = middle
                    counter = counter + 1
                elif result[pop[i].m1.fog_density] == result[pop[i].m2.fog_density] and result[pop[i].m1.fog_density]==False:
                    min_amount = config.FOG_DENSITY_threshold_min
                    max_amount = config.FOG_DENSITY_threshold_max
                    middle = (max_amount+ min_amount) / 2
                    pop[i].m1.fog_density = min_amount
                    pop[i].m2.fog_density = middle
                    counter = 0
        elif config.MUTATION_TYPE == "MUT_DROP_SIZE":
            min_amount = config.SIZE_OF_DROP_threshold_min
            max_amount = config.SIZE_OF_DROP_threshold_max
            middle = (max_amount + min_amount) / 2
            pop[i].m1.size_of_drop = min_amount
            pop[i].m2.size_of_drop = middle
            while counter < config.NUM_ITERATIONS_BINARY_SEARCH:
                result = problem.pre_evaluate_members_binary_search(pop[i], dict_already_done)
                dict_already_done.update(result)
                if result[pop[i].m1.size_of_drop] != result[pop[i].m2.size_of_drop]:
                    max_amount = middle
                    middle = (min_amount + max_amount) / 2
                    pop[i].m2.size_of_drop = middle
                    print("one success one failure")
                    counter = counter + 1
                elif result[pop[i].m1.size_of_drop] == result[pop[i].m2.size_of_drop] and result[pop[i].m1.size_of_drop] == True:
                    print("both are the same")
                    min_amount = middle
                    pop[i].m1.size_of_drop = min_amount
                    middle = (min_amount + max_amount) / 2
                    pop[i].m2.size_of_drop = middle
                    counter = counter + 1
                elif result[pop[i].m1.wet_foam_density] == result[pop[i].m2.wet_foam_density] and result[pop[i].m1.wet_foam_density] == False:
                    min_amount = config.WET_FOAM_threshold_min
                    max_amount = config.WET_FOAM_threshold_max
                    middle = (max_amount + min_amount) / 2
                    pop[i].m1.wet_foam_density = min_amount
                    pop[i].m2.wet_foam_density = middle
                    counter = 0

        elif config.MUTATION_TYPE == "MUT_WET_FOAM":
            min_amount = config.WET_FOAM_threshold_min
            max_amount = config.WET_FOAM_threshold_max
            middle = (max_amount + min_amount) / 2
            pop[i].m1.wet_foam_density = min_amount
            pop[i].m2.wet_foam_density = middle
            while counter < config.NUM_ITERATIONS_BINARY_SEARCH:
                result = problem.pre_evaluate_members_binary_search(pop[i], dict_already_done)
                dict_already_done.update(result)
                if result[pop[i].m1.wet_foam_density] != result[pop[i].m2.wet_foam_density]:
                    max_amount = middle
                    middle = (min_amount + max_amount) / 2
                    pop[i].m2.wet_foam_density = middle
                    print("one success one failure")
                    counter = counter + 1
                elif result[pop[i].m1.wet_foam_density] == result[pop[i].m2.wet_foam_density] and result[pop[i].m1.wet_foam_density] == True:
                    print("both are the same")
                    min_amount = middle
                    pop[i].m1.wet_foam_density = min_amount
                    middle = (min_amount + max_amount) / 2
                    pop[i].m2.wet_foam_density = middle
                    counter = counter + 1
                elif result[pop[i].m1.wet_foam_density] == result[pop[i].m2.wet_foam_density]  and result[pop[i].m1.wet_foam_density] == False:
                    min_amount = config.WET_FOAM_threshold_min
                    max_amount = config.WET_FOAM_threshold_max
                    middle = (max_amount + min_amount) / 2
                    pop[i].m1.wet_foam_density = min_amount
                    pop[i].m2.wet_foam_density = middle
                    counter = 0

        elif config.MUTATION_TYPE == "MUT_WET_RIPPLE":
            min_amount = config.WET_RIPPLE_threshold_min
            max_amount = config.WET_RIPPLE_threshold_max
            middle = (max_amount + min_amount) / 2
            pop[i].m1.wet_ripple_density = min_amount
            pop[i].m2.wet_ripple_density = middle
            while counter < config.NUM_ITERATIONS_BINARY_SEARCH:
                result = problem.pre_evaluate_members_binary_search(pop[i], dict_already_done)
                dict_already_done.update(result)
                if result[pop[i].m1.wet_ripple_density] != result[pop[i].m2.wet_ripple_density]:
                    max_amount = middle
                    middle = (min_amount + max_amount)/2
                    pop[i].m2.wet_ripple_density = middle
                    print("one success one failure")
                    counter = counter + 1
                elif result[pop[i].m1.wet_ripple_density] == result[pop[i].m2.wet_ripple_density]  and result[pop[i].m1.wet_ripple_density] == True:
                    print("both are the same")
                    min_amount = middle
                    pop[i].m1.wet_ripple_density = min_amount
                    middle = (min_amount + max_amount) / 2
                    pop[i].m2.wet_ripple_density = middle
                    counter = counter + 1
                elif result[pop[i].m1.wet_ripple_density] == result[pop[i].m2.wet_ripple_density] and result[pop[i].m1.wet_ripple_density] == False:
                    min_amount = config.WET_RIPPLE_threshold_min
                    max_amount = config.WET_RIPPLE_threshold_max
                    middle = (max_amount+ min_amount) / 2
                    pop[i].m1.wet_ripple_density = min_amount
                    pop[i].m2.wet_ripple_density = middle
                    counter = 0
        elif config.MUTATION_TYPE == "MUT_ILLUMINATION":
            min_amount = config.ILLUMINATION_AMOUNT_threshold_min
            max_amount = config.ILLUMINATION_AMOUNT_threshold_max
            middle = (max_amount + min_amount) / 2
            pop[i].m1.illumination = min_amount
            pop[i].m2.illumination = middle
            while counter < config.NUM_ITERATIONS_BINARY_SEARCH:
                result = problem.pre_evaluate_members_binary_search(pop[i], dict_already_done)
                dict_already_done.update(result)
                if result[pop[i].m1.illumination] != result[pop[i].m2.illumination]:
                    max_amount = middle
                    middle = (min_amount + max_amount)/2
                    pop[i].m2.illumination = middle
                    print("one success one failure")
                    counter = counter + 1
                elif result[pop[i].m1.illumination] == result[pop[i].m2.illumination] and result[pop[i].m1.illumination] == True:
                    print("both are the same")
                    min_amount = middle
                    pop[i].m1.illumination = min_amount
                    middle = (min_amount + max_amount) / 2
                    pop[i].m2.illumination = middle
                    counter = counter + 1
                elif result[pop[i].m1.illumination] == result[pop[i].m2.illumination] and result[pop[i].m1.illumination] == False:
                    min_amount = 0
                    max_amount = 1
                    middle = (max_amount + min_amount) / 2
                    pop[i].m1.illumination = min_amount
                    pop[i].m2.illumination = middle
                    counter = 0

            print("## min_amount = " + str(min_amount))
            print("## max_amount = " + str(max_amount))
            print("## middle_amount = " + str(middle))
        every_evaluation_time.append(str(datetime.now() - start3))
        i = i + 1
    evaluation_population_time = datetime.now() - start2
    whole_process_time = datetime.now() - start_process_time
    time_binary_search = {
        "evaluation_population_time":evaluation_population_time,
        "whole_process_time":whole_process_time,
        "initial_population_time":initial_population_time,
        "every_evaluation_time":every_evaluation_time
    }

    problem.binary_save_data(pop, time_binary_search)

