import random

from beamngpy import BeamNGpy, Scenario, Road, Vehicle
import numpy as np
import os
import matplotlib.pyplot as plt
from datetime import datetime
from time import sleep






# defining the global variable


# defining the beamng requirments
beamng = BeamNGpy('localhost', 64256)
beamng_modify = BeamNGpy('localhost', 64256)
main_scenario = Scenario('tig', 'the main scenario of creating the bump in the road ')
modify_scenario = Scenario('tig', 'the modify version of creating the bump in the road')
vehicle = Vehicle('ego_vehicle', model='etk800')

# adding valid
bump_list = {"upper_length": random.uniform(8, 12), "upper_width": random.uniform(0, 2),
                 "width": random.uniform(2, 10), "length": random.uniform(12, 20), "height": random.uniform(0, 2)}





# defining the changable variable
risk_value = 0.7
n_iterate = 10
amount_of_iterate = 40
number_of_object = 8
orig = (0, 0, -28, 7)
threshold = (orig[0] + amount_of_iterate, orig[1] - n_iterate * amount_of_iterate, orig[0])


# making the path for generating the
path = "testing-" + str(datetime.now().date()) + "-" + str(datetime.now().time().hour) + "-" + str(datetime.now().time().minute) + "-" + str(datetime.now().time().second)



def make_txt_outcome(old_version, bump_list, index, creation):
    if creation:
        with open("outcome/" + path + "/bump_info.txt", 'x') as f:
            f.write("the bump modification default version is "
                    + "\n" + "upper_width = " + str(bump_list["upper_width"])
                    + "\n" + "upper_length = " + str(bump_list["upper_length"])
                    + "\n" + "width = " + str(bump_list["width"])
                    + "\n" + "length = " + str(bump_list["length"])
                    + "\n" + "height = " + str(bump_list["height"]) + "\n\n"
                    )

    else:
        with open("outcome/"+path+"/bump_info.txt", 'a') as f:
            f.write("main " + str(index) + " is = " + str(old_version) + "\n" +
                    "amount of changing is  = " + str(bump_list[index] - old_version ) + "\n" +
                    "modify " + str(index) + " is = " + str(bump_list[index])+ "\n\n")






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


# defining the vehicle
def making_bump(main_scenario_active, bng, bump_lists):
    # adding the Vehicle

    if main_scenario_active:

        i = 1
        while i < n_iterate:
            bng.create_bump(name="bump", upper_length=bump_lists["upper_length"], upper_width=bump_lists["upper_width"],
                            rot=(0, 0, 100, 0),
                            pos=(orig[0] + ((i % 2) * amount_of_iterate), orig[1] - i * amount_of_iterate, orig[2]),
                            width=bump_lists["width"], length=bump_lists["length"], height=bump_lists["height"],
                            material="track_editor_C_center")
            i = i + 1

    else:
        i = 1
        while i < n_iterate:
            bng.create_bump(name="bump", upper_length=bump_lists["upper_length"],
                             upper_width=bump_lists["upper_width"], rot=(0, 0, 100, 0),
                             pos=(orig[0] + ((i % 2) * amount_of_iterate), orig[1] - i * amount_of_iterate, orig[2]),
                             width=bump_lists["width"], length=bump_lists["length"], height=bump_lists["height"],
                             material="track_editor_C_center")
            i = i + 1






def make_scenario_func(main_scenario_active, bump_lists):
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



        try:
            bng.load_scenario(main_scenario)



            # starting the scenario
            bng.start_scenario()

            making_bump(main_scenario_active, bng, bump_lists)
            #simple sxample which is valid
            # ######
            # i = 1
            # while i < n_iterate:
            #     bng.create_bump(name="bump", upper_length=10, upper_width=3,  rot=(0, 0, 100, 0),
            #                     pos=(orig[0] + ((i % 2) * amount_of_iterate), orig[1] - i * amount_of_iterate, orig[2]), width=10, length=20, height=3,
            #                     material="track_editor_C_center")
            #     i = i + 1
            #
            # #####


            # setting the lane keeping Assist system on
            vehicle.ai_set_aggression(risk_value)
            vehicle.ai_set_speed(100, mode='limit')
            vehicle.ai_drive_in_lane(True)
            vehicle.ai_set_mode('span')

            # how much time the simulation works
            sleep(40)
        finally:
            bng.close()
            return bump_lists

    else:
        bng2 = beamng_modify.open(launch=True)

        main_road = making_road(n_iterate, amount_of_iterate)
        making_vehicle(n_iterate, amount_of_iterate, main_scenario_active)
        modify_scenario.add_road(main_road)
        modify_scenario.make(beamng_modify)

        try:
            bng2.load_scenario(modify_scenario)
            bng2.start_scenario()
            making_bump(main_scenario_active, bng2, bump_lists)

            # setting the lane keeping Assist system on
            vehicle.ai_set_aggression(risk_value)
            vehicle.ai_set_speed(100, mode='limit')
            vehicle.ai_drive_in_lane(True)
            vehicle.ai_set_mode('span')

            # how much time the simulation works
            sleep(40)
        finally:
            bng2.close()
            return bump_lists


def change_bump_list(bl, i):

    if i == "upper_length":
        print("old " + i +" was =" +str(bl[i]))
        old_version = bl[i]
        bl["upper_length"] = random.choice(
            [random.uniform(10, bl["upper_length"]), random.uniform(bl["upper_length"], 20)])
        print("new " + i + " was =" + str(bl[i]))

        return bl,old_version
    elif i == "upper_width":
        print("old " + i + " was =" + str(bl[i]))
        old_version = bl[i]
        bl["upper_width"] = random.choice(
            [random.uniform(0, bl["upper_width"]), random.uniform(bl["upper_width"], 10)])
        print("new " + i + " was =" + str(bl[i]))
        return bl, old_version
    elif i == "width":
        print("old " + i + " was =" + str(bl[i]))
        old_version = bl[i]
        bl["width"] = random.choice(
            [random.uniform(0, bl["width"]), random.uniform(bl["width"], 10)])
        print("new " + i + " was =" + str(bl[i]))
        return bl, old_version
    elif i == "length":
        print("old " + i + " was =" + str(bl[i]))
        old_version = bl[i]
        bl["length"] = random.choice(
            [random.uniform(10, bl["length"]), random.uniform(bl["length"], 20)])
        print("new " + i + " was =" + str(bl[i]))
        return bl, old_version
    elif i == "height":
        print("old " + i + " was =" + str(bl[i]))
        old_version = bl[i]
        bl["height"] = random.choice(
            [random.uniform(0, bl["height"]), random.uniform(bl["height"], 10)])
        print("new " + i + " was =" + str(bl[i]))
        return bl, old_version


def executor():
    main_scenario_active = True
    bump_lists =make_scenario_func(main_scenario_active, bump_list)
    main_scenario_active = False
    make_txt_outcome(0, bump_list, "", True)
    for i in ["height", "upper_length", "upper_width", "width", "length"]:
        j = 0
        while j < 3:
            bump_list_new, old_version = change_bump_list(bump_list, i)
            bump_list_modification = make_scenario_func(main_scenario_active, bump_list_new)
            j = j + 1
            make_txt_outcome(old_version, bump_list_modification, i, False)
            bump_list[i] = old_version



if __name__ == '__main__':
    os.mkdir("outcome/"+path)
    executor()
