import hashlib
import random
from typing import Tuple, Dict

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
                 road_bbox: RoadBoundingBox, amount: int, type_operation):
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


    def clone(self):
        print("BeamNGMember..........................clone....................")

        res = BeamNGMember(list(self.control_nodes), list(self.sample_nodes), self.num_spline_nodes, self.road_bbox, self.type_operation,self.amount)
        res.config = self.config
        res.problem = self.problem
        res.distance_to_boundary = self.distance_to_boundary
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
                           dict['num_spline_nodes'], road_bbox,type_operation, amount)
        res.distance_to_boundary = dict['distance_to_boundary']
        return res

    def evaluate(self):
        print("BeamNGMember..........................evaluate....................")
        if self.needs_evaluation():
            self.problem._get_evaluator().evaluate([self])
            print('eval mbr', self)

        # assert not self.needs_evaluation()

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

    def mutate(self) -> 'BeamNGMember':
        print("BeamNGMember..........................mutate....................")
        RoadMutator(self, lower_bound=-int(self.problem.config.MUTATION_EXTENT), upper_bound=int(self.problem.config.MUTATION_EXTENT)).mutate()
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

class FogMutator:
    NUM_UNDO_ATTEMPTS = 10
    def __init__(self,fog_density_amount_high = 0,fog_density_amount_low = 1):
        print(
            "BeamNGMember..............FogMutator......................... initial ...........................................")
        self.fog_density_amount_high = fog_density_amount_high
        self.fog_density_amount_low = fog_density_amount_low
    def mutate_gene(self) -> float:
        print("s")



class RoadMutator:
    NUM_UNDO_ATTEMPTS = 20

    def __init__(self, road: BeamNGMember, lower_bound=-2, upper_bound=2):
        print("BeamNGMember................RoadMutator....................... RoadMutator ...........................................")
        self.road = road
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def mutate_gene(self, index, xy_prob=0.5) -> Tuple[int, int]:
        print("BeamNGMember...................RoadMutator.................... mutate_gene ...........................................")
        gene = list(self.road.control_nodes[index])
        print(index)
        # Choose the mutation extent
        candidate_mut_values = [i for i in range(self.lower_bound, self.upper_bound) if i !=0]
        mut_value = random.choice(candidate_mut_values)
        #mut_value = random.randint(self.lower_bound, self.upper_bound)
        # Avoid to choose 0
        #if mut_value == 0:
        #    mut_value += 1

        # Select coordinate to mutate
        if random.random() < xy_prob:
            c = 1
        else:
            c = 0
        gene[c] += mut_value
        # print(gene[c])
        # print(mut_value)

        self.road.control_nodes[index] = tuple(gene)
        self.road.sample_nodes = catmull_rom(self.road.control_nodes, self.road.num_spline_nodes)

        return c, mut_value

    def undo_mutation(self, index, c, mut_value):
        print("BeamNGMember....................RoadMutator................... undo_mutation ...........................................")
        gene = list(self.road.control_nodes[index])
        gene[c] -= mut_value
        # print("gene is  = "+str(gene))
        self.road.control_nodes[index] = tuple(gene)
        self.road.sample_nodes = catmull_rom(self.road.control_nodes, self.road.num_spline_nodes)

    def mutate(self, num_undo_attempts=10):
        print("BeamNGMember.....................RoadMutator.................. mutate ...........................................")
        backup_nodes = list(self.road.control_nodes)
        # print("back up nodes = "+str(backup_nodes))
        attempted_genes = set()
        n = len(self.road.control_nodes) - 2
        # print("n is "+str(n))
        # print(self.road.control_nodes)

        seglength = 3
        candidate_length = n - (2 * seglength)
        # print("candidate length = "+str(candidate_length))
        assert(candidate_length > 0)

        def next_gene_index() -> int:
            print("BeamNGMember..................RoadMutator..................... next_gene_index ...........................................")
            print("attempted gene  = " + str(attempted_genes))
            print("candidate length = " + str(candidate_length))
            if len(attempted_genes) == candidate_length:
                return -1
            i = None
            condition = False
            while not condition:
                i = random.randint(seglength, n - seglength)
                print("seglength = " + str(seglength))
                print("seglength = " + str(n - seglength))
                if i not in attempted_genes:
                    condition = True
            assert(i is not None)
            assert seglength <= i <= n - seglength

            # i = random.randint(3, n - 3)
            # while i in attempted_genes:
            #     i = random.randint(3, n-3)

            # print("attempted genes = " + str(attempted_genes))
            attempted_genes.add(i)
            return i

        gene_index = next_gene_index()
        # print("gene index = " + str(gene_index))
        while gene_index != -1:
            c, mut_value = self.mutate_gene(gene_index)
            attempt = 0
            is_valid = self.road.is_valid()
            while not is_valid and attempt < num_undo_attempts:
                self.undo_mutation(gene_index, c, mut_value)
                c, mut_value = self.mutate_gene(gene_index)
                attempt += 1
                is_valid = self.road.is_valid()
            if is_valid:
                break
            else:
                gene_index = next_gene_index()
        if gene_index == -1:
            raise ValueError("No gene can be mutated")

        assert self.road.is_valid()
        assert self.road.control_nodes != backup_nodes
