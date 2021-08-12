import json
import sys
import os
from pathlib import Path

path = Path(os.path.abspath(__file__))
# This corresponds to DeepHyperion-BNG
sys.path.append(str(path.parent))
sys.path.append(str(path.parent.parent))


from self_driving.beamng_problem import BeamNGProblem
from core import binary_search , failure_finder, exhaustive_hill_climbing, nsga2, random_walk, stochastic_hill_climbing,simulated_annealing
from core.archive_impl import GreedyArchive, SmartArchive , AllInArchive
from self_driving.beamng_config import BeamNGConfig
from datetime import datetime

start_time = datetime.now()
config = BeamNGConfig()

problem = BeamNGProblem(config, SmartArchive(config.ARCHIVE_THRESHOLD))
# problem = BeamNGProblem(config, GreedyArchive())
# problem = BeamNGProblem(config, AllInArchive())

if __name__ == '__main__':

    if config.SEARCH_ALGORITHM == "NSGA2":
        nsga2.main(problem, start_time)
    elif config.SEARCH_ALGORITHM == "BINARY_SEARCH":
        binary_search.main(problem, start_time)
    elif config.SEARCH_ALGORITHM == "FAILURE_FINDER":
        failure_finder.main(problem, start_time)
    elif config.SEARCH_ALGORITHM == "EXHAUSTIVE_HILL_CLIMBING":
        exhaustive_hill_climbing.main(problem, start_time)
    elif config.SEARCH_ALGORITHM == "RANDOM_WALK":
        random_walk.main(problem, start_time)
    elif config.SEARCH_ALGORITHM == "STOCHASTIC_HILL_CLIMBING":
        stochastic_hill_climbing.main(problem, start_time)
    elif config.SEARCH_ALGORITHM == "SIMULATED_ANNEALING":
        random_walk.main(problem, datetime.now())
        simulated_annealing.main(problem, datetime.now())
        stochastic_hill_climbing.main(problem, datetime.now())
        # exhaustive_hill_climbing.main(problem, datetime.now())
    print('done')


