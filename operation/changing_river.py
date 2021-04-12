import random
import shutil

from beamngpy import BeamNGpy, Scenario, Road, Vehicle, setup_logging, ProceduralCube
import numpy as np
import os
import matplotlib.pyplot as plt
from datetime import datetime, time
from time import sleep
import json

# defining the global variable



## wind default variable
default_wind_speed = 0.2000000029802322
default_coverage_cloud = 0
default_shadowSoftness = 0.2000000029802322
default_fogScale = [0.6941180229187012, 0.8549020290374756, 0.992156982421875, 1]
default_colorize = [0.4235289990901947, 0.6078429818153381, 0.8666669726371765, 1]
default_ambientScale = [0.5450980067253113, 0.5450980067253113, 0.549019992351532, 1]
default_sunScale = [0.9960780143737793, 0.9019610285758972, 0.8313729763031006, 1]



## fog default variables
default_fog_height = 800
default_fog_density = 0.0006000000284984708
default_fog_visible_distance = 45000

## brightness sky default variable

default_brightness_sky = 11
default_time_brightness = 0.1000000014901161

## sky default variables


## rain default variable =
default_drop_size = 0.0799999982
default_max_Speed =0.4
default_num_of_drops = 0
default_max_mass = 0.5




# defining the beamng requirments
beamng = BeamNGpy('localhost', 64256)
beamng_modify = BeamNGpy('localhost', 64256)
main_scenario = Scenario('tig', 'the main scenario ')
modify_scenario = Scenario('tig', 'changing the rivers inside  the scenario')
vehicle = Vehicle('ego_vehicle', model='etk800')



# defining the changable variable
risk_value = 0.7
n_iterate = 10
amount_of_iterate = 40
number_of_object = 8
orig = (0, 0, -28, 7)
threshold = (orig[0] + amount_of_iterate, orig[1] - n_iterate * amount_of_iterate, orig[0])

# making the path for generating the
path = "testing-" + str(datetime.now().date()) + "-" + str(datetime.now().time().hour) + "-" + str(
    datetime.now().time().minute) + "-" + str(datetime.now().time().second)

class MapFolder:
    def __init__(self, path):
        self.path = path
    def delete_all_map(self):
        shutil.rmtree(self.path, ignore_errors=True)
        # sometimes rmtree fails to remove files
        for tries in range(20):
            if os.path.exists(self.path):
                time.sleep(0.1)
                shutil.rmtree(self.path, ignore_errors=True)
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
class LevelsFolder:
    def __init__(self, path):
        self.path = os.path.realpath(path)
    def get_map(self, map_name: str):
        return MapFolder(os.path.join(self.path, map_name))

class Maps:
    beamng_map: MapFolder
    source_map: MapFolder

    def __init__(self):
        self.beamng_levels = LevelsFolder(os.path.join(os.environ['USERPROFILE'], r'Documents/BeamNG.research/levels'))
        self.source_levels = LevelsFolder(os.getcwd()+'/levels_2')
        self.source_levels_default = LevelsFolder(os.getcwd() + '/levels')
        self.source_map = self.source_levels.get_map('tig')
        self.source_map_default = self.source_levels_default.get_map('tig')
        self.beamng_map = self.beamng_levels.get_map('tig')
        self.never_logged_path = True
        self.beamng_map.delete_all_map()
    def install_map(self,type):
        if self.never_logged_path:
            self.never_logged_path = False
        if type == "modification":
            print(f'Copying from [{self.source_map.path}] to [{self.beamng_map.path}]')
            self.beamng_map.delete_all_map()
            shutil.copytree(src=self.source_map.path, dst=self.beamng_map.path)
        if type == "default":
            print(f'Copying from [{self.source_map_default.path}] to [{self.beamng_map.path}]')
            self.beamng_map.delete_all_map()
            shutil.copytree(src=self.source_map_default.path, dst=self.beamng_map.path)




# making the road
def making_road(n, ei):

    # adding the Road
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
def making_vehicle(main_scenario_active):

    # adding the Vehicle
    if main_scenario_active:
        main_scenario.add_vehicle(vehicle, pos=(orig[0], orig[1], orig[2], orig[3]), rot=None, rot_quat=(0, 0, 0, 0))
    else:
        modify_scenario.add_vehicle(vehicle, pos=(orig[0], orig[1], orig[2], orig[3]), rot=None, rot_quat=(0, 0, 0, 0))


def make_scenario_func(main_scenario_active):

    # call function for defining the road
    if main_scenario_active:
        bng = beamng.open(launch=True)

        main_road = making_road(n_iterate, amount_of_iterate)
        # adding the vehicle into scenario
        making_vehicle(main_scenario_active)
        main_scenario.add_road(main_road)
        main_scenario.make(beamng)

        try:
            bng.load_scenario(main_scenario)
            bng.start_scenario()

            # setting the lane keeping Assist system on
            vehicle.ai_set_aggression(risk_value)
            vehicle.ai_set_speed(100, mode='limit')
            vehicle.ai_drive_in_lane(True)
            vehicle.ai_set_mode('span')

            # how much time the simulation works
            sleep(20)
        finally:
            bng.close()
    else:
        bng2 = beamng_modify.open(launch=True)

        main_road = making_road(n_iterate, amount_of_iterate)
        making_vehicle(main_scenario_active)
        modify_scenario.add_road(main_road)
        modify_scenario.make(beamng_modify)


        try:
            bng2.load_scenario(modify_scenario)
            bng2.start_scenario()

            # setting the lane keeping Assist system on
            vehicle.ai_set_aggression(risk_value)
            vehicle.ai_set_speed(100, mode='limit')
            vehicle.ai_drive_in_lane(True)
            vehicle.ai_set_mode('span')

            # how much time the simulation works
            sleep(20)
        finally:
            bng2.close()


def executor(main_scenario_active):
    make_scenario_func(main_scenario_active)

global maps
maps = Maps()



def default_river():

  string_version_of_json=""
  with open('levels_2/tig/main/MissionGroup/sky_and_sun/items.level.json') as f:
    list_jasons=f.readlines()
  json_version=list()
  for js in list_jasons:
    json_version.append(json.loads(js))
  i = 0

  while i < len(json_version):
      if json_version[i]["name"] == "river1":
          json_version[i]["overallFoamOpacity"] = 3
      elif json_version[i]["name"] == "river2":
          json_version[i]["overallFoamOpacity"] = 3
      elif json_version[i]["name"] == "river3":
          json_version[i]["overallFoamOpacity"] = 3
      elif json_version[i]["name"] == "river4":
          json_version[i]["overallFoamOpacity"] = 3
      elif json_version[i]["name"] == "river5":
          json_version[i]["overallFoamOpacity"] = 3
      elif json_version[i]["name"] == "river6":
          json_version[i]["overallFoamOpacity"] = 3
      elif json_version[i]["name"] == "river7":
          json_version[i]["overallFoamOpacity"] = 3
      elif json_version[i]["name"] == "river8":
          json_version[i]["overallFoamOpacity"] = 3
      elif json_version[i]["name"] == "river9":
          json_version[i]["overallFoamOpacity"] = 3
      elif json_version[i]["name"] == "river10":
          json_version[i]["overallFoamOpacity"] = 3
      elif json_version[i]["name"] == "river11":
          json_version[i]["overallFoamOpacity"] = 3
      elif json_version[i]["name"] == "river12":
          json_version[i]["overallFoamOpacity"] = 3
      i = i + 1

  while i < len(json_version):
      if json_version[i]["name"] == "river1":
          json_version[i]["overallRippleMagnitude"] = 1
      elif json_version[i]["name"] == "river2":
          json_version[i]["overallRippleMagnitude"] = 1
      elif json_version[i]["name"] == "river3":
          json_version[i]["overallRippleMagnitude"] = 1
      elif json_version[i]["name"] == "river4":
          json_version[i]["overallRippleMagnitude"] = 1
      elif json_version[i]["name"] == "river5":
          json_version[i]["overallRippleMagnitude"] = 1
      elif json_version[i]["name"] == "river6":
          json_version[i]["overallRippleMagnitude"] = 1
      elif json_version[i]["name"] == "river7":
          json_version[i]["overallRippleMagnitude"] = 1
      elif json_version[i]["name"] == "river8":
          json_version[i]["overallRippleMagnitude"] = 1
      elif json_version[i]["name"] == "river9":
          json_version[i]["overallRippleMagnitude"] = 1
      elif json_version[i]["name"] == "river10":
          json_version[i]["overallRippleMagnitude"] = 1
      elif json_version[i]["name"] == "river11":
          json_version[i]["overallRippleMagnitude"] = 1
      elif json_version[i]["name"] == "river12":
          json_version[i]["overallRippleMagnitude"] = 1
      i = i + 1

  i=0
  while i < len(json_version):
    if i == 0:
      string_version_of_json = str(json.dumps(json_version[i]))
    else:
      string_version_of_json = string_version_of_json +"\n"+ str(json.dumps(json_version[i]))
    i = i + 1
  writing_json_in_file(string_version_of_json)
  maps.install_map("default")


def modification_river(amount,type):
  string_version_of_json = ""
  with open('levels_2/tig/main/MissionGroup/sky_and_sun/items.level.json') as f:
    list_jasons = f.readlines()
  json_version = list()
  for js in list_jasons:
    json_version.append(json.loads(js))
  i = 0
  if type == "foam":
      while i < len(json_version):
        if json_version[i]["name"] =="river1":
            json_version[i]["overallFoamOpacity"] = amount
        elif json_version[i]["name"] == "river2":
            json_version[i]["overallFoamOpacity"] = amount
        elif json_version[i]["name"] == "river3":
            json_version[i]["overallFoamOpacity"] = amount
        elif json_version[i]["name"] == "river4":
            json_version[i]["overallFoamOpacity"] = amount
        elif json_version[i]["name"] == "river5":
            json_version[i]["overallFoamOpacity"] = amount
        elif json_version[i]["name"] == "river6":
            json_version[i]["overallFoamOpacity"] = amount
        elif json_version[i]["name"] == "river7":
            json_version[i]["overallFoamOpacity"] = amount
        elif json_version[i]["name"] == "river8":
            json_version[i]["overallFoamOpacity"] = amount
        elif json_version[i]["name"] == "river9":
            json_version[i]["overallFoamOpacity"] = amount
        elif json_version[i]["name"] == "river10":
            json_version[i]["overallFoamOpacity"] = amount
        elif json_version[i]["name"] == "river11":
            json_version[i]["overallFoamOpacity"] = amount
        elif json_version[i]["name"] == "river12":
            json_version[i]["overallFoamOpacity"] = amount
        i = i + 1
  if type == "foam":
      while i < len(json_version):
        if json_version[i]["name"] =="river1":
            json_version[i]["overallRippleMagnitude"] = amount
        elif json_version[i]["name"] == "river2":
            json_version[i]["overallRippleMagnitude"] = amount
        elif json_version[i]["name"] == "river3":
            json_version[i]["overallRippleMagnitude"] = amount
        elif json_version[i]["name"] == "river4":
            json_version[i]["overallRippleMagnitude"] = amount
        elif json_version[i]["name"] == "river5":
            json_version[i]["overallRippleMagnitude"] = amount
        elif json_version[i]["name"] == "river6":
            json_version[i]["overallRippleMagnitude"] = amount
        elif json_version[i]["name"] == "river7":
            json_version[i]["overallRippleMagnitude"] = amount
        elif json_version[i]["name"] == "river8":
            json_version[i]["overallRippleMagnitude"] = amount
        elif json_version[i]["name"] == "river9":
            json_version[i]["overallRippleMagnitude"] = amount
        elif json_version[i]["name"] == "river10":
            json_version[i]["overallRippleMagnitude"] = amount
        elif json_version[i]["name"] == "river11":
            json_version[i]["overallRippleMagnitude"] = amount
        elif json_version[i]["name"] == "river12":
            json_version[i]["overallRippleMagnitude"] = amount
        i = i + 1

  i = 0
  while i < len(json_version):
    if i == 0:
      string_version_of_json = str(json.dumps(json_version[i]))
    else:
      string_version_of_json = string_version_of_json +"\n"+ str(json.dumps(json_version[i]))
    i = i + 1
  writing_json_in_file_river(string_version_of_json)
  maps.install_map("modification")




def writing_json_in_file_river(string_version_of_json):
    text_file = open('levels/tig/main/MissionGroup/sky_and_sun/items.level.json', 'w')
    text_file.write(string_version_of_json)
    text_file.close()


def run(type):

    default_river()
    amount_main = random.randint(0, 2)
    modification_river(amount_main,type)
    executor(True)
    if type == "foam":
        amount_modification = random.randint(10, 20)
    elif type == "ripple":
        amount_modification = random.randint(6, 3000)
    modification_river(amount_modification, type)
    executor(False)
    make_txt_outcome(type, amount_main, amount_modification - amount_main, amount_modification)
    default_river()


def make_txt_outcome(type,main_value,amount_of_change,modify_value):
    with open("outcome/"+path+"/river_changes.txt", 'x') as f:
        f.write("changing the river amount in type  = " + str(type) + "\n" +
                "main amount of " + str(type) + " is = " + str(main_value) + "\n" +
                "amount of changing is  = " + str(amount_of_change)+"\n" +
                "modify amount of " + str(type) + " is = " + str(modify_value)+"\n")




if __name__ == '__main__':
    os.mkdir("outcome/"+path)
    run("foam")
