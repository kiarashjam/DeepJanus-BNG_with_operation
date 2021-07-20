import json
import sys
import os
from pathlib import Path

path = Path(os.path.abspath(__file__))
# This corresponds to DeepHyperion-BNG
sys.path.append(str(path.parent))
sys.path.append(str(path.parent.parent))


from self_driving.beamng_problem import BeamNGProblem
from core import nsga2
from core import binary_search
from core import failure_finder
from core.archive_impl import GreedyArchive, SmartArchive , AllInArchive
from self_driving.beamng_config import BeamNGConfig
from datetime import datetime

start_time = datetime.now()
print(start_time)
config = BeamNGConfig()

# problem = BeamNGProblem(config, SmartArchive(config.ARCHIVE_THRESHOLD))
# problem = BeamNGProblem(config, GreedyArchive())
problem = BeamNGProblem(config, AllInArchive())

if __name__ == '__main__':

    if config.SEARCH_ALGORITHM == "NSGA2":
        nsga2.main(problem, start_time)
    elif config.SEARCH_ALGORITHM == "BINARY_SEARCH":
        binary_search.main(problem, start_time)
    elif config.SEARCH_ALGORITHM == "FAILURE_FINDER":
        failure_finder.main(problem, start_time)
    print('done')


    