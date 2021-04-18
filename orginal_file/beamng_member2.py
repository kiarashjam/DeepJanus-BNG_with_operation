# import hashlib
# import random
# from typing import Tuple, Dict
#
# from self_driving.beamng_config import BeamNGConfig
# from self_driving.beamng_evaluator import BeamNGEvaluator
# from core.member import Member
# from self_driving.catmull_rom import catmull_rom
# from self_driving.road_bbox import RoadBoundingBox
# from self_driving.road_polygon import RoadPolygon
# from self_driving.edit_distance_polyline import iterative_levenshtein
#
# Tuple4F = Tuple[float, float, float, float]
# Tuple2F = Tuple[float, float]
#
#
# class BeamNGMember(Member):
#     """A class representing a road returned by the RoadGenerator."""
#     counter = 0
#
#     def __init__(self, illumination_amount):
#         print("............phase 9q ................")
#         super().__init__()
#
#         BeamNGMember.counter += 1
#         self.illumination_amount = illumination_amount
#         self.name = f'mbr{str(BeamNGMember.counter)}'
#         self.name_ljust = self.name.ljust(7)
#         self.config: BeamNGConfig = None
#         self.problem: 'BeamNGProblem' = None
#         self._evaluator: BeamNGEvaluator = None
#
#     def clone(self):
#         res = BeamNGMember(list(self.illumination_amount))
#         res.config = self.config
#         res.problem = self.problem
#         return res
#
#     def to_dict(self) -> dict:
#         return {
#             'illumination_amount': self.illumination_amount
#         }
#
#     @classmethod
#     def from_dict(cls, dict: Dict):
#         road_bbox = RoadBoundingBox(dict['road_bbox_size'])
#         res = BeamNGMember([tuple(t) for t in dict['control_nodes']],
#                            [tuple(t) for t in dict['sample_nodes']],
#                            dict['num_spline_nodes'], road_bbox)
#         res.distance_to_boundary = dict['distance_to_boundary']
#         return res
#
#     def evaluate(self):
#         if self.needs_evaluation():
#             self.problem._get_evaluator().evaluate([self])
#             print('eval mbr', self)
#
#         assert not self.needs_evaluation()
#
#     def needs_evaluation(self):
#         return self.distance_to_boundary is None
#
#     def clear_evaluation(self):
#         self.distance_to_boundary = None
#
#     def is_valid(self):
#         return (RoadPolygon.from_nodes(self.sample_nodes).is_valid() and
#                 self.road_bbox.contains(RoadPolygon.from_nodes(self.control_nodes[1:-1])))
#
#     def distance(self, other: 'BeamNGMember'):
#         #TODO
#         #return frechet_dist(self.sample_nodes, other.sample_nodes)
#         return iterative_levenshtein(self.sample_nodes, other.sample_nodes)
#         #return frechet_dist(self.sample_nodes[0::3], other.sample_nodes[0::3])
#
#     def to_tuple(self):
#         import numpy as np
#         barycenter = np.mean(self.control_nodes, axis=0)[:2]
#         return barycenter
#
#     def mutate(self) -> 'BeamNGMember':
#         FogMutator(self, lower_bound=-int(self.problem.config.ILLUMINATION_AMOUNT), upper_bound=int(self.problem.config.ILLUMINATION_AMOUNT)).mutate()
#         self.distance_to_boundary = None
#         return self
#
#     def __repr__(self):
#         eval_boundary = 'na'
#         if self.distance_to_boundary:
#             eval_boundary = str(self.distance_to_boundary)
#             if self.distance_to_boundary > 0:
#                 eval_boundary = '+' + eval_boundary
#             eval_boundary = '~' + eval_boundary
#         eval_boundary = eval_boundary[:7].ljust(7)
#         h = hashlib.sha256(str([tuple(node) for node in self.control_nodes]).encode('UTF-8')).hexdigest()[-5:]
#         return f'{self.name_ljust} h={h} b={eval_boundary}'
#
# class FogMutator:
#     NUM_UNDO_ATTEMPTS = 20
#     def __init__(self, road: BeamNGMember, lower_bound=-2, upper_bound=2):
#         self.road = road
#         self.lower_bound = lower_bound
#         self.upper_bound = upper_bound
#     def mutate_gene(self):
#
#     def undo_mutation(self):
#
#     def mutate(self):
#         def next_gene_index() -> int:
#             if True :
#                 self.mutate_gene()
#
#
