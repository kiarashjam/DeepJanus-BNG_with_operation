import random
import shutil
import numpy as np
import os
import matplotlib.pyplot as plt
from datetime import datetime
from time import sleep
import json
from self_driving import main_beamng


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

## wet_floor default variables
overallRippleMagnitude_default = 500
overallFoamOpacity_default = 3



## rain default variable =
default_drop_size = 0.0799999982
default_max_Speed =0.4
default_num_of_drops = 0
default_max_mass = 0.5





# # making the path for generating the
# path = "testing-" + str(datetime.now().date()) + "-" + str(datetime.now().time().hour) + "-" + str(
#     datetime.now().time().minute) + "-" + str(datetime.now().time().second)

class MapFolder:
    def __init__(self, path):
        self.path = path

    def delete_all_map(self):
        print("delted ..................................")
        shutil.rmtree(self.path, ignore_errors=True)
        # sometimes rmtree fails to remove files
        for tries in range(20):
            if os.path.exists(self.path):
                sleep(0.1)
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
        self.source_levels = LevelsFolder(os.getcwd()+'/levels_template/main_level/')
        self.source_levels_rain = LevelsFolder(os.getcwd() + '/levels_template/level_with_rain/')
        self.source_levels_wet_floor = LevelsFolder(os.getcwd() + '/levels_template/level_with_wet_floor')
        self.source_map = self.source_levels.get_map('tig')
        self.source_map_rain = self.source_levels_rain.get_map('tig')
        self.source_map_wet_floor = self.source_levels_wet_floor.get_map('tig')
        self.beamng_map = self.beamng_levels.get_map('tig')
        self.never_logged_path = True
    def install_map_with_rain(self):
        if self.never_logged_path:
            self.never_logged_path = False

        self.beamng_map.delete_all_map()
        shutil.copytree(src=self.source_map_rain.path, dst=self.beamng_map.path)
        print(f'Copying from [{self.source_map_rain.path}] to [{self.beamng_map.path}]')
    def install_map_with_wet_floor(self):
        if self.never_logged_path:
            self.never_logged_path = False

        self.beamng_map.delete_all_map()
        shutil.copytree(src=self.source_map_wet_floor.path, dst=self.beamng_map.path)
        print(f'Copying from [{self.source_map_wet_floor.path}] to [{self.beamng_map.path}]')


    def install_map(self):
        if self.never_logged_path:
            self.never_logged_path = False

        self.beamng_map.delete_all_map()
        shutil.copytree(src=self.source_map.path, dst=self.beamng_map.path)
        print(f'Copying from [{self.source_map.path}] to [{self.beamng_map.path}]')

    # def install_map_river(self):
    #     print(f'Copying from [{self.source_map_river.path}] to [{self.beamng_map.path}]')
    #     self.source_map.delete_all_map()
    #     shutil.copytree(src=self.source_map_river.path, dst=self.source_map.path)
    # def install_map_default(self):
    #     print(f'Copying from [{self.source_map_river.path}] to [{self.beamng_map.path}]')
    #     self.source_map.delete_all_map()
    #     shutil.copytree(src=self.source_map_default.path, dst=self.source_map.path)



class Operations:

    def default(self):
        default_weather("normal")

    def change_fog_amount(self, amount_of_fog):
        default_weather("normal")
        modification_fog(amount_of_fog)

    def change_rain_amount(self, amount_of_rain):
        default_weather("rain")
        modification_rain(amount_of_rain)

    def change_foam_amount(self, amount_of_foam):
        default_weather("wet_floor")
        modification_wet_floor(amount_of_foam, "foam")
    def change_ripple_amount(self, amount_of_ripple):
        default_weather("wet_floor")
        modification_wet_floor(amount_of_ripple, "ripple")

global operations
operations = Operations()

global maps
maps = Maps()

def default_weather(type_level):

  string_version_of_json=""
  if type_level == "rain":
      with open('levels_template/level_with_rain/tig/main/MissionGroup/sky_and_sun/items.level.json') as f:
          list_jasons = f.readlines()
  elif type_level == "normal":
      with open('levels_template/main_level/tig/main/MissionGroup/sky_and_sun/items.level.json') as f:
          list_jasons = f.readlines()
  elif type_level == "wet_floor":
      with open('levels_template/level_with_wet_floor/tig/main/MissionGroup/sky_and_sun/items.level.json') as f:
          list_jasons = f.readlines()

  json_version=list()
  for js in list_jasons:
    json_version.append(json.loads(js))
  i = 0
  while i<len(json_version):

    if json_version[i]["class"] == "Precipitation":
        json_version[i]["numDrops"] = default_num_of_drops
        json_version[i]["maxSpeed"] = default_max_Speed
        json_version[i]["maxMass"] = default_max_mass
        json_version[i]["dropSize"] = default_drop_size
    elif json_version[i]["class"] == "CloudLayer":
        json_version[i]["coverage"] = default_coverage_cloud
        json_version[i]["windSpeed"] = default_wind_speed
    elif json_version[i]["class"] == "LevelInfo":
        json_version[i]["fogDensity"] = default_fog_density
    elif json_version[i]["class"] == "river":
        json_version[i]["overallFoamOpacity"] = overallFoamOpacity_default
        json_version[i]["overallRippleMagnitude"] = overallRippleMagnitude_default
    elif json_version[i]["class"] == "ScatterSky":
        json_version[i]["shadowSoftness"] = default_shadowSoftness
        json_version[i]["colorize"] = default_colorize
        json_version[i]["ambientScale"] = default_ambientScale
        json_version[i]["sunScale"] = default_sunScale
        json_version[i]["fogScale"] = default_fogScale

    i = i + 1
  i = 0

  while i < len(json_version):
    if i == 0:
      string_version_of_json = str(json.dumps(json_version[i]))
    else:
      string_version_of_json = string_version_of_json +"\n"+ str(json.dumps(json_version[i]))
    i = i + 1
  writing_json_in_file(string_version_of_json,type_level)

  if type_level == "rain":
      maps.install_map_with_rain()
  elif type_level == "normal":
      maps.install_map()
  elif type_level == "wet_floor":
      maps.install_map_with_wet_floor()


def modification_fog(fog_density):
  print("################## fog density ================="+str(fog_density))
  string_version_of_json = ""
  with open('levels_template/main_level/tig/main/MissionGroup/sky_and_sun/items.level.json') as f:
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
  writing_json_in_file(string_version_of_json, "normal")
  maps.install_map()

def modification_rain(num_drops):
    string_version_of_json = ""
    with open('levels_template/level_with_rain/tig/main/MissionGroup/sky_and_sun/items.level.json') as f:
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
    writing_json_in_file(string_version_of_json, "rain")
    # maps.install_map_default()
    maps.install_map_with_rain()




def writing_json_in_file(string_version_of_json,type_level):
    if type_level == "rain":
        text_file = open('levels_template/level_with_rain/tig/main/MissionGroup/sky_and_sun/items.level.json', 'w')
    elif type_level == "normal":
        text_file = open('levels_template/main_level/tig/main/MissionGroup/sky_and_sun/items.level.json', 'w')
    elif type_level == "wet_floor":
        text_file = open('levels_template/level_with_wet_floor/tig/main/MissionGroup/sky_and_sun/items.level.json', 'w')
    text_file.write(string_version_of_json)
    text_file.close()

# def make_txt_outcome(type,main_value,amount_of_change,modify_value):
#     with open("outcome/"+path+"/change_weather.txt", 'x') as f:
#         f.write("changing the weather in type  = " + str(type) + "\n" +
#                 "main amount of " + str(type) + " is = " + str(main_value) + "\n" +
#                 "amount of changing is  = " + str(amount_of_change)+"\n" +
#                 "modify amount of " + str(type) + " is = " + str(modify_value))



##### river




def modification_wet_floor(amount,type):
  string_version_of_json = ""
  with open('levels_template/level_with_wet_floor/tig/main/MissionGroup/sky_and_sun/items.level.json') as f:
    list_jasons = f.readlines()
  json_version = list()
  for js in list_jasons:
    json_version.append(json.loads(js))
  i = 0
  if type == "foam":
      while i < len(json_version):
        if json_version[i]["class"] == "river":
            json_version[i]["overallFoamOpacity"] = amount
        i = i + 1
  if type == "ripple":
      while i < len(json_version):
        if json_version[i]["class"] == "river":
            json_version[i]["overallRippleMagnitude"] = amount

  i = 0
  while i < len(json_version):
    if i == 0:
      string_version_of_json = str(json.dumps(json_version[i]))
    else:
      string_version_of_json = string_version_of_json +"\n"+ str(json.dumps(json_version[i]))
    i = i + 1
  writing_json_in_file(string_version_of_json,"wet_floor")
  maps.install_map_with_wet_floor()








