import random
from beamngpy import BeamNGpy, Scenario, Vehicle, ProceduralCube
from beamngpy.sensors import Camera
from core.folder_storage import SeedStorage
from self_driving.beamng_config import BeamNGConfig
from self_driving.beamng_member import BeamNGMember
from self_driving.decal_road import DecalRoad
from self_driving.road_points import List4DTuple, RoadPoints
from self_driving.simulation_data import SimulationParams
from self_driving.beamng_pose import BeamNGPose
from self_driving.beamng_operations import operations


class BeamNGCamera:
    def __init__(self, beamng: BeamNGpy, name: str, camera: Camera = None):
        self.name = name
        self.pose: BeamNGPose = BeamNGPose()
        self.camera = camera
        if not self.camera:
            self.camera = Camera((0, 0, 0), (0, 0, 0), 120, (1280, 1280), colour=True, depth=True, annotation=True)
        self.beamng = beamng

    def get_rgb_image(self):
        self.camera.pos = self.pose.pos
        self.camera.direction = self.pose.rot
        cam = self.beamng.render_cameras()
        img = cam[self.name]['colour'].convert('RGB')
        return img


class BeamNGBrewer:
    def __init__(self, road_nodes: List4DTuple = None):
        self.beamng = BeamNGpy('localhost', 64256)
        self.vehicle: Vehicle = None
        self.camera: BeamNGCamera = None
        if road_nodes:
            self.setup_road_nodes(road_nodes)
        steps = 5
        self.params = SimulationParams(beamng_steps=steps, delay_msec=int(steps * 0.05 * 1000))
        self.vehicle_start_pose = BeamNGPose()

    def setup_road_nodes(self, road_nodes):
        self.road_nodes = road_nodes
        self.decal_road: DecalRoad = DecalRoad('street_1').add_4d_points(road_nodes)
        self.road_points = RoadPoints().add_middle_nodes(road_nodes)

    def setup_operation(self, member):
        self.fog_density = member.fog_density
        self.wet_foam_density = member.wet_foam_density
        self.number_drop_rain = member.number_drop_rain
        self.wet_ripple_density = member.wet_ripple_density
        self.number_of_bump = member.number_of_bump
        self.number_of_obstacle = member.position_of_obstacle
        self.illumination = member.illumination
        self.type_operation = member.mutation_type


    def setup_vehicle(self) -> Vehicle:
        assert self.vehicle is None
        self.vehicle = Vehicle('ego_vehicle', model='etk800', licence='TIG', color='Red')
        return self.vehicle

    def setup_scenario_camera(self, resolution=(1280, 1280), fov=120) -> BeamNGCamera:
        assert self.camera is None
        self.camera = BeamNGCamera(self.beamng, 'brewer_camera')
        return self.camera

    def setup_fog(self, amount):
        operations.change_fog_amount(amount)

    def setup_rain(self, amount):
        operations.change_rain_amount(amount)

    def setup_wet_foam(self, amount):
        operations.change_foam_amount(amount)

    def setup_wet_ripple(self, amount):
        operations.change_ripple_amount(amount)

    def setup_changing_illumination(self, amount):
        self.beamng.set_tod(amount)

    def setup_adding_bump(self, amount):
        bump_lists = {"upper_length": random.uniform(4, 5), "upper_width": random.uniform(1, 2),
                      "width": random.uniform(6, 7), "length": random.uniform(10, 11),
                      "height": random.uniform(1, 2)}
        i = 30
        while i < amount:
            self.beamng.create_bump(name="bump" + str(i / 30), upper_length=bump_lists["upper_length"],
                                    upper_width=bump_lists["upper_width"],
                                    rot=(0, 1, 0, 0),
                                    pos=(self.road_nodes[i][0], self.road_nodes[i][1], self.road_nodes[i][2]),
                                    width=bump_lists["width"], length=bump_lists["length"], height=bump_lists["height"])
            i = i + 30

    def setup_adding_obstacle(self, amount):
        i = 0
        cube1 = ProceduralCube(name='cube1', pos=(amount), rot=None,
                               size=(1, 1, 10))
        self.scenario.add_procedural_mesh(cube1)

    def bring_up(self):
        if self.type_operation == "MUT_FOG":
            self.setup_fog(self.fog_density)
        elif self.type_operation  == "MUT_RAIN":
            self.setup_rain(self.number_drop_rain)
        elif self.type_operation  == "MUT_WET_FOAM":
            self.setup_wet_foam(self.wet_foam_density)
        elif self.type_operation  == "MUT_WET_RIPPLE":
            self.setup_wet_ripple(self.wet_ripple_density)
        self.scenario = Scenario('tig', 'tigscenario')
        if self.vehicle:
            self.scenario.add_vehicle(self.vehicle, pos=self.vehicle_start_pose.pos, rot=self.vehicle_start_pose.rot)

        if self.camera:
            self.scenario.add_camera(self.camera.camera, self.camera.name)

        ## addiing the obstacle operator
        if self.type_operation == "MUT_OBSTACLE":
            operations.default()
            self.setup_adding_obstacle(self.number_of_obstacle)

        self.scenario.make(self.beamng)
        if not self.beamng.server:
            self.beamng.open()
        self.beamng.pause()
        self.beamng.set_deterministic()
        self.beamng.load_scenario(self.scenario)
        self.beamng.start_scenario()
        ## changing illumination operator
        if self.type_operation == "MUT_ILLUMINATION":
            # operations.default()
            self.setup_changing_illumination(self.illumination)

        ## adding the bump operation
        if self.type_operation == "MUT_BUMP":
            operations.default()
            self.setup_adding_bump(self.number_of_bump)

    def __del__(self):
        if self.beamng:
            try:
                self.beamng.close()
            except:
                pass


if __name__ == '__main__':
    config = BeamNGConfig()
    brewer = BeamNGBrewer()
    vehicle = brewer.setup_vehicle()
    camera = brewer.setup_scenario_camera()
    while True:
        seed_storage = SeedStorage('basic5')
        for i in range(1, 11):
            member = BeamNGMember.from_dict(seed_storage.load_json_by_index(i))
            brewer.setup_road_nodes(member.sample_nodes)
            brewer.vehicle_start_pose = brewer.road_points.vehicle_start_pose()
            brewer.bring_up()
            print('bring up ok')
            brewer.beamng.resume()
            print('resumed')
            input('waiting keypress...')
            print('key received')
            brewer.beamng.stop_scenario()
