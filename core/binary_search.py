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
    print("###########start_process_time############" + str(start_process_time))
    print("###########start_time############" + str(start_time))
    config = problem.config
    random.seed(seed)

#
#     creator.create("FitnessMulti", base.Fitness, weights=config.fitness_weights)
#     creator.create("Individual", problem.deap_individual_class(), fitness=creator.FitnessMulti)
#
#     #####
#
#     toolbox = base.Toolbox()
#     problem.toolbox = toolbox
#
#
#     ####
#
#     toolbox.register("individual", problem.deap_generate_individual_binary_search)
#     toolbox.register("population", tools.initRepeat, list, toolbox.individual)
#
#
#     ###

# DEAP framework setup
    # We define a bi-objective fitness function.
    # 1. Maximize the sparseness minus an amount due to the distance between members
    # 2. Minimize the distance to the decision boundary
    creator.create("FitnessMulti", base.Fitness, weights=config.fitness_weights)
    creator.create("Individual", problem.deap_individual_class(), fitness=creator.FitnessMulti)

    toolbox = base.Toolbox()
    problem.toolbox = toolbox
    # We need to define the individual, the evaluation function (OOBs), mutation
    # toolbox.register("individual", tools.initIterate, creator.Individual)
    toolbox.register("individual", problem.deap_generate_individual_binary_search)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    # toolbox.register("evaluate", problem.deap_evaluate_individual)
    # toolbox.register("mutate", problem.deap_mutate_individual)
    # toolbox.register("select", tools.selNSGA2)

    # stats = tools.Statistics(lambda ind: ind.fitness.values)
    # stats.register("min", numpy.min, axis=0)
    # stats.register("max", numpy.max, axis=0)
    # stats.register("avg", numpy.mean, axis=0)
    # stats.register("std", numpy.std, axis=0)
    # logbook = tools.Logbook()
    # logbook.header = "gen", "evals", "min", "max", "avg", "std"

    log.info("### Initializing population....")
    pop = toolbox.population(n=config.POPSIZE)
    initial_population_time = datetime.now() -  start_time
    start2 = datetime.now()
    i = 0
    every_evaluation_time=[]

    while i < len(pop):
        start3 = datetime.now()
        counter = 0
        min_amount = 0
        max_amount = 1
        middle = (max_amount + min_amount) / 2
        pop[i].m2.fog_density = middle
        while counter < config.NUM_ITERATIONS_BINARY_SEARCH:
            result = problem.pre_evaluate_members_binary_search(pop, i)

            # fitnesses = toolbox.map(toolbox.evaluate, [pop[i]])
            # for ind, fit in zip([pop[i]], fitnesses):
            #     ind.fitness.values = fit
            # problem.archive.process_population(pop)
            if result[0] != result[1]:
                max_amount = middle
                middle = (min_amount + max_amount)/2
                pop[i].m2.fog_density = middle
                print("one succcess one failure")
                counter = counter + 1
            else:
                print("both are the same")
                min_amount = middle
                pop[i].m1.fog_density = min_amount
                middle = (min_amount + max_amount) / 2
                pop[i].m2.fog_density = middle
                counter = counter + 1
            print("## fog amount fo the first member = "+str(pop[i].m1.fog_density))
            print("## fog amount fo the second member = " + str(pop[i].m2.fog_density))
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

    problem.binary_save_data(pop,time_binary_search)

