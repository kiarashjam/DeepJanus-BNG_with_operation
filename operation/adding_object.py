import random

from beamngpy import BeamNGpy, Scenario, Road, Vehicle, setup_logging, ProceduralCube
import numpy as np
import os
import matplotlib.pyplot as plt
from datetime import datetime
from time import sleep
from matplotlib.pyplot import imshow
from PIL import Image
from shapely.geometry import Polygon


class BeamNGWaypoint:
    def __init__(self, name, position, persistentId=None):
        self.name = name
        self.position = position
        self.persistentId = None


# defining the global variable


# defining the beamng requirments
beamng = BeamNGpy('localhost', 64256)
beamng_modify = BeamNGpy('localhost', 64256)
main_scenario = Scenario('tig', 'the main scenario ')
modify_scenario = Scenario('tig',
                           'the scenario with the modification if y coordinate in obstacle in comparison with main scenario')
vehicle = Vehicle('ego_vehicle', model='etk800')
waypiont = BeamNGWaypoint("test1", (0, -400, 0), None)

# defining the changable variable
risk_value = 0.7
n_iterate = 10
amount_of_iterate = 40
number_of_object = 8
orig = (0, 0, -28, 7)
amount = 10
threshold = (orig[0] + amount_of_iterate, orig[1] - n_iterate * amount_of_iterate, orig[0])

# making the path for generating the
path = "testing-" + str(datetime.now().date()) + "-" + str(datetime.now().time().hour) + "-" + str(
    datetime.now().time().minute) + "-" + str(datetime.now().time().second)

# the list
script = list()
object_list = list()
script_x = list()
script_y = list()


# defining the obstacle position
def make_obstacle_position(o, t):
    position = (random.uniform(o[0], t[0]), random.uniform(o[1], t[1]), o[2])
    object_list.append(position)
    return position


# get the new position for the object
def change_obstacle_position(old_position, amount_of_change):
    new_position = (old_position[0], old_position[1] + amount_of_change, old_position[2])
    return new_position


# add obstacle  to scenarios
def make_obstacle(position):
    cube1 = ProceduralCube(name='cube1', pos=(position[0], position[1], position[2]), rot=None, rot_quat=(1, 0, 0, 0),
                           size=(1, 1, 10))
    return cube1


# change the position of the object
def make_obtacle_move(road, position, amount_change):
    cube2 = ProceduralCube(name='cube1', pos=(position[0], position[1] + amount_change, position[2]),
                           rot=None, rot_quat=(1, 0, 0, 0), size=(1, 1, 10))
    return cube2


# making the road
def making_road(n, ei):
    # adding the Road and the lines
    road_main = Road('tig_road_rubber_sticky', rid='main_road', drivability=1, texture_length=5, interpolate=True)

    i = 0
    while i < n:
        nodes_main_road = [
            (orig[0] + ((i % 2) * ei), orig[1] - i * ei, orig[2], 10),
        ]
        # adding the roads
        road_main.nodes.extend(nodes_main_road)
        i = i + 1
    return road_main


# defining the vehicle
def making_vehicle(n, ei, main_scenario_active):
    # adding the Vehicle

    if main_scenario_active:
        main_scenario.add_vehicle(vehicle, pos=(orig[0], orig[1], orig[2], orig[3]), rot=None, rot_quat=(0, 0, 0, 0))
    else:
        modify_scenario.add_vehicle(vehicle, pos=(orig[0], orig[1], orig[2], orig[3]), rot=None, rot_quat=(0, 0, 0, 0))


# making the plot from road nad the script of the vehicle
# def making_plot_road(bng, pl, main_scenario_active):
#     print("s2")
#
#     road_geometry = bng.get_road_edges('main_road')
#
#     left_edge_x = np.array([e['left'][0] for e in road_geometry])
#     left_edge_y = np.array([e['left'][1] for e in road_geometry])
#     right_edge_x = np.array([e['right'][0] for e in road_geometry])
#     right_edge_y = np.array([e['right'][1] for e in road_geometry])
#     plt.figure(figsize=(10, 10))
#     plot_road(plt.gca(), left_edge_x, left_edge_y, right_edge_x, right_edge_y)
#     plot_script(plt.gca())
#     if main_scenario_active:
#         plt.plot(pl[0], pl[1], 'r+')
#         print("main func")
#         plt.savefig("outcome/" + path + "/main.png")
#         plt.savefig("main.png")
#
#
#     else:
#         plt.plot(pl[0], pl[1], 'r+')
#         plt.plot(pl[0], pl[1] - amount, 'b+')
#         plt.savefig("outcome/" + path + "/modify.png")


def plot_road(ax, left_edge_x, left_edge_y, right_edge_x, right_edge_y):
    x_min = min(left_edge_x.min(), right_edge_x.min()) - 10  # We add/subtract 10 from the min/max coordinates to pad
    x_max = max(left_edge_x.max(), right_edge_x.max()) + 10  # the area of the plot a bit
    y_min = min(left_edge_y.min(), right_edge_y.min()) - 10
    y_max = max(left_edge_y.max(), right_edge_y.max()) + 10
    ax.set_aspect('equal', 'datalim')
    ax.set_xlim(left=x_max, right=x_min)  # pyplot & bng coordinate systems have different origins
    ax.set_ylim(bottom=y_max, top=y_min)  # so we flip them here
    ax.plot(left_edge_x, left_edge_y, 'b-')
    ax.plot(right_edge_x, right_edge_y, 'b-')


def plot_script(ax):
    ax.plot(script_x, script_y, 'y-')


# function for the main approches
def add_obstacles(road, obstacle_coordinates):
    return make_obstacle(obstacle_coordinates)


def move_obstacle(road, obstacle_coordinates, amount):
    return make_obtacle_move(road, obstacle_coordinates, amount)


def make_scenario_func(main_scenario_active):
    # call function for defining the vehicle
    making_vehicle(n_iterate, amount_of_iterate, main_scenario_active)

    # call function for defining the road
    if main_scenario_active:
        main_road = making_road(n_iterate, amount_of_iterate)
        # adding new obstacle
        obstacle_coordinates = make_obstacle_position(orig, threshold)
        object_list.append(obstacle_coordinates)
        objects = add_obstacles(main_road, obstacle_coordinates)

        # adding the vehicle into scenario
        making_vehicle(n_iterate, amount_of_iterate, main_scenario_active)
        main_scenario.add_road(main_road)
        main_scenario.add_procedural_mesh(objects)
        main_scenario.make(beamng)
        bng = beamng.open(launch=True)
        try:
            bng.load_scenario(main_scenario)
            bng.start_scenario()
            # making_plot_road(bng, obstacle_coordinates, main_scenario_active)
            # make the vehicle get auto run on the lane
            vehicle.ai_set_aggression(risk_value)
            vehicle.ai_set_speed(100, mode='limit')
            vehicle.ai_drive_in_lane(True)
            vehicle.ai_set_mode('span')
            sleep(3000)
        finally:
            bng.close()
    else:
        main_road = making_road(n_iterate, amount_of_iterate)
        obstacle_coordinates = change_obstacle_position(object_list[0], amount)

        # moving the obstacle
        moved_objects = move_obstacle(main_road, object_list[0], amount)
        making_vehicle(n_iterate, amount_of_iterate, main_scenario_active)
        modify_scenario.add_road(main_road)
        modify_scenario.add_procedural_mesh(moved_objects)
        modify_scenario.make(beamng_modify)
        bng = beamng_modify.open(launch=True)
        try:
            bng.load_scenario(modify_scenario)
            bng.start_scenario()
            print("s1")
            # making_plot_road(bng, obstacle_coordinates, main_scenario_active)

            # make the vehicle get auto run on the lane
            vehicle.ai_set_aggression(risk_value)
            vehicle.ai_set_speed(100, mode='limit')
            vehicle.ai_drive_in_lane(True)
            vehicle.ai_set_mode('span')
            sleep(30)
        finally:
            bng.close()


def executor():
    main_scenario_active = True
    make_scenario_func(main_scenario_active)
    main_scenario_active = False
    make_scenario_func(main_scenario_active)


if __name__ == '__main__':
    # os.mkdir("outcome/" + path)
    executor()
