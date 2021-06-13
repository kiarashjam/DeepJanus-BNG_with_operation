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
            seed_pool = SeedPoolFolder(self, config.initial_population_folder)
        else:
            seed_pool = SeedPoolFolder(self, config.seed_folder)
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

    def deap_evaluate_individual(self, individual: BeamNGIndividual):
        return individual.evaluate()

    def on_iteration(self, idx, pop: List[BeamNGIndividual], logbook):
        self.archive.process_population(pop)
        print("###################")

        self.experiment_path.mkdir(parents=True, exist_ok=True)
        self.experiment_path.joinpath('config.json').write_text(json.dumps(self.config.__dict__))

        gen_path = self.experiment_path.joinpath(f'gen{idx}')
        gen_path.mkdir(parents=True, exist_ok=True)

        # Generate final report at the end of the last iteration.
        # if idx + 1 == self.config.NUM_GENERATIONS:
        fog, rain , foam , ripple , illumination, bump , position ,shape_road , radius, type_operation, fog_avg, \
        rain_avg, foam_avg, ripple_avg, bump_avg, obstacle_avg, illumination_avg , angles   =  get_radius_seed(self.archive)
        report = {
            'archive_len': len(self.archive),
            'operation_type': type_operation,
            'fog_average_amount':fog_avg,
            'rain_average_amount':rain_avg,
            'foam_average_amount':foam_avg,
            'ripple_average_amount':ripple_avg,
            'bump_average_amount':bump_avg,
            'position_obstacle_average_amount':obstacle_avg,
            'illumintaion_average_amount':illumination_avg,
            'normalize_distance_fog':fog,
            'normalize_distance_rain':rain,
            'normalize_distance_foam':foam,
            'normalize_distance_ripple':ripple,
            'normalize_distance_bump':bump,
            'normalize_distance_obstacle':position,
            'normalize_distance_illumination':illumination,
            'normalize_distance_road_shape':shape_road,
            'radius': radius,
            'angle': angles,
            'diameter_out': get_diameter([ind.members_by_sign()[0] for ind in self.archive]),
            'diameter_in': get_diameter([ind.members_by_sign()[1] for ind in self.archive])
        }
        gen_path.joinpath(f'report{idx}.json').write_text(json.dumps(report))

        BeamNGIndividualSetStore(gen_path.joinpath('population')).save(pop)
        BeamNGIndividualSetStore(gen_path.joinpath('archive')).save(self.archive)
        return BeamNGIndividualSetStore(gen_path.joinpath('archive')).save(self.archive)



    def generate_random_member(self) -> Member:


        result = RoadGenerator(num_control_nodes=self.config.num_control_nodes,
                               seg_length=self.config.SEG_LENGTH).generate()
        result.config = self.config
        result.mutation_type = self.config.MUTATION_TYPE
        result.surrounding_type = self.config.SURROUNDING

        pointes = result.control_nodes
        n = len(pointes)
        i = 0
        array_angles = []
        while i < n-3 :
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

        if self.config.MUTATION_TYPE == 'MUT_FOG':
            result.fog_density = random.uniform(self.config.FOG_DENSITY_threshold_min,
                                                self.config.FOG_DENSITY_threshold_max)
            result.wet_foam_density = 0
            result.number_drop_rain = 0
            result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_RAIN':
            result.fog_density = 0
            result.wet_foam_density = 0
            result.number_drop_rain = random.randint(self.config.NUMBER_OF_DROP_RAIN_threshold_min,
                                          self.config.NUMBER_OF_DROP_RAIN_threshold_max)
            result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_WET_FOAM':
            result.fog_density = 0
            result.wet_foam_density = random.randint(self.config.WET_FOAM_threshold_min,
                                                     self.config.WET_FOAM_threshold_max)
            result.number_drop_rain = 0
            result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_WET_RIPPLE':
            result.fog_density = 0
            result.wet_foam_density = 0
            result.number_drop_rain = 0
            result.wet_ripple_density = random.randint(self.config.WET_RIPPLE_threshold_min,
                                                       self.config.WET_RIPPLE_threshold_max)
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_ILLUMINATION':
            result.fog_density = 0
            result.wet_foam_density = 0
            result.number_drop_rain = 0
            result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.position_of_obstacle = (0, 0, 0)
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
            result.wet_ripple_density = 0
            result.number_of_bump = 0
            result.illumination = 0
        elif self.config.MUTATION_TYPE == 'MUT_BUMP':
            result.fog_density = 0
            result.wet_foam_density = 0
            result.number_drop_rain = 0
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
            #log.info(f'reseed{seed_range}')
            #for i in range(0, seed_range):
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
        log.info('----warmpup completed')
