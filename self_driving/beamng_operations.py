import random
import shutil
import numpy as np
import os
import matplotlib.pyplot as plt
from datetime import datetime
from time import sleep
import json
from self_driving.beamng_tig_maps import MapsOperation

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
overallRippleMagnitude_default = 0
overallFoamOpacity_default = 0



# rain default variable =
default_drop_size = 0.0799999982
default_max_Speed = 0.4
default_num_of_drops = 0
default_max_mass = 0.5




class BeamNGOperations:

    def default(self):
        default_weather()

    def change_fog_amount(self, amount_of_fog):
        default_weather()
        modification_weather(amount_of_fog, "MUT_FOG")
    def change_whole_rain_amount(self, number_drop_rain, size_of_drop):
        amounts = []
        default_weather()
        amounts.append(number_drop_rain)
        amounts.append(size_of_drop)
        modification_weather(amounts, "MUT_RAIN_WHOLE")
    def change_storm_amount(self, fog, number_drop_rain, size_of_drop, foam, ripple):
        amounts = []
        default_weather()
        amounts.append(fog)
        amounts.append(number_drop_rain)
        amounts.append(size_of_drop)
        amounts.append(foam)
        amounts.append(ripple)
        modification_weather(amounts, "MUT_STORM")
    def change_whole_wet_floor_amount(self, foam, ripple):
        amounts = []
        default_weather()
        amounts.append(foam)
        amounts.append(ripple)
        modification_weather(amounts, "MUT_WHOLE_WET_FLOOR")

    def change_rain_amount(self, amount_of_rain):
        default_weather()
        modification_weather(amount_of_rain, "MUT_RAIN")

    def change_size_of_drop_amount(self, size_of_drop):
        default_weather()
        modification_weather(size_of_drop, "MUT_DROP_SIZE")

    def change_foam_amount(self, amount_of_foam):
        default_weather()
        modification_weather(amount_of_foam, "MUT_WET_FOAM")

    def change_ripple_amount(self, amount_of_ripple):
        default_weather()
        modification_weather(amount_of_ripple, "MUT_WET_RIPPLE")


global operations
operations = BeamNGOperations()

global maps
maps = MapsOperation()


def default_weather():
    string_version_of_json = ""
    with open('levels_template/tig/main/MissionGroup/sky_and_sun/items.level.json') as f:
        list_jasons = f.readlines()

    json_version = list()
    for js in list_jasons:
        json_version.append(json.loads(js))
    i = 0
    while i < len(json_version):

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
            json_version[i]["nodes"] = [[-1000, -1000, -27.9, 1000, 5, 0, 0, 1],
                                        [-1000, -1000, -27.9, 1000, 5, 0, 0, 1]]
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
            string_version_of_json = string_version_of_json + "\n" + str(json.dumps(json_version[i]))
        i = i + 1
    writing_json_in_file(string_version_of_json)
    maps.install_map()

def writing_json_in_file(string_version_of_json):
    text_file = open('levels_template/tig/main/MissionGroup/sky_and_sun/items.level.json', 'w')
    text_file.write(string_version_of_json)
    text_file.close()

def modification_weather(amount, type_operation):
    string_version_of_json = ""
    with open('levels_template/tig/main/MissionGroup/sky_and_sun/items.level.json') as f:
        list_jasons = f.readlines()
    json_version = list()
    for js in list_jasons:
        json_version.append(json.loads(js))
    i = 0
    if type_operation == "MUT_WET_FOAM":
        while i < len(json_version):
            if json_version[i]["class"] == "river":
                json_version[i]["overallFoamOpacity"] = amount
                json_version[i]["nodes"] = [[-1000, -1000, -27.9, 1000, 5, 0, 0, 1],
                                            [1000, 1000, -27.9, 1000, 5, 0, 0, 1]]
            i = i + 1
    elif type_operation == "MUT_WET_RIPPLE":
        while i < len(json_version):
            if json_version[i]["class"] == "river":
                json_version[i]["overallRippleMagnitude"] = amount
                json_version[i]["nodes"] = [[-1000, -1000, -27.9, 1000, 5, 0, 0, 1],
                                            [1000, 1000, -27.9, 1000, 5, 0, 0, 1]]

            i = i + 1
    elif type_operation == "MUT_RAIN":
        while i < len(json_version):
            if json_version[i]["class"] == "LevelInfo":
                json_version[i]["fogDensity"] = 0.02
            elif json_version[i]["class"] == "Precipitation":
                json_version[i]["numDrops"] = amount
            elif json_version[i]["class"] == "CloudLayer":
                json_version[i]["coverage"] = 1
            elif json_version[i]["class"] == "ScatterSky":
                json_version[i]["shadowSoftness"] = 1
                json_version[i]["colorize"] = [0.427451, 0.427451, 0.427451, 1]
                json_version[i]["ambientScale"] = [0.545098, 0.545098, 0.54902, 1]
                json_version[i]["sunScale"] = [0.686275, 0.686275, 0.686275, 1]
                json_version[i]["fogScale"] = [0.756863, 0.760784, 0.760784, 1]
            i = i + 1
    elif type_operation == "MUT_DROP_SIZE":
        while i < len(json_version):
            if json_version[i]["class"] == "LevelInfo":
                json_version[i]["fogDensity"] = 0.02
            elif json_version[i]["class"] == "Precipitation":
                json_version[i]["numDrops"] = amount[0]
                json_version[i]["dropSize"] = amount[1]
            elif json_version[i]["class"] == "CloudLayer":
                json_version[i]["coverage"] = 1
            elif json_version[i]["class"] == "ScatterSky":
                json_version[i]["shadowSoftness"] = 1
                json_version[i]["colorize"] = [0.427451, 0.427451, 0.427451, 1]
                json_version[i]["ambientScale"] = [0.545098, 0.545098, 0.54902, 1]
                json_version[i]["sunScale"] = [0.686275, 0.686275, 0.686275, 1]
                json_version[i]["fogScale"] = [0.756863, 0.760784, 0.760784, 1]
            i = i + 1
    elif type_operation == "MUT_STORM":
        while i < len(json_version):
            if json_version[i]["class"] == "LevelInfo":
                json_version[i]["fogDensity"] = amount[0]
            elif json_version[i]["class"] == "Precipitation":
                json_version[i]["numDrops"] = amount[1]
                json_version[i]["dropSize"] = amount[2]
            elif json_version[i]["class"] == "CloudLayer":
                json_version[i]["coverage"] = 1
            elif json_version[i]["class"] == "ScatterSky":
                json_version[i]["shadowSoftness"] = 1
                json_version[i]["colorize"] = [0.427451, 0.427451, 0.427451, 1]
                json_version[i]["ambientScale"] = [0.545098, 0.545098, 0.54902, 1]
                json_version[i]["sunScale"] = [0.686275, 0.686275, 0.686275, 1]
                json_version[i]["fogScale"] = [0.756863, 0.760784, 0.760784, 1]
            elif json_version[i]["class"] == "river":
                json_version[i]["overallFoamOpacity"] = amount[3]
                json_version[i]["overallRippleMagnitude"] = amount[4]
                json_version[i]["nodes"] = [[-1000, -1000, -27.9, 1000, 5, 0, 0, 1],
                                            [1000, 1000, -27.9, 1000, 5, 0, 0, 1]]
            i = i + 1
    elif type_operation == "MUT_WHOLE_WET_FLOOR":
        while i < len(json_version):
            if json_version[i]["class"] == "river":
                json_version[i]["overallFoamOpacity"] = amount[0]
                json_version[i]["overallRippleMagnitude"] = amount[1]
                json_version[i]["nodes"] = [[-1000, -1000, -27.9, 1000, 5, 0, 0, 1],
                                            [1000, 1000, -27.9, 1000, 5, 0, 0, 1]]
            i = i + 1
    elif type_operation == "MUT_RAIN_WHOLE":
        while i < len(json_version):
            if json_version[i]["class"] == "LevelInfo":
                json_version[i]["fogDensity"] = 0.02
            elif json_version[i]["class"] == "Precipitation":
                json_version[i]["numDrops"] = 10000
                json_version[i]["dropSize"] = amount
            elif json_version[i]["class"] == "CloudLayer":
                json_version[i]["coverage"] = 1
            elif json_version[i]["class"] == "ScatterSky":
                json_version[i]["shadowSoftness"] = 1
                json_version[i]["colorize"] = [0.427451, 0.427451, 0.427451, 1]
                json_version[i]["ambientScale"] = [0.545098, 0.545098, 0.54902, 1]
                json_version[i]["sunScale"] = [0.686275, 0.686275, 0.686275, 1]
                json_version[i]["fogScale"] = [0.756863, 0.760784, 0.760784, 1]
            i = i + 1

    elif type_operation == "MUT_FOG":
        while i < len(json_version):
            if json_version[i]["class"] == "LevelInfo":
                json_version[i]["fogDensity"] = amount
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
