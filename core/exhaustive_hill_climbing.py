import random

import numpy as np
from deap import base
from deap import creator
from deap import tools
from datetime import datetime

from core.log_setup import get_logger
from core.problem import Problem
from core.config import Config

log = get_logger(__file__)


def generate_base_solution(type):
    if type == "MUT_FOG_DROP_SIZE":
        return [0, 0]
    elif type == "MUT_RAIN_WHOLE":
        return [1000, 0.02]
    elif type == "MUT_STORM":
        return [0, 1000, 0.01, 0, 0]


def evaluate(solution, base, pop, problem):
    if pop.m1.mutation_type == "MUT_FOG_DROP_SIZE":
        pop.m1.fog_density = base[0]
        pop.m1.size_of_drop = base[1]
        pop.m2.fog_density = solution[0]
        pop.m2.size_of_drop = solution[1]
    elif pop.m1.mutation_type == "MUT_RAIN_WHOLE":
        pop.m1.number_drop_rain = int(base[0])
        pop.m1.size_of_drop = base[1]
        pop.m2.number_drop_rain = int(solution[0])
        pop.m2.size_of_drop = solution[1]
    if pop.m1.mutation_type == "MUT_STORM":
        pop.m1.fog_density = base[0]
        pop.m1.number_drop_rain = base[1]
        pop.m1.size_of_drop = base[2]
        pop.m1.wet_foam_density = base[3]
        pop.m1.wet_ripple_density = base[4]
        pop.m2.fog_density = solution[0]
        pop.m2.number_drop_rain = solution[1]
        pop.m2.size_of_drop = solution[2]
        pop.m2.wet_foam_density = solution[3]
        pop.m2.wet_ripple_density = solution[4]
    result, distances = problem.pre_evaluate_members_hill_climbing(pop)
    print(distances)
    print(result)
    return result, distances


def mutate_solution(base, pop, problem):
    if pop.m1.mutation_type == "MUT_FOG_DROP_SIZE":
        first_attempt_success, first_attempt_distance = evaluate(
            [base[0] + problem.config.MUTATION_FOG_PRECISE, base[1]], base, pop, problem)
        second_attempt_success, second_attempt_distance = evaluate(
            [base[0], base[1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE], base, pop, problem)
        if first_attempt_distance <= second_attempt_distance:
            return [base[0] + problem.config.MUTATION_FOG_PRECISE, base[1]], first_attempt_success
        else:
            return [base[0], base[1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE], second_attempt_success
    elif pop.m1.mutation_type == "MUT_RAIN_WHOLE":
        first_attempt_success, first_attempt_distance = evaluate(
            [base[0] + problem.config.MUTATION_RAIN_PRECISE, base[1]], base, pop,
            problem)
        second_attempt_success, second_attempt_distance = evaluate(
            [base[0], base[1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE],
            base, pop, problem)
        if first_attempt_distance <= second_attempt_distance:
            return [base[0] + problem.config.MUTATION_RAIN_PRECISE, base[1]], first_attempt_success
        else:
            return [base[0], base[1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE], second_attempt_success

    elif pop.m1.mutation_type == "MUT_STORM":
        first_attempt_success, first_attempt_distance = evaluate(
            [base[0] + problem.config.MUTATION_FOG_PRECISE, base[1], base[2], base[3], base[4]], base, pop, problem)
        second_attempt_success, second_attempt_distance = evaluate(
            [base[0], base[1] + problem.config.MUTATION_RAIN_PRECISE,
             base[2], base[3], base[4]], base, pop, problem)
        third_attempt_success, third_attempt_distance = evaluate([base[0], base[1],base[2] +
                                                                  problem.config.MUTATION_SIZE_OF_DROP_PRECISE,
                                                                  base[3], base[4]], base, pop, problem)
        forth_attempt_success, forth_attempt_distance = evaluate([base[0], base[1], base[2],
                                                                  base[3] + problem.config.MUTATION_FOAM_PRECISE,
                                                                  base[4]], base, pop, problem)
        fifth_attempt_success, fifth_attempt_distance = evaluate([base[0], base[1], base[2], base[3],
                                                                  base[4] + problem.config.MUTATION_RIPPLE_PRECISE],
                                                                 base, pop, problem)
        if np.min([first_attempt_distance, second_attempt_distance, third_attempt_distance, forth_attempt_distance,
                   fifth_attempt_distance]) == first_attempt_distance:
            print("first")
            return [base[0] + problem.config.MUTATION_FOG_PRECISE, base[1], base[2], base[3],
                    base[4]], first_attempt_success
        elif np.min([first_attempt_distance, second_attempt_distance, third_attempt_distance, forth_attempt_distance,
                     fifth_attempt_distance]) == second_attempt_distance:
            print("second")
            return [base[0] , base[1] + problem.config.MUTATION_RAIN_PRECISE, base[2], base[3],
                    base[4]], second_attempt_success
        elif np.min([first_attempt_distance, second_attempt_distance, third_attempt_distance, forth_attempt_distance,
                     fifth_attempt_distance]) == third_attempt_distance:
            print("third")
            return [base[0], base[1], base[2] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE, base[3],
                    base[4]], third_attempt_success
        elif np.min([first_attempt_distance, second_attempt_distance, third_attempt_distance, forth_attempt_distance,
                     fifth_attempt_distance]) == forth_attempt_distance:
            print("forth")
            return [base[0], base[1], base[2], base[3] + problem.config.MUTATION_FOAM_PRECISE,
                    base[4]], forth_attempt_success
        elif np.min([first_attempt_distance, second_attempt_distance, third_attempt_distance, forth_attempt_distance,
                     fifth_attempt_distance]) == fifth_attempt_distance:
            print("fifth")
            return [base[0], base[1], base[2], base[3],
                    base[4] + problem.config.MUTATION_RIPPLE_PRECISE], fifth_attempt_success


def main(problem: Problem = None, start_time=None, seed=None):
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
    base_amount = generate_base_solution(pop[i].m1.mutation_type)
    while i < len(pop):
        while True:
            best_result, status = mutate_solution(base_amount, pop[i], problem)
            print(best_result)
            if pop[i].m1.mutation_type == "MUT_FOG_DROP_SIZE":
                pop[i].m1.fog_density = best_result[0]
                pop[i].m1.size_of_drop = best_result[1]
                pop[i].m2.fog_density = best_result[0]
                pop[i].m2.size_of_drop = best_result[1]
            elif pop[i].m1.mutation_type == "MUT_RAIN_WHOLE":
                pop[i].m1.fog_density = best_result[0]
                pop[i].m1.size_of_drop = best_result[1]
                pop[i].m2.fog_density = best_result[0]
                pop[i].m2.size_of_drop = best_result[1]
            elif pop[i].m1.mutation_type == "MUT_STORM":
                pop[i].m1.fog_density = best_result[0]
                pop[i].m1.number_drop_rain = best_result[1]
                pop[i].m1.size_of_drop = best_result[2]
                pop[i].m1.wet_foam_density = best_result[3]
                pop[i].m1.wet_ripple_density = best_result[4]
                pop[i].m2.fog_density = best_result[0]
                pop[i].m2.number_drop_rain = best_result[1]
                pop[i].m2.size_of_drop = best_result[2]
                pop[i].m2.wet_foam_density = best_result[3]
                pop[i].m2.wet_ripple_density = best_result[4]
            print("the status is  = " + str(status))
            print("new base result = " + str(best_result) + "the count is " + str(i))
            if status == False:
                break

            base_amount = best_result
        i = i + 1
    problem.hill_climbing_save_data(pop)
