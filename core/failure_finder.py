
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
    csv_columns = ["amount", "result"]
    start_process_time = datetime.now()
    print("###########start_process_time############" + str(start_process_time))
    print("###########start_time############" + str(start_time))
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
    initial_population_time = datetime.now() -  start_time
    start2 = datetime.now()
    i = 0
    every_evaluation_time=[]
    all_statuses =[]
    while i < len(pop):

        if config.MUTATION_TYPE == "MUT_ILLUMINATION":

            dict_already_done = {0: True}
            start3 = datetime.now()
            counter = 0
            pop[i].m1.illumination = 0
            pop[i].m2.illumination = 1/config.FAILURE_FINDER_PRECISE
            while counter < config.FAILURE_FINDER_PRECISE:
                pop[i].m1.illumination = pop[i].m1.illumination + (1 / config.FAILURE_FINDER_PRECISE)
                pop[i].m2.illumination = pop[i].m2.illumination + (1 / config.FAILURE_FINDER_PRECISE)
                if pop[i].m2.illumination > 1 :
                    pop[i].m2.illumination = 1
                result  = problem.pre_evaluate_members_binary_search(pop[i], dict_already_done)
                dict_already_done.update(result)
                print(dict_already_done)
                counter = counter + 1



        if config.MUTATION_TYPE == "MUT_FOG":
            while i < len(pop):
                dict_already_done ={0: True}
        all_statuses.append(dict_already_done)
        i = i + 1
    problem.failure_finder_save_data(all_statuses)