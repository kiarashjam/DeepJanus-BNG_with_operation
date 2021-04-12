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
modify_scenario = Scenario('tig', 'changing the weather of the scenario')
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
        self.source_levels = LevelsFolder(os.getcwd()+'/levels')
        self.source_map = self.source_levels.get_map('tig')
        self.beamng_map = self.beamng_levels.get_map('tig')
        self.never_logged_path = True
        self.beamng_map.delete_all_map()
    def install_map(self):
        if self.never_logged_path:
            self.never_logged_path = False
        print(f'Copying from [{self.source_map.path}] to [{self.beamng_map.path}]')
        self.beamng_map.delete_all_map()
        shutil.copytree(src=self.source_map.path, dst=self.beamng_map.path)



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
            sleep(10)
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
            sleep(10)
        finally:
            bng2.close()


def executor(main_scenario_active):
    make_scenario_func(main_scenario_active)

global maps
maps = Maps()



def default_weather():

  string_version_of_json=""
  with open('levels/tig/main/MissionGroup/sky_and_sun/items.level.json') as f:
    list_jasons=f.readlines()
  json_version=list()
  for js in list_jasons:
    json_version.append(json.loads(js))
  i = 0
  while i<len(json_version):

    if json_version[i]["class"] == "Precipitation":
        json_version[i]["numDrops"] = default_num_of_drops
        # json_version[i]["maxSpeed"] = default_max_Speed
        # json_version[i]["maxMass"] = default_max_mass
        # json_version[i]["dropSize"] = default_drop_size
    elif json_version[i]["class"] == "CloudLayer":
        json_version[i]["coverage"] = default_coverage_cloud
        # json_version[i]["windSpeed"] = default_wind_speed
    elif json_version[i]["class"] == "LevelInfo":
        json_version[i]["fogDensity"] = default_fog_density
    elif json_version[i]["class"] == "ScatterSky":
        json_version[i]["shadowSoftness"] = default_shadowSoftness
        json_version[i]["colorize"] = default_colorize
        json_version[i]["ambientScale"] = default_ambientScale
        json_version[i]["sunScale"] = default_sunScale
        json_version[i]["fogScale"] = default_fogScale

    i=i+1
  i=0
  while i < len(json_version):
    if i == 0:
      string_version_of_json = str(json.dumps(json_version[i]))
    else:
      string_version_of_json = string_version_of_json +"\n"+ str(json.dumps(json_version[i]))
    i = i + 1
  writing_json_in_file(string_version_of_json)
  maps.install_map()


def modification_fog(fog_density):
  string_version_of_json = ""
  with open('levels/tig/main/MissionGroup/sky_and_sun/items.level.json') as f:
    list_jasons = f.readlines()
  json_version = list()
  for js in list_jasons:
    json_version.append(json.loads(js))
  i = 0
  while i < len(json_version):
    if json_version[i]["class"] =="LevelInfo":
        json_version[i]["fogDensity"] = fog_density
    elif json_version[i]["class"] == "CloudLayer":
        json_version[i]["coverage"] = 1
    elif json_version[i]["class"] == "ScatterSky":
        json_version[i]["shadowSoftness"] = 1
        json_version[i]["colorize"] = [0.427451, 0.427451, 0.427451, 1]
        json_version[i]["ambientScale"] = [0.545098, 0.545098, 0.54902, 1]
        json_version[i]["sunScale"] = [0.686275, 0.686275, 0.686275, 1]
        json_version[i]["fogScale"] = [0.756863, 0.760784, 0.760784, 1]
    i = i + 1
  i = 0
  while i < len(json_version):
    if i == 0:
      string_version_of_json = str(json.dumps(json_version[i]))
    else:
      string_version_of_json = string_version_of_json +"\n"+ str(json.dumps(json_version[i]))
    i = i + 1
  writing_json_in_file(string_version_of_json)
  maps.install_map()



def modification_rain(num_drops):
    string_version_of_json = ""
    with open('levels/tig/main/MissionGroup/sky_and_sun/items.level.json') as f:
      list_jasons = f.readlines()
    json_version = list()
    for js in list_jasons:
      json_version.append(json.loads(js))
    i = 0
    while i < len(json_version):
        if json_version[i]["class"] == "LevelInfo":
            json_version[i]["fogDensity"] = 0.02
        elif json_version[i]["class"] == "Precipitation":
            json_version[i]["numDrops"] = num_drops
        elif json_version[i]["class"] == "CloudLayer":
            json_version[i]["coverage"] = 1
        elif json_version[i]["class"] == "ScatterSky":
            json_version[i]["shadowSoftness"] = 1
            json_version[i]["colorize"] = [0.427451, 0.427451, 0.427451, 1]
            json_version[i]["ambientScale"] = [0.545098, 0.545098, 0.54902, 1]
            json_version[i]["sunScale"] = [0.686275, 0.686275, 0.686275, 1]
            json_version[i]["fogScale"] = [0.756863, 0.760784, 0.760784, 1]
        i = i + 1
    i = 0
    while i < len(json_version):
      if i == 0:
        string_version_of_json = str(json.dumps(json_version[i]))
      else:
        string_version_of_json = string_version_of_json + "\n" + str(json.dumps(json_version[i]))
      i = i + 1
    writing_json_in_file(string_version_of_json)
    maps.install_map()








def modification_wind():
  string_version_of_json =" "
  with open('levels/tig/main/MissionGroup/sky_and_sun/items.level.json') as f:
    list_jasons = f.readlines()
  json_version=list()
  for js in list_jasons:
    json_version.append(json.loads(js))
  i = 0
  while i < len(json_version):
    if json_version[i]["name"] == "clouds" or json_version[i]["name"] == "clouds1":

      json_version[i]["windSpeed"] = 500
    i = i+1
  i=0
  while i < len(json_version):
    if i == 0:
      string_version_of_json = str(json.dumps(json_version[i]))
    else:
      string_version_of_json = string_version_of_json +"\n"+ str(json.dumps(json_version[i]))
    i = i + 1
  writing_json_in_file(string_version_of_json)
  maps.install_map()



def writing_json_in_file(string_version_of_json):
    text_file = open('levels/tig/main/MissionGroup/sky_and_sun/items.level.json', 'w')
    text_file.write(string_version_of_json)
    text_file.close()


def run(type):
    default_weather()
    if type == "fog":
        amount_fog_main = random.uniform(0, 1)
        modification_fog(amount_fog_main)
        executor(True)
        amount_fog_modification = random.choice([random.uniform(0, amount_fog_main), random.uniform(amount_fog_main, 1)])
        modification_fog(amount_fog_modification)
        executor(False)
        make_txt_outcome(type, amount_fog_main,amount_fog_modification - amount_fog_main, amount_fog_modification)
        default_weather()
    # elif type == "wind":
    #     modification_wind()
    #     maps.install_map()
    #     generate()
    #     default_weather()
    if type == "rain":
        amount_of_rain = random.randint(0, 10000)
        modification_rain(amount_of_rain)
        executor(True)
        amount_rain_modification = random.choice(
            [random.randint(0, amount_of_rain), random.randint(amount_of_rain, 10000)])
        print("amount of modification is "+str(amount_rain_modification))
        modification_rain(amount_rain_modification)
        executor(False)
        make_txt_outcome(type, amount_of_rain,amount_rain_modification - amount_of_rain , amount_rain_modification)
        default_weather()
    # if type =="storm":
    #     # modification_brightness()
    #     # modification_wind()
    #     # modification_rain()
    #     # modification_fog()
    #     generate()
    #     default_weather()

def make_txt_outcome(type,main_value,amount_of_change,modify_value):
    with open("outcome/"+path+"/change_weather.txt", 'x') as f:
        f.write("changing the weather in type  = " + str(type) + "\n" +
                "main amount of " + str(type) + " is = " + str(main_value) + "\n" +
                "amount of changing is  = " + str(amount_of_change)+"\n" +
                "modify amount of " + str(type) + " is = " + str(modify_value))




if __name__ == '__main__':
    os.mkdir("outcome/"+path)
    run("rain")