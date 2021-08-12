import random

import numpy as np
from deap import base
from deap import creator
from deap import tools
from datetime import datetime

from core.log_setup import get_logger
from core.problem import Problem
from core.config import Config
from math import exp

log = get_logger(__file__)

stack = []
dictionary_of_steps = {}


def generate_base_solution(type):
    if type == "MUT_FOG_DROP_SIZE":
        return [0, 0.02]
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
        pop.m1.number_drop_rain = int(solution[0])
        pop.m1.size_of_drop = solution[1]
        pop.m2.number_drop_rain = int(solution[0])
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
    distance_array =[]
    i = 0
    count = 0
    while i < problem.config.EVALUATION_AMOUNT:
        result, distances = problem.pre_evaluate_members_hill_climbing(pop)
        if result:
            count = count + 1
        distance_array.append(distances)
        i = i + 1
    if count > (problem.config.EVALUATION_AMOUNT / 2):
        result = True
    else:
        result = False
    print(str(result)+ " ............ " + str(np.mean(distance_array)))
    return result, np.mean(distance_array)


# def fitness_function2(distances, parent_distance, pop):
#     deltas= []
#     vi= []
#     pi = []
#     if pop.m1.mutation_type == "MUT_RAIN_WHOLE":
#         for i  in distances:
#             deltas.append(i - parent_distance)
#         for delta in deltas:
#
#             if delta < 0 :
#                 vi.append(1)
#             else:
#                 vi.append(exp(-delta / 0.001))
#         for v in vi:
#             pi.append(v / (np.sum(vi)))
#
#         while len()
#         p1 = v1 / (v1 + v2)
#         p2 = v2 / (v1 + v2)
#         t = np.max([p1, p2])
#         k = random.uniform(0, 1)
#
#         print("p1 = " + str(p1) + " ,v1 = "+ str(v1)+" ,distance = " + str(first_attempt_distance))
#         print("p2 = " + str(p2) + " ,v2 = " + str(v2) + " ,distance = " + str(second_attempt_distance))
#         print("k = "+str(k) + " ,t = "+str(t))
#
#         if k < t :
#             if p1 == t:
#                 return  first_attempt_distance
#             else:
#                 return second_attempt_distance
#         else:
#             if p1 == t:
#                 return second_attempt_distance
#             else:
#                 return first_attempt_distance
steps = 0


def fitness_function(parent_distance, pop, steps, run_id, first_attempt_distance, first_amount,
                     second_attempt_distance, second_amount, third_amount=None, third_attempt_distance=None,
                     forth_amount=None, forth_attempt_distance=None, fifth_amount=None, fifth_attempt_distance=None):
    if pop.m1.mutation_type == "MUT_RAIN_WHOLE" or pop.m1.mutation_type == "MUT_FOG_DROP_SIZE":
        if first_attempt_distance < 0 or second_attempt_distance < 0:
            if np.min([first_attempt_distance, second_attempt_distance]) == first_attempt_distance:
                dictionary_of_steps.update({"last step winner:" + str(steps) + " run id:" + str(run_id): str(
                    first_amount) + " with distance = " + str(first_attempt_distance)})
                dictionary_of_steps.update({"last step loser" + str(steps) + " run id:" + str(run_id): str(
                    second_amount) + " with distance = " + str(
                    second_attempt_distance)})
            else:
                dictionary_of_steps.update({"last step winner" + str(steps) + " run id:" + str(run_id): str(
                    second_amount) + " with distance = " + str(
                    second_attempt_distance)})
                dictionary_of_steps.update({"last step loser:" + str(steps) + " run id:" + str(run_id): str(
                    first_amount) + " with distance = " + str(first_attempt_distance)})
            return np.min([first_attempt_distance, second_attempt_distance])
        else:
            delta_one = first_attempt_distance - parent_distance
            delta_two = second_attempt_distance - parent_distance
            if delta_one < 0:
                v1 = 1
            else:
                v1 = exp(-delta_one / 0.01)
                if v1 < 0.01:
                    v1 = 0.01
            if delta_two < 0:
                v2 = 1
            else:
                v2 = exp(-delta_two / 0.1)
                if v2 < 0.01:
                    v2 = 0.01
            p1 = v1 / (v1 + v2)
            p2 = v2 / (v1 + v2)
            t = np.max([p1, p2])
            k = random.uniform(0, 1)

            print("p1 = " + str(p1) + " ,v1 = " + str(v1) + " ,distance = " + str(first_attempt_distance))
            print("p2 = " + str(p2) + " ,v2 = " + str(v2) + " ,distance = " + str(second_attempt_distance))
            print("k = " + str(k) + " ,t = " + str(t))

            if k < t:
                if p1 == t:
                    dictionary_of_steps.update({"winnner of step:" + str(steps) + " run id:" + str(run_id): str(
                        first_amount) + ", p1 = " + str(p1) + " ,v1 = " + str(v1) + " ,distance = " + str(
                        first_attempt_distance)+ " ,k = " + str(k) + " ,t = "+str(t)})
                    dictionary_of_steps.update({"loser of step:" + str(steps) + " run id:" + str(run_id): str(
                        second_amount) + ", p2 = " + str(p2) + " ,v2 = " + str(v2) + " ,distance = " + str(
                        second_attempt_distance)+ " ,k = " + str(k) + " ,t = "+str(t)})
                    return first_attempt_distance
                else:
                    dictionary_of_steps.update({"loser of step:" + str(steps) + " run id:" + str(run_id): str(
                        first_amount) + ", p1 = " + str(p1) + " ,v1 = " + str(v1) + " ,distance = " + str(
                        first_attempt_distance)+ " ,k = " + str(k) + " ,t = "+str(t)})
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        second_amount) + ", p2 = " + str(p2) + " ,v2 = " + str(v2) + " ,distance = " + str(
                        second_attempt_distance)+ " ,k = " + str(k) + " ,t = "+str(t)})
                    return second_attempt_distance
            else:
                if p1 == t:
                    dictionary_of_steps.update({"loser of step:" + str(steps) + " run id:" + str(run_id): str(
                        first_amount) + ", p1 = " + str(p1) + " ,v1 = " + str(v1) + " ,distance = " + str(
                        first_attempt_distance)+ " ,k = " + str(k) + " ,t = "+str(t)})
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        second_amount) + ", p2 = " + str(p2) + " ,v2 = " + str(v2) + " ,distance = " + str(
                        second_attempt_distance)+ " ,k = " + str(k) + " ,t = "+str(t)})
                    return second_attempt_distance
                else:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        first_amount) + ", p1 = " + str(p1) + " ,v1 = " + str(v1) + " ,distance = " + str(
                        first_attempt_distance)+ " ,k = " + str(k) + " ,t = "+str(t)})
                    dictionary_of_steps.update({"loser of step:" + str(steps) + " run id:" + str(run_id): str(
                        second_amount) + ", p2 = " + str(p2) + " ,v2 = " + str(v2) + " ,distance = " + str(
                        second_attempt_distance)+ " ,k = " + str(k) + " ,t = "+str(t)})
                    return first_attempt_distance

    elif pop.m1.mutation_type == "MUT_STORM" :
        if first_attempt_distance < 0 or second_attempt_distance < 0 or third_attempt_distance < 0 or forth_attempt_distance < 0 or fifth_attempt_distance < 0:
            minimum = np.min([first_attempt_distance, second_attempt_distance,
                              third_attempt_distance, forth_attempt_distance,
                              fifth_attempt_distance])
            if minimum == first_attempt_distance:
                dictionary_of_steps.update({"last step:" + str(steps) + " run id:" + str(run_id): str(
                    first_amount) + " with distance = " + str(first_attempt_distance)})
            elif minimum == second_attempt_distance:
                dictionary_of_steps.update({"last step" + str(steps) + " run id:" + str(run_id): str(
                    second_amount) + " with distance = " + str(
                    second_attempt_distance)})
            elif minimum == third_attempt_distance:
                dictionary_of_steps.update({"last step" + str(steps) + " run id:" + str(run_id): str(
                    third_amount) + " with distance = " + str(
                    third_attempt_distance)})
            elif minimum == forth_attempt_distance:
                dictionary_of_steps.update({"last step" + str(steps) + " run id:" + str(run_id): str(
                    forth_amount) + " with distance = " + str(
                    forth_attempt_distance)})
            elif minimum == fifth_attempt_distance:
                dictionary_of_steps.update({"last step" + str(steps) + " run id:" + str(run_id): str(
                    fifth_amount) + " with distance = " + str(
                    fifth_attempt_distance)})
            return minimum
        else:
            delta_one = first_attempt_distance - parent_distance
            delta_two = second_attempt_distance - parent_distance
            delta_three = third_attempt_distance - parent_distance
            delta_four = forth_attempt_distance - parent_distance
            delta_five = fifth_attempt_distance - parent_distance
            if delta_one < 0:
                v1 = 1
            else:
                v1 = exp(-delta_one / 0.01)
            if delta_two < 0:
                v2 = 1
            else:
                v2 = exp(-delta_two / 0.1)
            if delta_two < 0:
                v3 = 1
            else:
                v3 = exp(-delta_three / 0.1)
            if delta_two < 0:
                v4 = 1
            else:
                v4 = exp(-delta_four/ 0.1)
            if delta_two < 0:
                v5 = 1
            else:
                v5 = exp(-delta_five / 0.1)
            p1 = v1 / (v1 + v2 + v3 + v4 + v5)
            p2 = v2 / (v1 + v2 + v3 + v4 + v5)
            p3 = v3 / (v1 + v2 + v3 + v4 + v5)
            p4 = v4 / (v1 + v2 + v3 + v4 + v5)
            p5 = v5 / (v1 + v2 + v3 + v4 + v5)
            all_p = [p1, p2, p3, p4, p5]
            t1 = np.max(all_p)
            print(t1)
            print(all_p)
            all_p.remove(t1)
            t2 = np.max(all_p)
            all_p.remove(t2)
            t3 = np.max(all_p)
            all_p.remove(t3)
            t4 = np.max(all_p)
            all_p.remove(t4)
            t5 = all_p[0]

            th1 = t1
            th2 = t1 + t2
            th3 = t1 + t2 + t3
            th4 = t1 + t2 + t3 + t4

            k = random.uniform(0, 1)

            print("p1 = " + str(p1) + " ,v1 = " + str(v1) + " ,distance = " + str(first_attempt_distance))
            print("p2 = " + str(p2) + " ,v2 = " + str(v2) + " ,distance = " + str(second_attempt_distance))
            print("k = " + str(k) + " , th1 = " + str(th1) + " , th2 = " + str(th2) +
                  " , th3 = " + str(th3) + " , th4 = " + str(th4))
            if 0 < k <= th1:
                if p1 == t1:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        first_amount) + ", p1 = " + str(p1) + " ,v1 = " + str(v1) + " ,distance = " + str(
                        first_attempt_distance)})
                    return first_attempt_distance
                elif p2 == t1:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        second_amount) + ", p2 = " + str(p2) + " ,v1 = " + str(v2) + " ,distance = " + str(
                        second_attempt_distance)})
                    return second_attempt_distance
                elif p3 == t1:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        third_amount) + ", p3 = " + str(p3) + " ,v3 = " + str(v3) + " ,distance = " + str(
                        third_attempt_distance)})
                    return third_attempt_distance
                elif p4 == t1:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        forth_amount) + ", p4 = " + str(p4) + " ,v4 = " + str(v4) + " ,distance = " + str(
                        forth_attempt_distance)})
                    return forth_attempt_distance
                elif p5 == t1:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        fifth_amount) + ", p5 = " + str(p5) + " ,v5 = " + str(v5) + " ,distance = " + str(
                        fifth_attempt_distance)})
                    return fifth_attempt_distance
            elif th1 < k < th2:
                if p1 == t2:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        first_amount) + ", p1 = " + str(p1) + " ,v1 = " + str(v1) + " ,distance = " + str(
                        first_attempt_distance)})
                    return first_attempt_distance
                elif p2 == t2:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        second_amount) + ", p2 = " + str(p2) + " ,v1 = " + str(v2) + " ,distance = " + str(
                        second_attempt_distance)})
                    return second_attempt_distance
                elif p3 == t2:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        third_amount) + ", p3 = " + str(p3) + " ,v3 = " + str(v3) + " ,distance = " + str(
                        third_attempt_distance)})
                    return third_attempt_distance
                elif p4 == t2:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        forth_amount) + ", p4 = " + str(p4) + " ,v4 = " + str(v4) + " ,distance = " + str(
                        forth_attempt_distance)})
                    return forth_attempt_distance
                elif p5 == t2:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        fifth_amount) + ", p5 = " + str(p5) + " ,v5 = " + str(v5) + " ,distance = " + str(
                        fifth_attempt_distance)})
                    return fifth_attempt_distance
            elif th2 < k < th3:
                if p1 == t3:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        first_amount) + ", p1 = " + str(p1) + " ,v1 = " + str(v1) + " ,distance = " + str(
                        first_attempt_distance)})
                    return first_attempt_distance
                elif p2 == t3:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        second_amount) + ", p2 = " + str(p2) + " ,v1 = " + str(v2) + " ,distance = " + str(
                        second_attempt_distance)})
                    return second_attempt_distance
                elif p3 == t3:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        third_amount) + ", p3 = " + str(p3) + " ,v3 = " + str(v3) + " ,distance = " + str(
                        third_attempt_distance)})
                    return third_attempt_distance
                elif p4 == t2:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        forth_amount) + ", p4 = " + str(p4) + " ,v4 = " + str(v4) + " ,distance = " + str(
                        forth_attempt_distance)})
                    return forth_attempt_distance
                elif p5 == t3:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        fifth_amount) + ", p5 = " + str(p5) + " ,v5 = " + str(v5) + " ,distance = " + str(
                        fifth_attempt_distance)})
                    return fifth_attempt_distance
            elif th3 < k < th4:
                if p1 == t4:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        first_amount) + ", p1 = " + str(p1) + " ,v1 = " + str(v1) + " ,distance = " + str(
                        first_attempt_distance)})
                    return first_attempt_distance
                elif p2 == t4:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        second_amount) + ", p2 = " + str(p2) + " ,v1 = " + str(v2) + " ,distance = " + str(
                        second_attempt_distance)})
                    return second_attempt_distance
                elif p3 == t4:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        third_amount) + ", p3 = " + str(p3) + " ,v3 = " + str(v3) + " ,distance = " + str(
                        third_attempt_distance)})
                    return third_attempt_distance
                elif p4 == t4:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        forth_amount) + ", p4 = " + str(p4) + " ,v4 = " + str(v4) + " ,distance = " + str(
                        forth_attempt_distance)})
                    return forth_attempt_distance
                elif p5 == t4:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        fifth_amount) + ", p5 = " + str(p5) + " ,v5 = " + str(v5) + " ,distance = " + str(
                        fifth_attempt_distance)})
                    return fifth_attempt_distance
            elif th4 < k < 1:
                if p1 == t5:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        first_amount) + ", p1 = " + str(p1) + " ,v1 = " + str(v1) + " ,distance = " + str(
                        first_attempt_distance)})
                    return first_attempt_distance
                elif p2 == t5:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        second_amount) + ", p2 = " + str(p2) + " ,v1 = " + str(v2) + " ,distance = " + str(
                        second_attempt_distance)})
                    return second_attempt_distance
                elif p3 == t5:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        third_amount) + ", p3 = " + str(p3) + " ,v3 = " + str(v3) + " ,distance = " + str(
                        third_attempt_distance)})
                    return third_attempt_distance
                elif p4 == t5:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        forth_amount) + ", p4 = " + str(p4) + " ,v4 = " + str(v4) + " ,distance = " + str(
                        forth_attempt_distance)})
                    return forth_attempt_distance
                elif p5 == t5:
                    dictionary_of_steps.update({"winner of step:" + str(steps) + " run id:" + str(run_id): str(
                        fifth_amount) + ", p5 = " + str(p5) + " ,v5 = " + str(v5) + " ,distance = " + str(
                        fifth_attempt_distance)})
                    return fifth_attempt_distance


def mutate_solution(base, pop, problem, parent_distance, steps, run_id):
    if pop.m1.mutation_type == "MUT_FOG_DROP_SIZE":
        first_attempt_success, first_attempt_distance = evaluate(
            [base[0] + problem.config.MUTATION_FOG_PRECISE, base[1]], pop,
            problem)
        second_attempt_success, second_attempt_distance = evaluate(
            [base[0], base[1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE],
            pop, problem)

        chosen_distance = fitness_function(parent_distance, pop, steps, run_id, first_attempt_distance,
                                           [base[0] + problem.config.MUTATION_FOG_PRECISE, base[1]],
                                           second_attempt_distance,
                                           [base[0], base[1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE])
        if first_attempt_distance == chosen_distance:

            print("[" + str(base[0] + problem.config.MUTATION_FOG_PRECISE) + "," + str(
                base[1]) + "]" + " = " + str(first_attempt_distance))
            print("[" + str(base[0]) + "," + str(
                base[1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE) + "]" + "=" + str(
                second_attempt_distance))

            return [base[0] + problem.config.MUTATION_FOG_PRECISE,
                    base[1]], first_attempt_success, first_attempt_distance
        else:

            print("[" + str(base[0]) + "," + str(
                base[1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE) + "]" + " = " + str(
                second_attempt_distance))
            print("[" + str(base[0] + problem.config.MUTATION_FOG_PRECISE) + "," + str(
                base[1]) + "]" + " = " + str(
                first_attempt_distance))
            return [base[0], base[
                1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE], second_attempt_success, second_attempt_distance
    elif pop.m1.mutation_type == "MUT_RAIN_WHOLE":
        first_attempt_success, first_attempt_distance = evaluate(
            [base[0] + problem.config.MUTATION_RAIN_PRECISE, base[1]], pop,
            problem)
        second_attempt_success, second_attempt_distance = evaluate(
            [base[0], base[1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE],
            pop, problem)

        chosen_distance = fitness_function(parent_distance, pop, steps, run_id, first_attempt_distance,
                                           [base[0] + problem.config.MUTATION_RAIN_PRECISE, base[1]],
                                           second_attempt_distance,
                                           [base[0], base[1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE])
        if first_attempt_distance == chosen_distance:

            print("[" + str(base[0] + problem.config.MUTATION_RAIN_PRECISE) + "," + str(
                base[1]) + "]" + " = " + str(first_attempt_distance))
            print("[" + str(base[0]) + "," + str(
                base[1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE) + "]" + "=" + str(
                second_attempt_distance))

            return [base[0] + problem.config.MUTATION_RAIN_PRECISE,
                    base[1]], first_attempt_success, first_attempt_distance
        else:

            print("[" + str(base[0]) + "," + str(
                base[1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE) + "]" + " = " + str(
                second_attempt_distance))
            print("[" + str(base[0] + problem.config.MUTATION_RAIN_PRECISE) + "," + str(
                base[1]) + "]" + " = " + str(
                first_attempt_distance))
            return [base[0], base[
                1] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE], second_attempt_success, second_attempt_distance

    elif pop.m1.mutation_type == "MUT_STORM":
        first_attempt_success, first_attempt_distance = evaluate(
            [base[0] + problem.config.MUTATION_FOG_PRECISE, base[1], base[2], base[3], base[4]], pop, problem)
        second_attempt_success, second_attempt_distance = evaluate(
            [base[0], base[1] + problem.config.MUTATION_RAIN_PRECISE,
             base[2], base[3], base[4]], pop, problem)
        third_attempt_success, third_attempt_distance = evaluate([base[0], base[1], base[2] +
                                                                  problem.config.MUTATION_SIZE_OF_DROP_PRECISE,
                                                                  base[3], base[4]], pop, problem)
        forth_attempt_success, forth_attempt_distance = evaluate([base[0], base[1], base[2],
                                                                  base[3] + problem.config.MUTATION_FOAM_PRECISE,
                                                                  base[4]], pop, problem)
        fifth_attempt_success, fifth_attempt_distance = evaluate([base[0], base[1], base[2], base[3],
                                                                  base[4] + problem.config.MUTATION_RIPPLE_PRECISE],
                                                                 pop, problem)
        chosen_distance = fitness_function(parent_distance, pop, steps, run_id, first_attempt_distance,
                                           [base[0] + problem.config.MUTATION_FOG_PRECISE, base[1], base[2], base[3],
                                            base[4]], second_attempt_distance,
                                           [base[0], base[1] + problem.config.MUTATION_RAIN_PRECISE, base[2], base[3],
                                            base[4]], [base[0], base[1],
                                                       base[2] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE, base[3],
                                                       base[4]], third_attempt_distance,
                                           [base[0], base[1], base[2], base[3] + problem.config.MUTATION_FOAM_PRECISE,
                                            base[4]], forth_attempt_distance, [base[0], base[1], base[2], base[3],
                                                                               base[
                                                                                   4] + problem.config.MUTATION_RIPPLE_PRECISE],
                                           fifth_attempt_distance)

        if chosen_distance == first_attempt_distance:
            print("first")
            return [base[0] + problem.config.MUTATION_FOG_PRECISE, base[1], base[2], base[3],
                    base[4]], first_attempt_success, first_attempt_distance
        elif chosen_distance == second_attempt_distance:
            print("second")
            return [base[0], base[1] + problem.config.MUTATION_RAIN_PRECISE, base[2], base[3],
                    base[4]], second_attempt_success, second_attempt_distance
        elif chosen_distance == third_attempt_distance:
            print("third")
            return [base[0], base[1], base[2] + problem.config.MUTATION_SIZE_OF_DROP_PRECISE, base[3],
                    base[4]], third_attempt_success, third_attempt_distance
        elif chosen_distance == forth_attempt_distance:
            print("forth")
            return [base[0], base[1], base[2], base[3] + problem.config.MUTATION_FOAM_PRECISE,
                    base[4]], forth_attempt_success, forth_attempt_distance
        elif chosen_distance == fifth_attempt_distance:
            print("fifth")
            return [base[0], base[1], base[2], base[3],
                    base[4] + problem.config.MUTATION_RIPPLE_PRECISE], fifth_attempt_success, fifth_attempt_distance


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

    while i < len(pop):
        steps = 0
        base_amount = generate_base_solution(pop[i].m1.mutation_type)
        status, base_distance = evaluate(base_amount, pop[i], problem)

        print("base distance = " + str(base_distance))
        dictionary_of_steps.update({"first step:" + str(steps) + " run id:" + str(i): str(
            base_amount) + " with distance = " + str(base_distance)})
        while True:
            steps = steps + 1
            best_result, status, base_distance = mutate_solution(base_amount, pop[i], problem, base_distance, steps, i)
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
            print("new base result = " + str(best_result) + "the number population is  = " + str(i))
            if status == False:
                break

            base_amount = best_result
        i = i + 1
    # //TODO : change to only pop
    whole_process_time = datetime.now() - start_process_time
    problem.hill_climbing_save_data(pop, "simulated_annealing", dictionary_of_steps, whole_process_time)
