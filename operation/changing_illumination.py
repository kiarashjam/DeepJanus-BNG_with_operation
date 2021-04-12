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





# defining the global variable


# defining the beamng requirments
beamng = BeamNGpy('localhost', 64256)
beamng_modify = BeamNGpy('localhost', 64256)
main_scenario = Scenario('tig', 'the main scenario ')
modify_scenario = Scenario('tig', 'changing the illumination of the scenario')
vehicle = Vehicle('ego_vehicle', model='etk800')



# defining the changable variable
risk_value = 0.7
n_iterate = 10
amount_of_iterate = 40
number_of_object = 8
orig = (0, 0, -28, 7)
threshold = (orig[0] + amount_of_iterate, orig[1] - n_iterate * amount_of_iterate, orig[0])


# making the path for generating the
path = "testing-" + str(datetime.now().date()) + "-" + str(datetime.now().time().hour) + "-" + str(datetime.now().time().minute) + "-" + str(datetime.now().time().second)



def make_txt_outcome(brightness,amount_of_change,change_brighness):
    with open("outcome/"+path+"/illumination_info.txt", 'x') as f:
        f.write("main brightness is = " + str(brightness) + "\n" +
                "amount of changing is  = " + str(amount_of_change)+"\n" +
                "modify brightness is = " + str(change_brighness))


# defining the obstacle position
def main_illumination():
    brightness = random.uniform(0 , 1)
    return brightness

# get the new position for the object
def change_illumination(brightness , first_amount,second_amount):

    # this is the choice between the amount higher than brightness or less than the main brightness
    choice = random.choice([True, False])

    # with the choice it it will save the data in txt file by calling make_txt_outcome function and also, it returnsZZZZZ the modify brightness
    if choice:
        print("main brightness is = " + str(brightness))
        print("amount of changing is  = " + str(brightness - first_amount))
        make_txt_outcome(brightness,brightness - first_amount, first_amount)
        return first_amount
    else:
        print("main brightness  = " + str(brightness))
        print("amount of changing is  = " + str(second_amount - brightness))
        make_txt_outcome(brightness, second_amount - brightness , second_amount)
        return second_amount






# making the road
def making_road(n, ei):
    # adding the Road and the lines
    road_main = Road('tig_road_rubber_sticky',rid='main_road',drivability=1,texture_length =5, interpolate = True)

    i = 0
    while i < n:
        nodes_main_road = [
            (orig[0] + ((i%2) * ei) , orig[1] - i*ei , orig[2], 10),
        ]
        # adding the roads
        road_main.nodes.extend(nodes_main_road)
        i = i + 1
    return road_main



# defining the vehicle
def making_vehicle(n,ei,main_scenario_active):
    # adding the Vehicle

    if main_scenario_active:

        main_scenario.add_vehicle(vehicle, pos=(orig[0],orig[1],orig[2],orig[3]), rot=None, rot_quat=(0, 0, 0, 0))
    else:
        modify_scenario.add_vehicle(vehicle, pos=(orig[0],orig[1],orig[2],orig[3]), rot=None, rot_quat=(0, 0, 0, 0))







def make_scenario_func(main_scenario_active, main_brightness):
    # call function for defining the vehicle
    making_vehicle(n_iterate, amount_of_iterate,main_scenario_active)

    # call function for defining the road
    if main_scenario_active:
        bng = beamng.open(launch=True)

        main_road = making_road(n_iterate, amount_of_iterate)
        # adding the vehicle into scenario
        making_vehicle(n_iterate, amount_of_iterate, main_scenario_active)
        main_scenario.add_road(main_road)
        main_scenario.make(beamng)

        # adding the main  illumination
        brightness = main_illumination()

        try:
            bng.load_scenario(main_scenario)



            # starting the scenario
            bng.start_scenario()
            bng.set_tod(brightness)

            # make the vehicle get auto run on the lane
            if 0.22 < brightness < 0.75:
                vehicle.set_lights(headlights=2)

            # setting the lane keeping Assist system on
            vehicle.ai_set_aggression(risk_value)
            vehicle.ai_set_speed(100, mode='limit')
            vehicle.ai_drive_in_lane(True)
            vehicle.ai_set_mode('span')

            # how much time the simulation works
            sleep(10)
        finally:
            bng.close()
            return brightness
    else:
        bng2 = beamng_modify.open(launch=True)

        main_road = making_road(n_iterate, amount_of_iterate)
        making_vehicle(n_iterate, amount_of_iterate, main_scenario_active)
        modify_scenario.add_road(main_road)
        modify_scenario.make(beamng_modify)


        # modification of  the illumination
        brightness = change_illumination(main_brightness, random.uniform(0, main_brightness), random.uniform(main_brightness,1))

        try:
            bng2.load_scenario(modify_scenario)
            bng2.start_scenario()

            # set the brightness with the modification amount
            bng2.set_tod(brightness)

            # if the time was in the night, the car turn oon the headlight
            if 0.2 < brightness < 0.75:
                vehicle.set_lights(headlights=2)

            # setting the lane keeping Assist system on
            vehicle.ai_set_aggression(risk_value)
            vehicle.ai_set_speed(100, mode='limit')
            vehicle.ai_drive_in_lane(True)
            vehicle.ai_set_mode('span')

            # how much time the simulation works
            sleep(10)
        finally:
            bng2.close()
            return brightness


def executor():
    main_scenario_active = True
    main_brighness =make_scenario_func(main_scenario_active, 0)
    main_scenario_active = False
    change_brighness = make_scenario_func(main_scenario_active, main_brighness)
    print("modify brightness is = " + str(change_brighness))

if __name__ == '__main__':
    os.mkdir("outcome/"+path)
    executor()