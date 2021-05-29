import json

from core import nsga2
from core.archive_impl import FogArchive
from data.experiments_20210519085252.self_driving.beamng_config import BeamNGConfig
import matplotlib.pyplot as plt

from data.experiments_20210519085252.self_driving.beamng_problem import BeamNGProblem



def start():
    config = BeamNGConfig()
    problem = BeamNGProblem(config, FogArchive())
    p, q, path_ind = nsga2.main(problem)
    print('done')
    plt.ioff()
    plt.show()
    return path_ind

