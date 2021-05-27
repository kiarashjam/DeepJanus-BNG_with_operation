from core import nsga2
from core.archive_impl import SmartArchive
from self_driving.beamng_config import BeamNGConfig
import matplotlib.pyplot as plt
import json
from datetime import time
from os import listdir
from os.path import isfile, join
from time import sleep

from self_driving.beamng_problem import BeamNGProblem

class InitialValue:
    fog_max = 1
    fog_min = 0
    precise_fog = 0.2
    path = ""

def start():
    config = BeamNGConfig()
    problem = BeamNGProblem(config, SmartArchive(config.ARCHIVE_THRESHOLD))
    new_start(problem)

def new_start(problem):
    i = 0
    while i < 6:
        fog_densities_boundary = []
        self = InitialValue
        p, q, path_ind = nsga2.main(problem)
        if path_ind:
            f = open(path_ind)
            ind = json.load(f)
            fog_densities_boundary.append(ind["m1"]['fog_density'])
            fog_densities_boundary.append(ind["m2"]['fog_density'])
            f.close()
            maximum = max(fog_densities_boundary)
            minimum = min(fog_densities_boundary)
            self.fog_max = maximum
            self.fog_min = minimum
            self.precise_fog = self.precise_fog / 10
            print(self.fog_max)
            print(self.fog_min)
        i = i + 1
    print('**** CRITICAL ERROR (you may want to run) ****')

    plt.ioff()
    plt.show()


