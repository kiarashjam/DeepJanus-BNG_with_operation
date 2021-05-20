import hashlib
import math
import random
from typing import Tuple, Dict

from similaritymeasures import frechet_dist

from core.config import Config
from self_driving.beamng_config import BeamNGConfig
from self_driving.beamng_evaluator import BeamNGEvaluator
from core.member import Member
from self_driving.catmull_rom import catmull_rom
from self_driving.road_bbox import RoadBoundingBox
from self_driving.road_polygon import RoadPolygon
from self_driving.edit_distance_polyline import iterative_levenshtein

Tuple4F = Tuple[float, float, float, float]
Tuple2F = Tuple[float, float]


class BeamNGMember(Member):
    """A class representing a road returned by the RoadGenerator."""
    counter = 0

    def __init__(self, control_nodes: Tuple4F, sample_nodes: Tuple4F, num_spline_nodes: int,
                 road_bbox: RoadBoundingBox, fog_density, number_drop_rain, wet_foam_density, wet_ripple_density,
                           number_of_bump, position_of_obstacle, illumination, mutation_type):

        print("BeamNGMember........initial.........")
        super().__init__()
        BeamNGMember.counter += 1
        self.name = f'mbr{str(BeamNGMember.counter)}'
        self.name_ljust = self.name.ljust(7)
        self.control_nodes = control_nodes
        self.sample_nodes = sample_nodes
        self.num_spline_nodes = num_spline_nodes
        self.road_bbox = road_bbox
        self.config: BeamNGConfig = None
        self.problem: 'BeamNGProblem' = None
        self._evaluator: BeamNGEvaluator = None
        self.fog_density = fog_density
        self.number_drop_rain = number_drop_rain
        self.wet_foam_density = wet_foam_density
        self.wet_ripple_density = wet_ripple_density
        self.number_of_bump = number_of_bump
        self.position_of_obstacle = position_of_obstacle
        self.illumination = illumination
        self.mutation_type = mutation_type
        self.surrounding_type = None
        self.surrounding_amount = {"Trees_amount": 0, "Rocks_amount": 0, "Cabin_amount": 0, "House_amount": 0}


    def clone(self):
        print("BeamNGMember........clone.........")

        res = BeamNGMember(list(self.control_nodes), list(self.sample_nodes), self.num_spline_nodes, self.road_bbox,
                           self.fog_density,  self.number_drop_rain, self.wet_foam_density, self.wet_ripple_density,
                           self.number_of_bump, self.position_of_obstacle, self.illumination, self.mutation_type)
        res.config = self.config
        res.problem = self.problem
        res.distance_to_boundary = self.distance_to_boundary
        res.mutation_type = self.problem.config.MUTATION_TYPE
        res.surrounding_type = self.problem.config.SURROUNDING
        res.surrounding_amount = self.problem.config.Surrounding_amount
        if self.problem.config.MUTATION_TYPE == "MUT_OBSTACLE" and self.position_of_obstacle == (0, 0, 0):
            while True:
                new_amount = (
                random.randint(-1000, 1000), random.randint(-1000, 1000), self.control_nodes[0][2])
                if self.is_valid(new_amount):
                    res.position_of_obstacle = new_amount
                    break
        return res

    def to_dict(self) -> dict:
        print("BeamNGMember........to_dict.........")
        return {
            'control_nodes': self.control_nodes,
            'sample_nodes': self.sample_nodes,
            'num_spline_nodes': self.num_spline_nodes,
            'road_bbox_size': self.road_bbox.bbox.bounds,
            'distance_to_boundary': self.distance_to_boundary,
            'fog_density': self.fog_density,
            'number_drop_rain': self.number_drop_rain,
            'wet_foam_density': self.wet_foam_density,
            'wet_ripple_density': self.wet_ripple_density,
            'number_of_bump': self.number_of_bump,
            'position_of_obstacle': self.position_of_obstacle,
            'illumination': self.illumination,

            'mutation_type': self.mutation_type
        }

    @classmethod
    def from_dict(cls, dict: Dict):
        print("BeamNGMember........from_dict.........")
        road_bbox = RoadBoundingBox(dict['road_bbox_size'])
        res = BeamNGMember([tuple(t) for t in dict['control_nodes']],
                           [tuple(t) for t in dict['sample_nodes']],
                           dict['num_spline_nodes'], road_bbox, dict['fog_density'], dict['number_drop_rain'],
                           dict['wet_foam_density'], dict['wet_ripple_density'], dict['number_of_bump'],
                           dict['position_of_obstacle'], dict['illumination'], dict['mutation_type'])
        res.distance_to_boundary = dict['distance_to_boundary']
        return res

    def evaluate(self):
        print("BeamNGMember........evaluate.........")
        if self.needs_evaluation():
            self.problem._get_evaluator().evaluate([self])
            print('eval mbr', self)

        assert not self.needs_evaluation()

    def needs_evaluation(self):
        return self.distance_to_boundary is None

    def clear_evaluation(self):
        self.distance_to_boundary = None

    def is_valid(self, amount):
        print("BeamNGMember........is_valid.........")
        if self.mutation_type == 'MUT_FOG':
            return self.problem.config.FOG_DENSITY_threshold_min < amount < self.problem.config.FOG_DENSITY_threshold_max
        elif self.mutation_type == 'MUT_RAIN':
            return self.problem.config.NUMBER_OF_DROP_RAIN_threshold_min < amount < self.problem.config.NUMBER_OF_DROP_RAIN_threshold_max
        elif self.mutation_type == 'MUT_WET_FOAM':
            return self.problem.config.WET_FOAM_threshold_min < amount < self.problem.config.WET_FOAM_threshold_max
        elif self.mutation_type == 'MUT_WET_RIPPLE':
            return self.problem.config.WET_RIPPLE_threshold_min < amount < self.problem.config.WET_RIPPLE_threshold_max
        elif self.mutation_type == 'MUT_ILLUMINATION':
            return self.problem.config.ILLUMINATION_AMOUNT_threshold_min < amount < self.problem.config.ILLUMINATION_AMOUNT_threshold_max
        elif self.mutation_type == 'MUT_OBSTACLE':
            for node in self.control_nodes:
                distance = math.sqrt(((node[0] - amount[0]) ** 2) + ((node[1] - amount[1]) ** 2))
                if distance < 5:
                    return True
            return False

            # return self.problem.config.ADDING_OBSTACLE_min < amount < self.problem.config.ADDING_OBSTACLE_max
        elif self.mutation_type == 'MUT_BUMP':
            return self.problem.config.NUMBER_BUMP_threshold_min < amount < self.problem.config.NUMBER_BUMP_threshold_max
        elif self.mutation_type == 'MUT_CONTROL_POINTS':
            return (RoadPolygon.from_nodes(self.sample_nodes).is_valid() and
                    self.road_bbox.contains(RoadPolygon.from_nodes(self.control_nodes[1:-1])))

    def distance(self, other: 'BeamNGMember'):
        #TODO
        #return frechet_dist(self.sample_nodes, other.sample_nodes)
        return iterative_levenshtein(self.sample_nodes, other.sample_nodes)
        #return frechet_dist(self.sample_nodes[0::3], other.sample_nodes[0::3])

    def to_tuple(self):
        import numpy as np
        barycenter = np.mean(self.control_nodes, axis=0)[:2]
        return barycenter

    def mutate(self) -> 'BeamNGMember':
        print("BeamNGMember........mutate.........")
        self.mutation_type = self.problem.config.MUTATION_TYPE
        if self.problem.config.MUTATION_TYPE == 'MUT_FOG':
            FogMutator(self, min_amount=-int(self.problem.config.MUTATION_FOG_EXTENT),
                       max_amount=int(self.problem.config.MUTATION_FOG_EXTENT),
                       discrete_value=self.problem.config.MUTATION_FOG_DISCRETE).mutate()
            self.distance_to_boundary = None
        elif self.problem.config.MUTATION_TYPE == 'MUT_RAIN':
            RainMutator(self, min_amount=-int(self.problem.config.MUTATION_RAIN_EXTENT),
                       max_amount=int(self.problem.config.MUTATION_RAIN_EXTENT),
                       discrete_value=self.problem.config.MUTATION_RAIN_DISCRETE).mutate()
        elif self.problem.config.MUTATION_TYPE == 'MUT_WET_FOAM':
            WetFoamMutator(self, min_amount=-int(self.problem.config.MUTATION_FOAM_EXTENT),
                       max_amount=int(self.problem.config.MUTATION_FOAM_EXTENT),
                       discrete_value=self.problem.config.MUTATION_FOAM_DISCRETE).mutate()
        elif self.problem.config.MUTATION_TYPE == 'MUT_WET_RIPPLE':
            WetRippleMutator(self, min_amount=-int(self.problem.config.MUTATION_RIPPLE_EXTENT),
                       max_amount=int(self.problem.config.MUTATION_RIPPLE_EXTENT),
                       discrete_value=self.problem.config.MUTATION_RIPPLE_DISCRETE).mutate()
        elif self.problem.config.MUTATION_TYPE == 'MUT_ILLUMINATION':
            ChangeIlluminationMutator(self, min_amount=-int(self.problem.config.MUTATION_ILLUMINATION_EXTENT),
                       max_amount=int(self.problem.config.MUTATION_ILLUMINATION_EXTENT),
                       discrete_value=self.problem.config.MUTATION_ILLUMINATION_DISCRETE).mutate()
        elif self.problem.config.MUTATION_TYPE == 'MUT_OBSTACLE':
            AddObstacleMutator(self, min_amount=-int(self.problem.config.MUTATION_OBSTACLE_EXTENT),
                       max_amount=int(self.problem.config.MUTATION_OBSTACLE_EXTENT),
                       discrete_value=self.problem.config.MUTATION_OBSTACLE_DISCRETE,
                       axis=self.problem.config.MUTATION_OBSTACLE_AXIS).mutate()
        elif self.problem.config.MUTATION_TYPE == 'MUT_BUMP':
            AddBumpMutator(self, min_amount=-int(self.problem.config.MUTATION_BUMP_EXTENT),
                       max_amount=int(self.problem.config.MUTATION_BUMP_EXTENT),
                       discrete_value=self.problem.config.MUTATION_BUMP_DISCRETE).mutate()
        elif self.problem.config.MUTATION_TYPE == 'MUT_CONTROL_POINTS':
            RoadMutator(self, lower_bound=-int(self.problem.config.MUTATION_EXTENT),
                        upper_bound=int(self.problem.config.MUTATION_EXTENT)).mutate()
        self.distance_to_boundary = None
        return self

    def __repr__(self):
        eval_boundary = 'na'
        if self.distance_to_boundary:
            eval_boundary = str(self.distance_to_boundary)
            if self.distance_to_boundary > 0:
                eval_boundary = '+' + eval_boundary
            eval_boundary = '~' + eval_boundary
        eval_boundary = eval_boundary[:7].ljust(7)
        h = hashlib.sha256(str([tuple(node) for node in self.control_nodes]).encode('UTF-8')).hexdigest()[-5:]
        return f'{self.name_ljust} h={h} b={eval_boundary}'


class RoadMutator:
    NUM_UNDO_ATTEMPTS = 20

    def __init__(self, road: BeamNGMember, lower_bound=-2, upper_bound=2):
        self.road = road
        self.lower_bound = lower_bound
        self.higher_bound = upper_bound

    def mutate_gene(self, index, xy_prob=0.5) -> Tuple[int, int]:
        gene = list(self.road.control_nodes[index])
        # Choose the mutation extent
        mut_value = random.randint(self.lower_bound, self.higher_bound)
        # Avoid to choose 0
        if mut_value == 0:
            mut_value += 1
        c = 0
        if random.random() < xy_prob:
            c = 1
        gene[c] += mut_value
        self.road.control_nodes[index] = tuple(gene)
        self.road.sample_nodes = catmull_rom(self.road.control_nodes, self.road.num_spline_nodes)
        return c, mut_value

    def undo_mutation(self, index, c, mut_value):
        gene = list(self.road.control_nodes[index])
        gene[c] -= mut_value
        self.road.control_nodes[index] = tuple(gene)
        self.road.sample_nodes = catmull_rom(self.road.control_nodes, self.road.num_spline_nodes)

    def mutate(self, num_undo_attempts=10):
        backup_nodes = list(self.road.control_nodes)
        attempted_genes = set()
        n = len(self.road.control_nodes) - 2

        def next_gene_index() -> int:
            if len(attempted_genes) == n:
                return -1
            i = random.randint(3, n-3)
            while i in attempted_genes:
                i = random.randint(3, n-3)
            attempted_genes.add(i)
            assert 3 <= i <= n-3
            return i

        gene_index = next_gene_index()

        while gene_index != -1:
            c, mut_value = self.mutate_gene(gene_index)

            attempt = 0

            is_valid = self.road.is_valid(0)
            while not is_valid and attempt < num_undo_attempts:
                self.undo_mutation(gene_index, c, mut_value)
                c, mut_value = self.mutate_gene(gene_index)
                attempt += 1
                is_valid = self.road.is_valid(0)

            if is_valid:
                break
            else:
                gene_index = next_gene_index()

        if gene_index == -1:
            raise ValueError("No gene can be mutated")

        assert self.road.is_valid(0)
        assert self.road.control_nodes != backup_nodes

class FogMutator:
    def __init__(self, operation, min_amount, max_amount, discrete_value):
        self.operation = operation
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.discrete_value = discrete_value

    def mutate(self):
        while True:
            temp = random.randint(self.min_amount, self.max_amount)
            distance_mutant_value = temp * self.discrete_value
            new_amount = self.operation.fog_density + distance_mutant_value
            if self.operation.is_valid(new_amount):
                if new_amount != self.operation.fog_density:
                    self.operation.fog_density = new_amount
                    break

class RainMutator:
    def __init__(self, operation, min_amount, max_amount, discrete_value):
        self.operation = operation
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.discrete_value = discrete_value

    def mutate(self):
        while True:

            temp = random.randint(self.min_amount, self.max_amount)
            distance_mutant_value = temp * self.discrete_value
            new_amount = self.operation.number_drop_rain + distance_mutant_value
            if self.operation.is_valid(new_amount):
                if new_amount != self.operation.number_drop_rain:
                    self.operation.fog_density = new_amount
                    break

class WetFoamMutator:
    def __init__(self, operation, min_amount, max_amount, discrete_value):
        self.operation = operation
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.discrete_value = discrete_value

    def mutate(self,):
        while True:
            temp = random.randint(self.min_amount, self.max_amount)
            distance_mutant_value = temp * self.discrete_value
            new_amount = self.operation.wet_foam_density + distance_mutant_value
            if self.operation.is_valid(new_amount):
                if new_amount != self.operation.wet_foam_density:
                    self.operation.fog_density = new_amount
                    break


class WetRippleMutator:
    def __init__(self, operation, min_amount, max_amount, discrete_value):
        self.operation = operation
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.discrete_value = discrete_value

    def mutate(self):
        while True:
            temp = random.randint(self.min_amount, self.max_amount)
            distance_mutant_value = temp * self.discrete_value
            new_amount = self.operation.wet_ripple_density + distance_mutant_value
            if self.operation.is_valid(new_amount):
                if new_amount != self.operation.wet_ripple_density:
                    self.operation.fog_density = new_amount
                    break


class ChangeIlluminationMutator:
    def __init__(self, operation, min_amount, max_amount, discrete_value):
        self.operation = operation
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.discrete_value = discrete_value

    def mutate(self):
        while True:
            temp = random.randint(self.min_amount, self.max_amount)
            distance_mutant_value = temp * self.discrete_value
            new_amount = self.operation.illumination + distance_mutant_value
            if self.operation.is_valid(new_amount):
                if new_amount != self.operation.illumination:
                    self.operation.fog_density = new_amount
                    break


class AddObstacleMutator:
    def __init__(self, operation, min_amount, max_amount, discrete_value, axis):
        self.operation = operation
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.discrete_value = discrete_value
        self.axis = axis

    def mutate(self):
        if axis == 'x':
            temp = random.randint(self.min_amount, self.max_amount)
            distance_mutant_value = temp * self.discrete_value
            amount = self.operation.illumination + distance_mutant_value
            new_amount = (self.operation.position_of_obstacle[0]+amount, self.operation.position_of_obstacle[1],
                          self.operation.position_of_obstacle[2])
            self.operation.position_of_obstacle = new_amount
        elif axis == 'y':
            temp = random.randint(self.min_amount, self.max_amount)
            distance_mutant_value = temp * self.discrete_value
            amount = self.operation.illumination + distance_mutant_value
            new_amount = (self.operation.position_of_obstacle[0] , self.operation.position_of_obstacle[1] + amount,
                          self.operation.position_of_obstacle[2])
            self.operation.position_of_obstacle = new_amount

class AddBumpMutator:
    def __init__(self, operation, min_amount, max_amount, discrete_value):
        self.operation = operation
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.discrete_value = discrete_value

    def mutate(self):
        while True:
            temp = random.randint(self.min_amount, self.max_amount)
            distance_mutant_value = temp * self.discrete_value
            new_amount = self.operation.number_of_bump + distance_mutant_value
            if self.operation.is_valid(new_amount):
                if new_amount != self.operation.number_of_bump:
                    self.operation.fog_density = new_amount
                    break