import logging as log
import os
import random
import time
import traceback
from typing import List, Tuple

from core.folder_storage import SeedStorage
from core.folders import folders
from core.log_setup import get_logger
from self_driving.beamng_brewer import BeamNGBrewer
from self_driving.beamng_config import BeamNGConfig
from self_driving.beamng_evaluator import BeamNGEvaluator
from self_driving.beamng_member import BeamNGMember
from self_driving.beamng_tig_maps import maps
from self_driving.beamng_operations import operations
from self_driving.beamng_waypoint import BeamNGWaypoint
from self_driving.nvidia_prediction import NvidiaPrediction
from self_driving.simulation_data import SimulationDataRecord, SimulationData
from self_driving.simulation_data_collector import SimulationDataCollector
from self_driving.utils import get_node_coords, points_distance
from self_driving.vehicle_state_reader import VehicleStateReader
from udacity_integration.beamng_car_cameras import BeamNGCarCameras
from tensorflow.keras.models import load_model

log = get_logger(__file__)

FloatDTuple = Tuple[float, float, float, float]


class BeamNGNvidiaOob(BeamNGEvaluator):
    def __init__(self, config: BeamNGConfig):
        print(
            "BeamNGNvidiaRunner....................................... initial ...........................................")

        self.config = config
        self.brewer: BeamNGBrewer = None
        self.model_file = str(folders.trained_models_colab.joinpath(config.keras_model_file))
        if not os.path.exists(self.model_file):
            raise Exception(f'File {self.model_file} does not exist!')
        self.model = None
        self.problem: 'BeamNGProblem' = None
        self.stop_searching = True

    def evaluate_operation(self,  members: List[BeamNGMember]):
        print(
            "BeamNGNvidiaRunner....................................... evaluate_operation ...........................................")
        for member in members:
            sim = self._run_simulation_operation(member.sample_nodes, member.type_operation, member.amount)
        return sim

    def _run_simulation_operation(self, nodes, type_operation, amount) -> SimulationData:


        print(
            "BeamNGNvidiaRunner....................................... _run_simulation ...........................................")
        print("the amount is = " + str(amount))
        if type_operation == "fog":
            operations.change_fog_amount(amount)
        elif type_operation == "rain":
            operations.change_rain_amount(amount)
        elif type_operation == "wet_foam":
            operations.change_foam_amount(amount)
        elif type_operation == "wet_ripple":
            operations.change_ripple_amount(amount)
        elif type_operation == "default":
            operations.default()
        if not self.brewer:
            self.brewer = BeamNGBrewer(beamng_home=self.config.BNG_HOME)
            self.vehicle = self.brewer.setup_vehicle()
            self.camera = self.brewer.setup_scenario_camera()

        brewer = self.brewer
        brewer.setup_road_nodes(nodes)
        beamng = brewer.beamng
        waypoint_goal = BeamNGWaypoint('waypoint_goal', get_node_coords(nodes[-1]))
        maps.install_map_if_needed()
        maps.beamng_map.generated().write_items(brewer.decal_road.to_json() + '\n' + waypoint_goal.to_json())

        cameras = BeamNGCarCameras()
        vehicle_state_reader = VehicleStateReader(self.vehicle, beamng, additional_sensors=cameras.cameras_array)
        brewer.vehicle_start_pose = brewer.road_points.vehicle_start_pose()

        steps = brewer.params.beamng_steps
        simulation_id = time.strftime('%Y-%m-%d--%H-%M-%S', time.localtime())
        name = self.config.simulation_name.replace('$(id)', simulation_id)
        sim_data_collector = SimulationDataCollector(self.vehicle, beamng, brewer.decal_road, brewer.params,
                                                     vehicle_state_reader=vehicle_state_reader,
                                                     camera=self.camera,
                                                     simulation_name=name, operation_type=type_operation, amount=amount)
        # #
        # sim_data_collector.get_simulation_data().start()
        try:
            brewer.bring_up(type_operation, amount)
            if not self.model:
                self.model = load_model(self.model_file)
            predict = NvidiaPrediction(self.model, self.config)
            iterations_count = 10000
            idx = 0
            while True:
                idx += 1
                if idx >= iterations_count:
                    #     sim_data_collector.save()
                    raise Exception('Timeout simulation ', sim_data_collector.name)

                sim_data_collector.collect_current_data(oob_bb=False)
                last_state: SimulationDataRecord = sim_data_collector.states[-1]
                if points_distance(last_state.pos, waypoint_goal.position) < 6.0:
                    print("the car finish the line #######################################################")
                    sim_data_collector.get_simulation_data().end(success=True)
                    sim_data_collector.save()
                    validity = True
                    break
                if last_state.is_oob:
                    print("the car is out of boundary #######################################################")
                    validity = False
                    sim_data_collector.get_simulation_data().end(success=True)
                    break
        except Exception as ex:
            print("failure #######################################################")
            sim_data_collector.get_simulation_data().end(success=True)
            traceback.print_exception(type(ex), ex, ex.__traceback__)
        finally:
            self.end_iteration()
        return validity


    def end_iteration(self):
        print(
            "BeamNGNvidiaRunner....................................... end_iteration ...........................................")
        try:
            if self.config.beamng_close_at_iteration:
                self._close()
            else:
                if self.brewer:
                    self.brewer.beamng.stop_scenario()
        except Exception as ex:
            log.debug('end_iteration() failed:')
            traceback.print_exception(type(ex), ex, ex.__traceback__)

    def _close(self):
        print(
            "BeamNGNvidiaRunner....................................... _close ...........................................")
        if self.brewer:
            try:
                self.brewer.beamng.close()
            except Exception as ex:
                log.debug('beamng.close() failed:')
                traceback.print_exception(type(ex), ex, ex.__traceback__)
            self.brewer = None


if __name__ == '__main__':
    config = BeamNGConfig()
    inst = BeamNGNvidiaOob(config)
    while True:
        seed_storage = SeedStorage('basic5')
        for i in range(1, 11):
            member = BeamNGMember.from_dict(seed_storage.load_json_by_index(i))
            member.clear_evaluation()
            inst.evaluate([member])
            log.info(member)
