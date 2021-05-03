import hashlib
import random
from typing import Tuple, Dict

from self_driving.beamng_config import BeamNGConfig
from self_driving.beamng_evaluator import BeamNGEvaluator
from core.member import Member
from self_driving.road_bbox import RoadBoundingBox
from self_driving.road_polygon import RoadPolygon
from self_driving.edit_distance_polyline import iterative_levenshtein

Tuple4F = Tuple[float, float, float, float]
Tuple2F = Tuple[float, float]


class BeamNGMember(Member):
    """A class representing a road returned by the RoadGenerator."""
    counter = 0

    def __init__(self, control_nodes: Tuple4F, sample_nodes: Tuple4F, num_spline_nodes: int,
                 road_bbox: RoadBoundingBox, type_operation, amount: int,):
        print("BeamNGMember..........................initial....................")
        super().__init__()
        BeamNGMember.counter += 1
        self.name = f'mbr{str(BeamNGMember.counter)}'
        self.amount = amount
        self.type_operation = type_operation
        self.name_ljust = self.name.ljust(7)
        self.control_nodes = control_nodes
        self.sample_nodes = sample_nodes
        self.num_spline_nodes = num_spline_nodes
        self.road_bbox = road_bbox
        self.config: BeamNGConfig = None
        self.problem: 'BeamNGProblem' = None
        self._evaluator: BeamNGEvaluator = None

    def is_valid_operation(self, type_operation, amount):
        print("BeamNGMember..........................is_valid_operation....................")
        if self.type_operation == "fog":
            return self.problem.config.FOG_DENSITY_threshold_min < amount < self.problem.config.FOG_DENSITY_threshold_max
        elif self.type_operation == "rain":
            return self.problem.problem.config.NUMBER_OF_DROP_RAIN_threshold_min < amount < self.problem.config.NUMBER_OF_DROP_RAIN_threshold_max
        elif self.type_operation == "wet_foam":
            return self.problem.config.WET_FOAM_threshold_min < amount < self.problem.config.FOG_DENSITY_threshold_max
        elif self.type_operation == "wet_ripple":
            return self.problem.config.WET_RIPPLE_threshold_min < amount < self.problem.config.WET_RIPPLE_threshold_max
        elif self.type_operation == "default":
            return  True
        elif self.type_operation == "add_obstacle":
            return  self.problem.config.ADDING_OBSTACLE_min < amount < self.problem.config.ADDING_OBSTACLE_max
        elif self.type_operation == "changing_illumination":
            return self.problem.config.ILLUMINATION_AMOUNT_threshold_min < amount < self.problem.config.ILLUMINATION_AMOUNT_threshold_max
        elif self.type_operation == "add_bump":
            return  self.problem.config.NUMBER_BUMP_threshold_min < amount < self.problem.config.NUMBER_BUMP_threshold_max



    def clone(self):
        print("BeamNGMember..........................clone....................")

        res = BeamNGMember(list(self.control_nodes), list(self.sample_nodes), self.num_spline_nodes, self.road_bbox, self.type_operation,self.amount)
        res.config = self.config
        res.problem = self.problem
        res.distance_to_boundary = self.distance_to_boundary
        res.amount = self.amount
        res.type_operation = self.type_operation
        return res

    def to_dict(self) -> dict:
        print("BeamNGMember..........................to_dict....................")
        if self.type_operation == "fog":
            amount = self.config.FOG_DENSITY
        elif self.type_operation == "rain":
            amount = self.config.NUMBER_OF_DROP_RAIN
        elif self.type_operation == "wet_foam":

            amount = self.config.WET_FOAM
        elif self.type_operation == "wet_ripple":
            amount = self.config.WET_RIPPLE
        elif self.type_operation == "default":
            amount = 0
        elif self.type_operation == "add_obstacle":
            amount = self.config.NUMBER_BUMP
        elif self.type_operation == "changing_illumination":
            amount = self.config.ILLUMINATION_AMOUNT

        return {
            'control_nodes': self.control_nodes,
            'sample_nodes': self.sample_nodes,
            'num_spline_nodes': self.num_spline_nodes,
            'road_bbox_size': self.road_bbox.bbox.bounds,
            'distance_to_boundary': self.distance_to_boundary,
            'amount': amount,
            'type': self.type_operation
        }

    @classmethod
    def from_dict(cls, dict: Dict, type_operation, amount):
        print("BeamNGMember..........................from_dict....................")
        road_bbox = RoadBoundingBox(dict['road_bbox_size'])
        res = BeamNGMember([tuple(t) for t in dict['control_nodes']],
                           [tuple(t) for t in dict['sample_nodes']],
                           dict['num_spline_nodes'], road_bbox, type_operation, amount)
        res.distance_to_boundary = dict['distance_to_boundary']
        return res

    def evaluate(self):
        print("BeamNGMember..........................evaluate....................")
        if self.needs_evaluation():
            validity = self.problem._get_evaluator(1).evaluate_operation([self])
            print('eval mbr', self)
            print("the operation validity is  == " + str(validity))

        assert not self.needs_evaluation()

    def needs_evaluation(self):
        print("BeamNGMember..........................needs_evaluation....................")

        return self.distance_to_boundary is None

    def clear_evaluation(self):
        print("BeamNGMember..........................clear_evaluation....................")

        self.distance_to_boundary = None

    # def is_valid(self):
    #     print("BeamNGMember..........................is_valid....................")
    #
    #     return (RoadPolygon.from_nodes(self.sample_nodes).is_valid() and
    #             self.road_bbox.contains(RoadPolygon.from_nodes(self.control_nodes[1:-1])))

    def distance(self, other: 'BeamNGMember'):
        print("BeamNGMember..........................distance....................")
        #TODO
        #return frechet_dist(self.sample_nodes, other.sample_nodes)
        return iterative_levenshtein(self.sample_nodes, other.sample_nodes)
        #return frechet_dist(self.sample_nodes[0::3], other.sample_nodes[0::3])

    def to_tuple(self):
        print("BeamNGMember..........................to_tuple....................")
        import numpy as np
        barycenter = np.mean(self.control_nodes, axis=0)[:2]
        return barycenter

    def mutate_operation(self) -> 'BeamNGMember':
        print("BeamNGMember..........................mutate....................")
        if self.type_operation == "fog":
            OperatorMutant(self).mutate(self.problem.config.FOG_DENSITY_threshold_min, self.problem.config.FOG_DENSITY_threshold_max, 1)
        elif self.type_operation == "rain":
            OperatorMutant(self).mutate(self.problem.problem.config.NUMBER_OF_DROP_RAIN_threshold_min, self.problem.config.NUMBER_OF_DROP_RAIN_threshold_max, 2)
        elif self.type_operation == "wet_foam":
            OperatorMutant(self).mutate(self.problem.config.WET_FOAM_threshold_min, self.problem.config.FOG_DENSITY_threshold_max, 2)
        elif self.type_operation == "wet_ripple":
            OperatorMutant(self).mutate(self.problem.config.WET_RIPPLE_threshold_min, self.problem.config.WET_RIPPLE_threshold_max, 2)
        elif self.type_operation == "default":
            print("default change")
        elif self.type_operation == "add_obstacle":
            OperatorMutant(self).mutate(self.problem.config.ADDING_OBSTACLE_min, self.problem.config.ADDING_OBSTACLE_max, 2)
        elif self.type_operation == "changing_illumination":
            OperatorMutant(self).mutate(self.problem.config.ILLUMINATION_AMOUNT_threshold_min, self.problem.config.ILLUMINATION_AMOUNT_threshold_max, 1)
        elif self.type_operation == "add_bump":
            OperatorMutant(self).mutate(self.problem.config.NUMBER_BUMP_threshold_min, self.problem.config.NUMBER_BUMP_threshold_max, 2)



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

class OperatorMutant:

    def __init__(self, operation):
        print(
            "OperatorMutant................................... initial ...........................................")
        self.operation = operation
        print(self.operation.amount)

    def mutate(self, minimum, maximum, type_operator):
        print(
            "OperatorMutant................................... mutate ...........................................")
        if type_operator == 1:
            while True:
                new_amount = random.choice([random.uniform(minimum, self.operation.amount), random.uniform(self.operation.amount, maximum)])
                if self.operation.is_valid_operation(type_operator, new_amount):
                    if new_amount != self.operation.amount:
                        self.operation.amount = new_amount
                        print(self.operation.amount)
                    break
        if type_operator == 2:
            while True:
                new_amount = random.choice([random.randint(minimum, self.operation.amount), random.randint(self.operation.amount, maximum)])
                if self.operation.is_valid_operation(type_operator, new_amount):
                    if new_amount != self.operation.amount:
                        self.operation.amount = new_amount
                        print(self.operation.amount)
                        break
