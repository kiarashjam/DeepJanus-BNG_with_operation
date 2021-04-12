import random
from math import sqrt

from beamngpy import BeamNGpy, Scenario, Road, Vehicle, setup_logging, ProceduralCube ,StaticObject , ScenarioObject
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




def making_rocks_main(number_of_rocks, type):


    amount_in_every_axis = int(sqrt(number_of_rocks / n_iterate))
    distance = float(amount_of_iterate+20) / amount_in_every_axis

    i = 1
    while i < amount_in_every_axis * (n_iterate):
        j = 1
        while j < amount_in_every_axis:

            print("make the one rock in postion x = " + str(j*distance)+ "  y  =" + str(i * distance) )
            rock = StaticObject( name= "rock" + str(i) + "_" +str(j) ,pos=(j*distance,  -i * distance, orig[2]), rot=(0, 0, 0), scale=(0.3, 0.3, 0.05),
                             shape='/levels/tig/art/shapes/rocks/wca_rock1.dae', rot_quat=None)
            if type == "main":
                main_scenario.add_object(rock)
            elif type == "modification":
                modify_scenario.add_object(rock)
            j = j + 1
        i = i + 1


def make_scenario_func(main_scenario_active):
    # call function for defining the vehicle
    making_vehicle(n_iterate, amount_of_iterate, main_scenario_active)

    # call function for defining the road
    if main_scenario_active:
        main_road = making_road(n_iterate, amount_of_iterate)
        amount_of_rocks = random.randint(1000, 2000)
        # adding the vehicle into scenario
        making_vehicle(n_iterate, amount_of_iterate, main_scenario_active)

        main_scenario.add_road(main_road)
        making_rocks_main(amount_of_rocks, "main")
        main_scenario.make(beamng)
        bng = beamng.open(launch=True)
        try:
            bng.load_scenario(main_scenario)
            bng.start_scenario()

            # make the vehicle get auto run on the lane
            vehicle.ai_set_aggression(risk_value)
            vehicle.ai_set_speed(100, mode='limit')
            vehicle.ai_drive_in_lane(True)
            vehicle.ai_set_mode('span')
            sleep(30)
        finally:
            bng.close()
    else:
        main_road = making_road(n_iterate, amount_of_iterate)
        amount_of_rocks= random.randint(2000, 20000)


        # moving the obstacle
        making_vehicle(n_iterate, amount_of_iterate, main_scenario_active)
        modify_scenario.add_road(main_road)
        making_rocks_main(amount_of_rocks, "modification")
        modify_scenario.make(beamng_modify)
        bng = beamng_modify.open(launch=True)
        try:
            bng.load_scenario(modify_scenario)
            bng.start_scenario()


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
    os.mkdir("outcome/" + path)
    executor()
