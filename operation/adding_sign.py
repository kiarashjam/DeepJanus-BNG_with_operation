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

# defining the changable variable
risk_value = 0.7
n_iterate = 10
amount_of_iterate = 40
number_of_object = 8
orig = (0, 0, -28, 7)
amount = 10
threshold = (orig[0] + amount_of_iterate, orig[1] + n_iterate * amount_of_iterate, orig[0])

# # making the path for generating the
# path = "testing-" + str(datetime.now().date()) + "-" + str(datetime.now().time().hour) + "-" + str(
#     datetime.now().time().minute) + "-" + str(datetime.now().time().second)

# the list
list_of_signs = ["sign_weightlimit.dae","sign_tractor.dae","sign_stop.dae", "sign_south.dae", "sign_route1.dae", "sign_route2.dae",
                 "sign_north.dae", "sign_dip.dae", "sign_bump.dae", "sign_2way.dae", "sign_4way.dae",
                 "sign_bend_left.dae", "sign_bend_right.dae", "sign_gravel.dae"]









# making the road
def making_road(n, ei):
    # adding the Road and the lines
    road_main = Road('tig_road_rubber_sticky', rid='main_road', drivability=1, texture_length=5, interpolate=True)

    i = 0
    while i < n:
        nodes_main_road = [
            (orig[0] + ((i % 2) * ei), orig[1] + i * ei, orig[2], 10),
        ]
        # adding the roads
        road_main.nodes.extend(nodes_main_road)
        i = i + 1
    return road_main


# defining the vehicle
def making_vehicle(n, ei, main_scenario_active):
    # adding the Vehicle

    if main_scenario_active:
        main_scenario.add_vehicle(vehicle, pos=(orig[0], orig[1], orig[2]), rot=(-10,0,0), rot_quat=(0, 0, 0, 0))
    else:
        modify_scenario.add_vehicle(vehicle, pos=(orig[0], orig[1], orig[2]), rot=(1,1,0), rot_quat=(0, 0, 0, 0))

def making_sign_edges(roads_edges,type):
    i = 0
    for road_edge in roads_edges:
        sign = StaticObject(name="sign_right" + str(i) , pos=(road_edge["right"]),
                             rot=(0, 0, 0), scale=(1, 1, 1),
                             shape='/levels/tig/art/shapes/signs/'+random.choice(list_of_signs), rot_quat=None)
        sign2 = StaticObject(name="sign_left" + str(i), pos=(road_edge["left"]),
                            rot=(0, 0, 0), scale=(1, 1, 1),
                            shape='/levels/tig/art/shapes/signs/'+random.choice(list_of_signs), rot_quat=None)
        if type == "main":
            print(i)

            main_scenario.add_object(sign)
            main_scenario.add_object(sign2)
        elif type == "modification":
            modify_scenario.add_object(sign)
            modify_scenario.add_object(sign2)
        i = i +1






def make_scenario_func(main_scenario_active):
    # call function for defining the vehicle
    making_vehicle(n_iterate, amount_of_iterate, main_scenario_active)

    # call function for defining the road
    if main_scenario_active:
        main_road = making_road(n_iterate, amount_of_iterate)
        # adding the vehicle into scenario
        making_vehicle(n_iterate, amount_of_iterate, main_scenario_active)
        main_scenario.add_road(main_road)
        main_scenario.make(beamng)

        print("s")


        bng = beamng.open(launch=True)
        try:
            bng.load_scenario(main_scenario)
            bng.start_scenario()
            list_road_edges = beamng.get_road_edges("main_road")
            making_sign_edges(list_road_edges, "main")
            sleep(1)
        finally:
            bng.close()
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
            sleep(60)
        finally:
            bng.close()
    else:
        main_road = making_road(n_iterate, amount_of_iterate)
        amount_of_rocks= random.randint(200, 2000)


        # moving the obstacle
        making_vehicle(n_iterate, amount_of_iterate, main_scenario_active)
        modify_scenario.add_road(main_road)
        modify_scenario.make(beamng_modify)
        bng2 = beamng_modify.open(launch=True)
        try:
            bng2.load_scenario(modify_scenario)
            list_road_edges = bng2.get_road_edges("main_road")
            making_sign_edges(list_road_edges, "modification")
            bng2.start_scenario()



            # make the vehicle get auto run on the lane
            vehicle.ai_set_aggression(risk_value)
            vehicle.ai_set_speed(100, mode='limit')
            vehicle.ai_drive_in_lane(True)
            vehicle.ai_set_mode('span')
            sleep(30)
        finally:
            bng2.close()


def executor():
    main_scenario_active = True
    make_scenario_func(main_scenario_active)
    main_scenario_active = False
    make_scenario_func(main_scenario_active)


if __name__ == '__main__':


    executor()
