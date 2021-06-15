import json
import sys
import os
from pathlib import Path

path = Path(os.path.abspath(__file__))
# This corresponds to DeepHyperion-BNG
sys.path.append(str(path.parent))
sys.path.append(str(path.parent.parent))


from core import nsga2
from core.archive_impl import GreedyArchive
from self_driving.beamng_config import BeamNGConfig
import matplotlib.pyplot as plt
from self_driving.beamng_problem import BeamNGProblem

config = BeamNGConfig()
problem = BeamNGProblem(config, GreedyArchive())

if __name__ == '__main__':
    nsga2.main(problem)
    print('done')
    plt.ioff()
    plt.show()



    