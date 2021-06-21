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
from core.archive_impl import SmartArchive
from self_driving.beamng_config import BeamNGConfig
from datetime import datetime

start_time = datetime.now()
print(start_time)
config = BeamNGConfig()

problem = BeamNGProblem(config, SmartArchive(config.ARCHIVE_THRESHOLD))

if __name__ == '__main__':

    print("################start")
    print(str(datetime.now() - start_time))

    nsga2.main(problem, start_time)
    print('done')


    