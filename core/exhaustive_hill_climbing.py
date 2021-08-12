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



def get_last_element(lists):
    return lists[len(lists)-1]


def generate_base_solution(type):
    if type == "MUT_FOG_DROP_SIZE":
        return [0, 0]
    elif type == "MUT_RAIN_WHOLE":
        return [1000, 0.02]
    elif type == "MUT_STORM":
        return [0, 1000, 0.01, 0, 0]


def evaluate(solution, pop, problem):
    if pop.m1.mutation_type == "MUT_FOG_DROP_SIZE":
        pop.m1.fog_density = solution[0]
        pop.m1.size_of_drop = solution[1]
        pop.m2.fog_density = solution[0]
        pop.m2.size_of_drop = solution[1]
    elif pop.m1.mutation_type == "MUT_RAIN_WHOLE":
        pop.m1.number_drop_rain = solution[0]
        pop.m1.size_of_drop = solution[1]
        pop.m2.number_drop_rain = solution[0]
        pop.m2.size_of_drop = solution[1]
    if pop.m1.mutation_type == "MUT_STORM":
        pop.m1.fog_density = solution[0]
        pop.m1.number_drop_rain = solution[1]
        pop.m1.size_of_drop = solution[2]
        pop.m1.wet_foam_density = solution[3]
        pop.m1.wet_ripple_density = solution[4]
        pop.m2.fog_density = solution[0]
        pop.m2.number_drop_rain = solution[1]
        pop.m2.size_of_drop = solution[2]
        pop.m2.wet_foam_density = solution[3]
        pop.m2.wet_ripple_density = solution[4]
    result, distances = problem.pre_evaluate_members_hill_climbing(pop)
    return result, distances


def mutate_solution(base, pop, problem , run_id):
    steps = 0
    if pop.m1.mutation_type == "MUT_FOG_DROP_SIZE":
        choice = random.choice(["first", "second"])
        if choice == "first":
            new_amount = [base[0] + problem.config.MUTATION_FOG_PRECISE, base[1]]
            attempt_success, attempt_distance = evaluate(new_amount, pop, problem)
        elif choice == "second":
            new_amount = [base[0], base[1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE]
            attempt_success, attempt_distance = evaluate(new_amount, pop, problem)
        # if attempt_distance <= base_distance:
        print("next generation chosen")
        return choice ,new_amount, attempt_success, attempt_distance

    elif pop.m1.mutation_type == "MUT_RAIN_WHOLE":
        result_base,distance_base = evaluate(base, pop, problem)
        stack = [str(base[0])+","+str(base[1])]
        dictionary_of_steps = {"run id = "+str(run_id) + " , step = " + str(steps): str(stack[0])}
        parent_distances = {stack[0]: distance_base}
        already_done =[stack[0]]
        while True:
            steps = steps + 1
            parent_value = stack[-1]
            base0, base1 = parent_value.split(",")
            base = [float(base0), float(base1)]
            new_amount_1 = [base[0] + problem.config.MUTATION_RAIN_PRECISE, base[1]]
            print("new amount 1 "+str(new_amount_1))
            print("the parent are :"+ str(parent_distances))
            if str(new_amount_1[0])+","+str(new_amount_1[1]) in already_done:
                attempt_distance_first = parent_distances[str(new_amount_1[0])+","+str(new_amount_1[1])]
                dictionary_of_steps.update({
                    "run id = " + str(run_id) + " , step = already done" : str(new_amount_1[0]) + "," + str(
                        new_amount_1[1]) + " ,distance = " + str(attempt_distance_first)})

                attempt_success_first = True
                t1 = True
            else:
                attempt_success_first, attempt_distance_first = evaluate(new_amount_1, pop, problem)
                parent_distances.update({str(new_amount_1[0])+","+str(new_amount_1[1]): attempt_distance_first})
                dictionary_of_steps.update({
                    "run id = " + str(run_id) + " , step = " + str(steps): str(new_amount_1[0]) + "," + str(
                        new_amount_1[1])+" ,distance = " + str(attempt_distance_first)})
                t1 = False
            new_amount_2 = [base[0], base[1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE]
            print("new amount 2 " + str(new_amount_2))
            print("the parent are :" + str(parent_value))
            if str(new_amount_2[0])+","+str(new_amount_2[1]) in  already_done:
                attempt_distance_second  = parent_distances[str(new_amount_2[0])+","+str(new_amount_2[1])]
                dictionary_of_steps.update({
                    "run id = " + str(run_id) + " , step = already done": str(new_amount_2[0]) + "," + str(
                        new_amount_2[1]) + " ,distance = " + str(attempt_distance_second)})
                t2 = True
            else:
                attempt_success_second, attempt_distance_second = evaluate(new_amount_2, pop, problem)
                parent_distances.update({str(new_amount_2[0])+","+str(new_amount_2[1]): attempt_distance_second})
                dictionary_of_steps.update({
                    "run id = " + str(run_id) + " , step = " + str(steps): str(new_amount_2[0]) + "," + str(
                        new_amount_2[1])+" ,distance = " + str(attempt_distance_second)})
                t2 = False
            if t1 and t2:
                stack.pop()
                if len(stack) == 0:
                    return 0, "stop", 0, True, dictionary_of_steps
                    break
            else:
                if attempt_success_first == False or attempt_success_second == False:
                    if attempt_distance_first < attempt_distance_second:
                        return new_amount_1, attempt_success_first, attempt_distance_first, False , dictionary_of_steps
                    else:
                        return new_amount_2, attempt_success_second, attempt_distance_second, False, dictionary_of_steps
                # parent_list[parent_value].append(choice)
                if (attempt_distance_first <= parent_distances[parent_value]) and (str(new_amount_1[0])+","+str(new_amount_1[1]) not in  already_done):
                    stack.append(str(new_amount_1[0]) +","+ str(new_amount_1[1]))
                    already_done.append(str(new_amount_1[0]) +","+ str(new_amount_1[1]))
                    print("stack right now is = "+str(stack))
                elif (attempt_distance_second <= parent_distances[parent_value]) and (str(new_amount_2[0])+","+str(new_amount_2[1]) not in already_done):
                    stack.append(str(new_amount_2[0]) + "," + str(new_amount_2[1]))
                    already_done.append(str(new_amount_2[0]) + "," + str(new_amount_2[1]))
                    print("stack right now is = "+str(stack))
                elif(str(new_amount_1[0])+","+str(new_amount_1[1]) not in already_done) and (str(new_amount_2[0])+","+str(new_amount_2[1]) not in  already_done):
                    stack.pop()
                    if len(stack) == 0:
                        return 0, "stop", 0, True, dictionary_of_steps
                        break




    elif pop.m1.mutation_type == "MUT_STORM":
        choice = random.choice(["first", "second", "third", "forth", "fifth"])
        if choice == "first":
            new_amount = [base[0] + problem.config.MUTATION_FOG_PRECISE, base[1], base[2], base[3], base[4]]
            attempt_success, attempt_distance = evaluate(new_amount, base, pop, problem)
        elif choice == "second":
            new_amount = [base[0], base[1] + problem.config.MUTATION_RAIN_PRECISE, base[2], base[3], base[4]]
            attempt_success, attempt_distance = evaluate(new_amount, base, pop, problem)
        elif choice == "third":
            new_amount = [base[0], base[1], base[2] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE, base[3], base[4]]
            attempt_success, attempt_distance = evaluate(new_amount, base, pop, problem)
        elif choice == "forth":
            new_amount = [base[0], base[1], base[2], base[3] + problem.config.MUTATION_FOAM_PRECISE, base[4]]
            attempt_success, attempt_distance = evaluate(new_amount, base, pop, problem)
        elif choice == "fifth":
            new_amount = [base[0], base[1], base[2], base[3], base[4] + problem.config.MUTATION_RIPPLE_PRECISE]
            attempt_success, attempt_distance = evaluate(new_amount, base, pop, problem)
        # if attempt_distance <= base_distance:
        print("next generation chosen")
        return new_amount, attempt_success, attempt_distance


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
    first_distance = 100

    while i < len(pop):
        base_amount = generate_base_solution(pop[i].m1.mutation_type)
        if pop[i].m1.mutation_type == "MUT_FOG_DROP_SIZE":
            pop[i].m1.fog_density = base_amount[0]
            pop[i].m1.size_of_drop = base_amount[1]
            pop[i].m2.fog_density = base_amount[0]
            pop[i].m2.size_of_drop = base_amount[1]
        elif pop[i].m1.mutation_type == "MUT_RAIN_WHOLE":
            pop[i].m1.number_drop_rain = base_amount[0]
            pop[i].m1.size_of_drop = base_amount[1]
            pop[i].m2.number_drop_rain = base_amount[0]
            pop[i].m2.size_of_drop = base_amount[1]
        elif pop[i].m1.mutation_type == "MUT_STORM":
            pop[i].m1.fog_density = base_amount[0]
            pop[i].m1.number_drop_rain = base_amount[1]
            pop[i].m1.size_of_drop = base_amount[2]
            pop[i].m1.wet_foam_density = base_amount[3]
            pop[i].m1.wet_ripple_density = base_amount[4]
            pop[i].m2.fog_density = base_amount[0]
            pop[i].m2.number_drop_rain = base_amount[1]
            pop[i].m2.size_of_drop = base_amount[2]
            pop[i].m2.wet_foam_density = base_amount[3]
            pop[i].m2.wet_ripple_density = base_amount[4]
        best_result, status, temp, not_found , dictionary = mutate_solution(base_amount, pop[i], problem , i )
        if not_found:
            print("not found............")
            if pop[i].m1.mutation_type == "MUT_RAIN_WHOLE":
                pop[i].m1.number_drop_rain = "not found"
                pop[i].m1.size_of_drop = "not found"
                pop[i].m2.number_drop_rain = "not found"
                pop[i].m2.size_of_drop = "not found"
        else:
            if pop[i].m1.mutation_type == "MUT_FOG_DROP_SIZE":
                pop[i].m1.fog_density = best_result[0]
                pop[i].m1.size_of_drop = best_result[1]
                pop[i].m2.fog_density = best_result[0]
                pop[i].m2.size_of_drop = best_result[1]
            elif pop[i].m1.mutation_type == "MUT_RAIN_WHOLE":
                pop[i].m1.number_drop_rain = best_result[0]
                pop[i].m1.size_of_drop = best_result[1]
                pop[i].m2.number_drop_rain = best_result[0]
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
            print("new base result = " + str(best_result) + "the count is  = " + str(i))
        i = i + 1
    whole_process_time = datetime.now() - start_process_time
    problem.hill_climbing_save_data(pop,"exhaustive" , dictionary, whole_process_time)
