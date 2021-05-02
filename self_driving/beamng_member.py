import hashlib
import random
from typing import Tuple, Dict

from self_driving.beamng_config import BeamNGConfig
from self_driving.beamng_evaluator import BeamNGEvaluator
from core.member import Member
# from self_driving.beamng_nvidia_runner import BeamNGNvidiaOob
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

    def is_valid_operation(self):
        return self.problem._get_evaluator(2).evaluate_operation(self, self.amount, self.type_operation, self.sample_nodes)



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
            temp = self.config.FOG_DENSITY
        elif self.type_operation == "rain":
            temp = self.config.NUMBER_OF_DROP_RAIN
        elif self.type_operation == "wet_foam":

            temp = self.config.WET_FOAM
        elif self.type_operation == "wet_ripple":
            temp = self.config.WET_RIPPLE
        elif self.type_operation == "default":
            amount = 0
        elif self.type_operation == "add_obstacle":
            temp = self.config.NUMBER_BUMP
        elif self.type_operation == "changing_illumination":
            temp = self.config.ILLUMINATION_AMOUNT

        return {
            'control_nodes': self.control_nodes,
            'sample_nodes': self.sample_nodes,
            'num_spline_nodes': self.num_spline_nodes,
            'road_bbox_size': self.road_bbox.bbox.bounds,
            'distance_to_boundary': self.distance_to_boundary,
            'amount': temp,
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
            self.problem._get_evaluator(1).evaluate_operation([self])
            # print('eval mbr', self)

        assert not self.needs_evaluation()

    def needs_evaluation(self):
        print("BeamNGMember..........................needs_evaluation....................")

        return self.distance_to_boundary is None

    def clear_evaluation(self):
        print("BeamNGMember..........................clear_evaluation....................")

        self.distance_to_boundary = None

    def is_valid(self):
        print("BeamNGMember..........................is_valid....................")

        return (RoadPolygon.from_nodes(self.sample_nodes).is_valid() and
                self.road_bbox.contains(RoadPolygon.from_nodes(self.control_nodes[1:-1])))

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
        OperatorMutant(self, lower_bound=-int(self.problem.config.MUTATION_EXTENT), upper_bound=int(self.problem.config.MUTATION_EXTENT)).mutate()
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

    def __init__(self, operation , lower_bound, upper_bound):
        print(
            "OperatorMutant................................... initial ...........................................")
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.operation = operation
        print(self.operation.amount)

    def mutate(self):
        print(
            "OperatorMutant................................... mutate ...........................................")
        if self.operation.type_operation == "fog":
            print(
                "OperatorMutant................................... fog ...........................................")
            self.operation.amount = random.choice([random.uniform(0, self.operation.amount), random.uniform(self.operation.amount, 1)])
            print(self.operation.amount)
        elif self.operation.type_operation == "rain":
            print(
                "OperatorMutant................................... rain ...........................................")
            self.operation.amount = random.choice([random.randint(0, self.operation.amount), random.randint(self.operation.amount, 2000)])
        elif self.operation.type_operation == "wet_foam":
            print(
                "OperatorMutant................................... wet_foam ...........................................")
            self.operation.amount = random.choice([random.randint(0, self.operation.amount), random.randint(self.operation.amount, 20)])
        elif self.operation.type_operation == "wet_ripple":
            print(
                "OperatorMutant................................... wet_ripple ...........................................")
            self.operation.amount = random.choice([random.randint(0, self.operation.amount), random.randint(self.operation.amount, 1000)])
        elif self.operation.type_operation == "default":
            print(
                "OperatorMutant................................... default ...........................................")
            self.operation.amount = 0
        elif self.operation.type_operation == "add_obstacle":
            print(
                "OperatorMutant................................... add_obstacle ...........................................")
            self.operation.amount = random.choice([random.randint(0, self.operation.amount), random.randint(self.operation.amount, 100)])
        elif self.operation.type_operation == "changing_illumination":
            print(
                "OperatorMutant................................... changing_illumination ...........................................")
            self.operation.amount = random.choice([random.uniform(0, self.operation.amount), random.uniform(self.operation.amount, 1)])
        elif self.operation.type_operation == "add_bump":
            print(
                "OperatorMutant................................... add_bump ...........................................")
            self.operation.amount = random.choice([random.randint(0, self.operation.amount), random.randint(self.operation.amount, 1000)])