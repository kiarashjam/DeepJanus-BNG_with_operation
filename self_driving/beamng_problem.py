import itertools
import json
import math
import random
from typing import List

from deap import creator

from core.archive import Archive
from core.folders import folders
from core.log_setup import get_logger
from core.member import Member
from core.metrics import get_radius_seed, get_diameter
from core.misc import delete_folder_recursively
from core.problem import Problem
from core.seed_pool_access_strategy import SeedPoolAccessStrategy
from core.seed_pool_impl import SeedPoolFolder, SeedPoolRandom
from self_driving.beamng_config import BeamNGConfig
from self_driving.beamng_evaluator import BeamNGEvaluator
from self_driving.beamng_individual import BeamNGIndividual
from self_driving.beamng_individual_set_store import BeamNGIndividualSetStore
from self_driving.beamng_member import BeamNGMember
from self_driving.road_generator import RoadGenerator
from self_driving.initial_population_generator import initial_pool_generator, initial_population_generator

log = get_logger(__file__)
import numpy as np


class BeamNGProblem(Problem):
    def __init__(self, config: BeamNGConfig, archive: Archive):
        self.config: BeamNGConfig = config
        self._evaluator: BeamNGEvaluator = None
        super().__init__(config, archive)
        if self.config.generator_name == self.config.GEN_RANDOM:
            seed_pool = SeedPoolRandom(self, config.POPSIZE)
        elif self.config.generator_name == self.config.GEN_DIVERSITY:
            path = initial_pool_generator(self.config, self)
            initial_population_generator(path, self.config, self)
            seed_pool = SeedPoolFolder(self, config, config.initial_population_folder)
        else:
            seed_pool = SeedPoolFolder(self, config, config.seed_folder)
        self._seed_pool_strategy = SeedPoolAccessStrategy(seed_pool)
        self.experiment_path = folders.experiments.joinpath(self.config.experiment_name)
        # delete_folder_recursively(self.experiment_path)

    def deap_generate_individual(self):
        seed = self._seed_pool_strategy.get_seed()
        road1 = seed.clone()
        road2 = seed.clone().mutate()
        road1.config = self.config
        road2.config = self.config
        individual: BeamNGIndividual = creator.Individual(road1, road2, self.config, self.archive)
        individual.seed = seed
        log.info(f'generated {individual}')

        return individual

    def deap_generate_individual_binary_search(self):
        seed = self._seed_pool_strategy.get_seed()
        road1 = seed.clone().mutate_binary_search(0)
        road2 = seed.clone().mutate_binary_search(1)
        road1.config = self.config
        road2.config = self.config
        individual: BeamNGIndividual = creator.Individual(road1, road2, self.config, self.archive)
        individual.seed = seed
        log.info(f'generated {individual}')

        return individual

    # def deap_generate_individual_binary_search_two(self, amount, another_amount):
    #     seed = self._seed_pool_strategy.get_seed()
    #     road1 = seed.clone().mutate_binary_search(amount)
    #     road2 = seed.clone().mutate_binary_search(another_amount)
    #     road1.config = self.config
    #     road2.config = self.config
    #     individual: BeamNGIndividual = creator.Individual(road1, road2, self.config, self.archive)
    #     individual.seed = seed
    #     log.info(f'generated {individual}')
    #
    #     return individual

    def deap_evaluate_individual(self, individual: BeamNGIndividual):
        return individual.evaluate()

    def on_iteration(self, idx, pop: List[BeamNGIndividual], logbook, time_records):
        self.archive.process_population(pop)

        self.experiment_path.mkdir(parents=True, exist_ok=True)
        self.experiment_path.joinpath('config.json').write_text(json.dumps(self.config.__dict__))

        gen_path = self.experiment_path.joinpath(f'gen{idx}')
        gen_path.mkdir(parents=True, exist_ok=True)

        # Generate final report at the end of the last iteration.
        # if idx + 1 == self.config.NUM_GENERATIONS:
        if (len(self.archive) > 0):
            fog, rain, size_of_drop, foam, ripple, illumination, bump, position, road_shape, radius, type_operation, fog_avg, rain_avg, size_of_drop_avg, foam_avg, ripple_avg, bump_avg, obstacle_avg, illumination_avg, road_shape_avg, fog_amount, rain_amount, size_of_drop_amount, foam_amount, ripple_amount, illumination_amount  = get_radius_seed(
                self.archive)
            raduis_array = []
            active_array=[]
            if fog != 0:
                raduis_array.append(fog)
                active_array.append("fog")
            if rain != 0:
                raduis_array.append(rain)
                active_array.append("rain")
            if size_of_drop != 0:
                raduis_array.append(size_of_drop)
                active_array.append("size_of_drop")
            if foam != 0:
                raduis_array.append(foam)
                active_array.append("foam")
            if ripple != 0:
                raduis_array.append(ripple)
                active_array.append("ripple")
            if illumination != 0:
                raduis_array.append(illumination)
                active_array.append("illumination")
            if bump != 0:
                raduis_array.append(bump)
                active_array.append("bump")
            if position != 0:
                raduis_array.append(position)
                active_array.append("position")
            if road_shape != 0:
                raduis_array.append(road_shape)
                active_array.append("road_shape")

            report = {
                'archive_len': len(self.archive),
                'initial population time': str(time_records[0]),
                'evaluation process time': str(time_records[1]),
                'distance calculation time': str(time_records[2]),
                'whole generation time': str(time_records[3]),
                'operation type': type_operation,
                'fog average amount': fog_amount,
                'rain average amount': rain_amount,
                'size of drop average amount': size_of_drop_amount,
                'foam average amount': foam_amount,
                'ripple average amount': ripple_amount,
                'bump average amount': bump_avg,
                'position obstacle average amount': obstacle_avg,
                'illumination average amount': illumination_amount,
                'road shape average': road_shape_avg,
                'normalize_distance_fog': fog,
                'normalize_distance_rain': rain,
                'normalize_distance_size_of_drop': size_of_drop,
                'normalize_distance_foam': foam,
                'normalize_distance_ripple': ripple,
                'normalize_distance_bump': bump,
                'normalize_distance_obstacle': position,
                'normalize_distance_illumination': illumination,
                'normalize_distance_road_shape': road_shape,
                'active operators': active_array,
                'radius': raduis_array,
                'diameter_out': get_diameter([ind.members_by_sign()[0] for ind in self.archive]),
                'diameter_in': get_diameter([ind.members_by_sign()[1] for ind in self.archive])
            }
            gen_path.joinpath(f'report{idx}.json').write_text(json.dumps(report))

        BeamNGIndividualSetStore(gen_path.joinpath('population')).save(pop)
        BeamNGIndividualSetStore(gen_path.joinpath('archive')).save(self.archive)
    def hill_climbing_save_data(self, pop: List[BeamNGIndividual], type, dictionaries_of_steps, process_time):

        self.experiment_path.mkdir(parents=True, exist_ok=True)
        self.experiment_path.joinpath('config.json').write_text(json.dumps(self.config.__dict__))

        gen_path = self.experiment_path.joinpath('individuals')
        gen_path.mkdir(parents=True, exist_ok=True)
        dict = {}
        i = 0
        for ind in pop:
            if ind.m1.mutation_type == "MUT_FOG_DROP_SIZE":
                dict.update({i:{"fog":ind.m2.fog_density,"drop_size":ind.m2.size_of_drop}})
                i = i + 1
            elif ind.m1.mutation_type == "MUT_RAIN_WHOLE":
                dict.update({i:{"number of drop":ind.m1.number_drop_rain,"drop_size":ind.m1.size_of_drop}})
                i = i + 1
            elif ind.m1.mutation_type == "MUT_STORM":
                dict.update({i:{"fog":ind.m2.fog_density, "number of drop":ind.m2.number_drop_rain,
                                "drop_size":ind.m2.size_of_drop, "foam density":ind.m2.wet_foam_density,
                                "ripple density":ind.m2.wet_ripple_density}})
                i = i + 1
        print(dict)
        report = {"frontiers": dict,
                  "time": str(process_time)}

        if type == "random":
            gen_path.joinpath('random_steps_report.json').write_text(json.dumps(dictionaries_of_steps))
            gen_path.joinpath('random_report.json').write_text(json.dumps(report))
        elif type == "simulated_annealing":
            gen_path.joinpath('simulated_annealing__steps_report.json').write_text(json.dumps(dictionaries_of_steps))
            gen_path.joinpath('simulated_annealing_report.json').write_text(json.dumps(report))
        elif type == "stochastic":
            gen_path.joinpath('stochastic_report.json').write_text(json.dumps(report))
            gen_path.joinpath('stochastic_steps_report.json').write_text(json.dumps(dictionaries_of_steps))
        elif type == "exhaustive":
            gen_path.joinpath('exhaustive_report.json').write_text(json.dumps(report))
            gen_path.joinpath('exhaustive_steps_report.json').write_text(json.dumps(dictionaries_of_steps))
        BeamNGIndividualSetStore(gen_path.joinpath('population_binary_search')).save(pop)

    def binary_save_data(self, pop: List[BeamNGIndividual], times_of_process):

        self.experiment_path.mkdir(parents=True, exist_ok=True)
        self.experiment_path.joinpath('config.json').write_text(json.dumps(self.config.__dict__))

        gen_path = self.experiment_path.joinpath('individuals')
        gen_path.mkdir(parents=True, exist_ok=True)
        successful_array = []
        failure_array = []
        for ind in pop:
            if ind.m1.mutation_type == "MUT_FOG":
                successful_array.append(ind.m1.fog_density)
                failure_array.append(ind.m2.fog_density)
            elif ind.m1.mutation_type == "MUT_WET_FOAM":
                successful_array.append(ind.m1.wet_foam_density)
                failure_array.append(ind.m2.wet_foam_density)
            elif ind.m1.mutation_type == "MUT_WET_RIPPLE":
                successful_array.append(ind.m1.wet_ripple_density)
                failure_array.append(ind.m2.wet_ripple_density)
            elif ind.m1.mutation_type == "MUT_ILLUMINATION":
                successful_array.append(ind.m1.illumination)
                failure_array.append(ind.m2.illumination)
            elif ind.m1.mutation_type == "MUT_DROP_SIZE":
                successful_array.append(ind.m1.size_of_drop)
                failure_array.append(ind.m2.size_of_drop)

        report = {"amount for successful": successful_array,
                  "amount for failure": failure_array,
                  "evaluation_population_time": str(times_of_process["evaluation_population_time"]),
                  "whole_process_time": str(times_of_process["whole_process_time"]),
                  "initial_population_time": str(times_of_process["initial_population_time"]),
                  "every_evaluation_time": times_of_process["every_evaluation_time"],
                  }
        gen_path.joinpath('report.json').write_text(json.dumps(report))
        BeamNGIndividualSetStore(gen_path.joinpath('population_binary_search')).save(pop)

    def failure_finder_save_data(self, dicts):
        self.experiment_path.mkdir(parents=True, exist_ok=True)
        self.experiment_path.joinpath('config.json').write_text(json.dumps(self.config.__dict__))
        gen_path = self.experiment_path.joinpath('reports')
        gen_path.mkdir(parents=True, exist_ok=True)
        all_amount = []
        all_status = []
        for whole_data in dicts:
            amounts = []
            statuses = []
            for status in whole_data.values():
                if status:
                    statuses.append("success")
                elif not status:
                    statuses.append("failure")
            for amount in whole_data.keys():
                amounts.append(amount)
            all_status.append(statuses)
            all_amount.append(amounts)
        report = {
            "amount": all_amount,
            "status": all_status,
        }
        gen_path.joinpath('report.json').write_text(json.dumps(report))

    def generate_random_member(self) -> Member:

        result = RoadGenerator(num_control_nodes=self.config.num_control_nodes,
                               seg_length=self.config.SEG_LENGTH).generate()
        result.config = self.config
        result.problem = self
        result.mutation_type = self.config.MUTATION_TYPE
        result.surrounding_type = self.config.SURROUNDING

        pointes = result.control_nodes
        n = len(pointes)
        i = 0
        array_angles = []
        while i < n - 3:
            a = np.array([pointes[i][0], pointes[i][1]])
            b = np.array([pointes[i + 1][0], pointes[i + 1][1]])
            c = np.array([pointes[i + 2][0], pointes[i + 2][1]])

            ba = a - b
            bc = c - b

            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.arccos(cosine_angle)

            array_angles.append(180 - np.degrees(angle))
            i = i + 1
        result.angles = array_angles
        result.highest_angles = max(array_angles)
        if self.config.MUTATION_TYPE == 'MUT_FOG' or self.config.MUTATION_TYPE == 'MUT_FOG_WITH_CONTROL_POINTS':
            if result.config.SEARCH_ALGORITHM == "BINARY_SEARCH" or result.config.SEARCH_ALGORITHM == "FAILURE_FINDER":
                result.fog_density = 0
            elif result.config.SEARCH_ALGORITHM == "NSGA2":
                result.fog_density = random.uniform(self.config.FOG_DENSITY_threshold_for_generating_seed_min,
                                                    self.config.FOG_DENSITY_threshold_for_generating_seed_max)
            result.wet_foam_density = 0
            result.number_drop_rain = 0
            result.size_of_drop = 0
            result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_FOG_DROP_SIZE':
            if result.config.SEARCH_ALGORITHM == "BINARY_SEARCH" or result.config.SEARCH_ALGORITHM == "FAILURE_FINDER" or result.config.SEARCH_ALGORITHM == "EXHAUSTIVE_HILL_CLIMBING":
                result.fog_density = 0
            elif result.config.SEARCH_ALGORITHM == "NSGA2":
                result.fog_density = random.uniform(self.config.FOG_DENSITY_threshold_for_generating_seed_min,
                                                    self.config.FOG_DENSITY_threshold_for_generating_seed_max)
            result.wet_foam_density = 0
            result.number_drop_rain = 0
            result.size_of_drop = 0
            result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_FAILURE_FINDER':
            result.fog_density = 0
            result.wet_foam_density = 0
            result.number_drop_rain = 0
            result.size_of_drop = 0
            result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
            result.failure_finder_amount = 0
            result.failure_finder_type = self.config.FAILURE_FINDER_TYPE
            result.failure_finder_class = self.config.FAILURE_FINDER_CLASS
        elif self.config.MUTATION_TYPE == 'MUT_RAIN':
            result.fog_density = 0
            result.wet_foam_density = 0
            if result.config.SEARCH_ALGORITHM == "BINARY_SEARCH" or \
                    result.config.SEARCH_ALGORITHM == "FAILURE_FINDER":
                result.number_drop_rain = 0

            elif result.config.SEARCH_ALGORITHM == "NSGA2":
                result.number_drop_rain = random.randint(self.config.NUMBER_OF_DROP_RAIN_threshold_min,
                                                         self.config.NUMBER_OF_DROP_RAIN_threshold_max)
            result.size_of_drop = 0
            result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_RAIN_WHOLE' or self.config.MUTATION_TYPE == 'MUT_RAIN_WITH_CONTROL_POINTS':
            result.fog_density = 0
            if result.config.SEARCH_ALGORITHM == "NSGA2":
                result.number_drop_rain = random.randint(self.config.NUMBER_OF_DROP_RAIN_threshold_min,
                                                         self.config.NUMBER_OF_DROP_RAIN_threshold_max)
                result.size_of_drop = random.uniform(self.config.SIZE_OF_DROP_threshold_min,
                                                 self.config.SIZE_OF_DROP_threshold_max)
            else :
                result.number_drop_rain = 1000
                result.size_of_drop = 0.02
            result.wet_foam_density = 0
            result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_STORM':
            if result.config.SEARCH_ALGORITHM == "NSGA2":
                result.fog_density = random.uniform(self.config.FOG_DENSITY_threshold_for_generating_seed_min,
                                                    self.config.FOG_DENSITY_threshold_for_generating_seed_max)
                result.number_drop_rain = random.randint(self.config.NUMBER_OF_DROP_RAIN_threshold_min,
                                                         self.config.NUMBER_OF_DROP_RAIN_threshold_max)
                result.size_of_drop = random.randint(self.config.SIZE_OF_DROP_threshold_min,
                                                     self.config.SIZE_OF_DROP_threshold_max)
                result.wet_foam_density = random.randint(self.config.WET_FOAM_threshold_min,
                                                         self.config.WET_FOAM_threshold_max)
                result.wet_ripple_density = random.randint(self.config.WET_RIPPLE_threshold_min,
                                                           self.config.WET_RIPPLE_threshold_max)
            else:
                result.fog_density = 0
                result.number_drop_rain = 1000
                result.size_of_drop = 0.01
                result.wet_foam_density = 0
                result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_WHOLE_WET_FLOOR':
            result.fog_density = 0
            result.number_drop_rain = 0
            result.size_of_drop = 0
            result.wet_foam_density = random.randint(self.config.WET_FOAM_threshold_min,
                                                     self.config.WET_FOAM_threshold_max)
            result.wet_ripple_density = random.randint(self.config.WET_RIPPLE_threshold_min,
                                                       self.config.WET_RIPPLE_threshold_max)
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_DROP_SIZE':
            result.fog_density = 0
            result.wet_foam_density = 0
            if result.config.SEARCH_ALGORITHM == "BINARY_SEARCH" or result.config.SEARCH_ALGORITHM == "FAILURE_FINDER":
                result.size_of_drop = 0
            elif result.config.SEARCH_ALGORITHM == "NSGA2":
                result.size_of_drop = random.randint(self.config.SIZE_OF_DROP_threshold_min,
                                                     self.config.SIZE_OF_DROP_threshold_max)
            result.number_drop_rain = 10000
            result.size_of_drop = 0
            result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_WET_FOAM':
            result.fog_density = 0
            if result.config.SEARCH_ALGORITHM == "BINARY_SEARCH" or result.config.SEARCH_ALGORITHM == "FAILURE_FINDER":
                result.wet_foam_density = 0
            elif result.config.SEARCH_ALGORITHM == "NSGA2":
                result.wet_foam_density = random.randint(self.config.WET_FOAM_threshold_min,
                                                         self.config.WET_FOAM_threshold_max)
            result.number_drop_rain = 0
            result.size_of_drop = 0
            result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_WET_RIPPLE':
            result.fog_density = 0
            result.wet_foam_density = 0
            result.number_drop_rain = 0
            result.size_of_drop = 0
            if result.config.SEARCH_ALGORITHM == "BINARY_SEARCH" or result.config.SEARCH_ALGORITHM == "FAILURE_FINDER":
                result.wet_ripple_density = 0
            elif result.config.SEARCH_ALGORITHM == "NSGA2":
                result.wet_ripple_density = random.randint(self.config.WET_RIPPLE_threshold_min,
                                                           self.config.WET_RIPPLE_threshold_max)
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_ILLUMINATION' or self.config.MUTATION_TYPE == "MUT_ILLUMINATION_WITH_CONTROL_POINTS":
            result.fog_density = 0
            result.wet_foam_density = 0
            result.number_drop_rain = 0
            result.size_of_drop = 0
            result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            if result.config.SEARCH_ALGORITHM == "BINARY_SEARCH" or result.config.SEARCH_ALGORITHM == "FAILURE_FINDER":
                result.illumination = 0
            elif result.config.SEARCH_ALGORITHM == "NSGA2":
                result.illumination = random.uniform(self.config.ILLUMINATION_AMOUNT_threshold_min,
                                                     self.config.ILLUMINATION_AMOUNT_threshold_max)
        elif self.config.MUTATION_TYPE == 'MUT_OBSTACLE':
            while True:
                new_amount = (
                    random.randint(-1000, 1000), random.randint(-1000, 1000), -28)
                if self.positin_valid(result, new_amount):
                    result.position_of_obstacle = new_amount
                    break
            result.fog_density = 0
            result.wet_foam_density = 0
            result.number_drop_rain = 0
            result.size_of_drop = 0
            result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_BUMP':
            result.fog_density = 0
            result.wet_foam_density = 0
            result.number_drop_rain = 0
            result.size_of_drop = 0
            result.wet_ripple_density = 0
            result.number_of_bump = random.randint(self.config.NUMBER_BUMP_threshold_min,
                                                   self.config.NUMBER_BUMP_threshold_max)
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
        return result

    def deap_individual_class(self):
        return BeamNGIndividual

    def member_class(self):
        return BeamNGMember

    def positin_valid(self, result, amount):
        for node in result.control_nodes:
            distance = math.sqrt(((node[0] - amount[0]) ** 2) + ((node[1] - amount[1]) ** 2))
            if distance < 5:
                return True
        return False

    def reseed(self, pop, offspring):
        if len(self.archive) > 0:
            stop = self.config.RESEED_UPPER_BOUND + 1
            seed_range = min(random.randrange(0, stop), len(pop))
            # log.info(f'reseed{seed_range}')
            # for i in range(0, seed_range):
            #    ind1 = self.deap_generate_individual()
            #    rem_idx = -(i + 1)
            #    log.info(f'reseed rem {pop[rem_idx]}')
            #    pop[rem_idx] = ind1
            archived_seeds = [i.seed for i in self.archive]
            for i in range(len(pop)):
                if pop[i].seed in archived_seeds:
                    ind1 = self.deap_generate_individual()
                    log.info(f'reseed rem {pop[i]}')
                    pop[i] = ind1

    def _get_evaluator(self):
        if self._evaluator:
            return self._evaluator
        ev_name = self.config.beamng_evaluator
        if ev_name == BeamNGConfig.EVALUATOR_FAKE:
            from self_driving.beamng_evaluator_fake import BeamNGFakeEvaluator
            self._evaluator = BeamNGFakeEvaluator(self.config)
        elif ev_name == BeamNGConfig.EVALUATOR_LOCAL_BEAMNG:
            from self_driving.beamng_nvidia_runner import BeamNGNvidiaOob
            self._evaluator = BeamNGNvidiaOob(self.config)
        elif ev_name == BeamNGConfig.EVALUATOR_REMOTE_BEAMNG:
            from self_driving.beamng_evaluator_remote import BeamNGRemoteEvaluator
            self._evaluator = BeamNGRemoteEvaluator(self.config)
        else:
            raise NotImplemented(self.config.beamng_evaluator)

        return self._evaluator

    def pre_evaluate_members(self, individuals: List[BeamNGIndividual]):
        # return
        # the following code does not work as wanted or expected!
        all_members = list(itertools.chain(*[(ind.m1, ind.m2) for ind in individuals]))
        log.info('----evaluation warmup')
        self._get_evaluator().evaluate(all_members)
        log.info('----warmup completed')

    def pre_evaluate_members_binary_search(self, individuals: List[BeamNGIndividual], dict_already_done):

        all_members = list(itertools.chain(*[(individuals.m1, individuals.m2)]))
        log.info('----evaluation of two members ')
        result = self._get_evaluator().evaluate_binary_search(all_members, dict_already_done)
        log.info('----evaluation of two members completed')
        return result
    def pre_evaluate_members_hill_climbing(self, individuals: List[BeamNGIndividual]):

        all_members = list(itertools.chain(*[(individuals.m1, individuals.m2)]))
        log.info('----evaluation of two members ')
        result , distances = self._get_evaluator().evaluate_hill_climbing(all_members)
        log.info('----evaluation of two members completed')
        return result , distances
