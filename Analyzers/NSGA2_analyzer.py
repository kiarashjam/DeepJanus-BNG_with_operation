import pandas as pd
import json
import numpy as np
from os import listdir
import matplotlib.pyplot as plt
from datetime import datetime

time_columns = ["Generation id", "Number of archives", "Initial population time", "Evaluation process time",
                "Distance calculation time", "Whole process time"]
fog_columns = ["Generation id", "Number of archives", "Average fog amount for whole generation",
               "Name of the individual", "Fog density of failure version", "Fog density of successful version",
               "Average fog density of individual"]
whole_data_columns = ["Generation id", "Number of archives", "Average fog density", "Standard deviation of fog density"]

mypath = "data"
onlyfiles = [f for f in listdir(mypath)]
matchers = ['experiments_20210628205521']
matching = [s for s in onlyfiles if any(xs in s for xs in matchers)]

distances = []
main_distance = []
columns_json = []
fog_density = []


def time_consuming(json_data, i):
    for section in json_data:
        # print(section)
        if section == "archive_len":
            archive_len = json_data[section]
        elif section == "initial population time":
            initial_population_time = json_data[section]
        elif section == "evaluation process time":
            evaluation_population_time = json_data[section]
        elif section == "distance calculation time":
            assigning_distance_time = json_data[section]
        elif section == "whole generation time":
            whole_process_time = json_data[section]
    return [i, archive_len, initial_population_time, evaluation_population_time, assigning_distance_time,
            whole_process_time]


def produce_csv(list_of_data, column, name_of_file, path):
    df = pd.DataFrame(list_of_data, columns=column)
    producing_plot(df, path, name_of_file)
    df.to_csv(path + name_of_file + ".csv")


def producing_plot(df, path, name_of_file):
    if name_of_file == "time_information":
        i = 0
        whole_process_list = []
        initial_process_list = []
        testing_population_list = []
        calculation_distancces_list = []
        while i < len(df["Whole process time"]):
            whole_process_list.append(int(df["Whole process time"][i].split(":")[0]) * 60 +
                                      int(df["Whole process time"][i].split(":")[1]))
            initial_process_list.append(int(df["Initial population time"][i].split(":")[0]) * 60 +
                                        int(df["Initial population time"][i].split(":")[1]))
            testing_population_list.append(int(df["Evaluation process time"][i].split(":")[0]) * 60 +
                                           int(df["Evaluation process time"][i].split(":")[1]))
            calculation_distancces_list.append(int(df["Distance calculation time"][i].split(":")[0]) * 60 +
                                               int(df["Distance calculation time"][i].split(":")[1]))
            i = i + 1
        # plt.plot(df["Generation id"], whole_process_list, label='Successful member')
        # plt.xlabel('Generation id')
        # plt.ylabel('Whole process time')
        # plt.title("time per generation")
        # plt.savefig(path+"line_whole_time_generation_id"+".png")
        plt.figure(figsize=(12, 5))
        plt.bar(df["Generation id"], whole_process_list)
        plt.xlabel('Generation id')
        plt.ylabel('Whole process time')
        plt.title("time to process per generation")
        plt.savefig(path + "bar_whole_time_generation_id" + ".png", dpi=400)
        plt.show()

        plt.figure(figsize=(12, 5))
        plt.plot(df["Generation id"], df["Number of archives"])
        plt.xlabel('Generation id')
        plt.ylabel('total amount of archive')
        plt.title("size of archive  per every generation")
        plt.savefig(path + "plot_number_of_archive_generation_id" + ".png", dpi=400)
        plt.show()

        plt.figure(figsize=(12, 5))
        plt.bar(df["Generation id"], initial_process_list, color='b', label='generation of population', width=0.25)
        plt.bar(df["Generation id"], testing_population_list, color='g', label='testing the individuals', width=0.25)
        plt.bar(df["Generation id"], calculation_distancces_list, color='r', label='calculation of metrics', width=0.25)
        plt.xlabel('Generation id')
        plt.ylabel('process time')
        plt.title("duration of each process in whole process per generation")
        plt.savefig(path + "bar_eah_process_time_generation_id" + ".png", dpi=400)
        plt.show()
    elif name_of_file == "fog_density_details":
        names_list = df["Name of the individual"].unique()
        successful_list = []
        failure_list = []
        names = []
        for name in names_list:
            successful = df[df["Name of the individual"] == name]["Fog density of successful version"].unique()[0]
            failure = df[df["Name of the individual"] == name]["Fog density of failure version"].unique()[0]
            names.append(name)
            successful_list.append(successful)
            failure_list.append(failure)
        plt.figure(figsize=(12, 5))
        plt.scatter(names, successful_list, label='Successful member')
        plt.scatter(names, failure_list, label='Failure member')
        plt.xlabel('fog density amount')
        plt.ylabel('name of individual')
        plt.title("fog density falure and succesful version")
        plt.grid()
        plt.savefig(path + "line_two_member_fog" + ".png", dpi=400)
        plt.show()

    elif name_of_file == "whole_fog_information":
        plt.figure(figsize=(12, 5))
        plt.plot(df["Generation id"], df["Standard deviation of fog density"])
        plt.xlabel('Generation id')
        plt.ylabel('Standard deviation of fog densityl')
        plt.title("standard deviation per generation")
        plt.savefig(path + "line_std_generation_id" + ".png", dpi=400)
        plt.show()


if __name__ == '__main__':
    for experiment in matching:
        path_of_experiment = mypath + "/" + experiment + "/"
        mypath_gen = mypath + "/" + experiment + "/exp"
        generation = [f for f in listdir(mypath_gen)]
        matcher_gen = ['gen']
        matching_gen = [s for s in generation if any(xs in s for xs in matcher_gen)]
        first_data = []
        time_data = []
        i = 0
        for index in matching_gen:
            if index == "gen49":
                mypath_report = mypath + "/" + experiment + "/exp/" + index
                files_reports = [f for f in listdir(mypath_report)]
                matchers_report = ['report']
                reports = [s for s in files_reports if any(xs in s for xs in matchers_report)]
                json_path = mypath + "/" + experiment + "/exp/" + index + "/" + reports[0]
                f1 = open(json_path, )
                data1 = json.load(f1)
                temp = time_consuming(data1, i)
                time_data.append(temp)
                distances = []
                for section in data1:
                    distances.append(data1[section])
                    if section == "fog_average_amount":
                        average_fog = data1[section]
                    elif section == "archive_len":
                        number_of_solution = data1[section]
                    if i == 0:
                        columns_json.append(section)
                first_data = [i, number_of_solution, average_fog]

                mypath_ind = mypath + "/" + experiment + "/exp/" + index + "/archive"
                files_ind = [f for f in listdir(mypath_ind)]
                matchers_ind = ['.json']
                inds = [s for s in files_ind if any(xs in s for xs in matchers_ind)]
                for ind in inds:
                    json_ind_path = mypath + "/" + experiment + "/exp/" + index + "/archive/" + ind
                    f2 = open(json_ind_path, )
                    data2 = json.load(f2)
                    temp1 = data2["m1"]["fog_density"]
                    temp2 = data2["m2"]["fog_density"]
                    if temp1 > temp2:
                        fog_density.append(
                            [i, number_of_solution, average_fog, data2["name"], temp1, temp2, abs(temp2 + temp1) / 2])
                    else:
                        fog_density.append(
                            [i, number_of_solution, average_fog, data2["name"], temp2, temp1, abs(temp2 + temp1) / 2])

                main_distance.append(distances)
                i = i + 1

        produce_csv(time_data, time_columns, "time_information", path_of_experiment)
        produce_csv(fog_density, fog_columns, "fog_density_details", path_of_experiment)

        dframe = pd.DataFrame(fog_density, columns=fog_columns)
        run_id = dframe["Generation id"].unique()
        whole_data_info = []
        for i in run_id:
            df = dframe[dframe["Generation id"] == i]

            number_of_solution = df["Number of archives"].iloc[0]
            fog_avg = df["Average fog amount for whole generation"].iloc[0]
            list_of_avg_fog = df["Average fog density of individual"]
            std_fog_avg = np.std(list_of_avg_fog, axis=0)
            whole_data_info.append([i, number_of_solution, fog_avg, std_fog_avg])
        produce_csv(whole_data_info, whole_data_columns, "whole_fog_information", path_of_experiment)