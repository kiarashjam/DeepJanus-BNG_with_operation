import pandas as pd
import json
import numpy as np
from os import listdir
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

time_columns = ["Initial population time", "Evaluation process time", "Whole process time",
                "Every seed duration"]
fog_columns =["Seed id",  "Fog density of successful version", "Fog density of failure version"]
avg_std_columns = ["Standard deviation of fog density", "Average fog density",  "max failure fog density",
                   "min failure fog density"]

mypath = "data"
onlyfiles = [f for f in listdir(mypath)]
matchers = ['experiments_20210708154512']
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
    csv_path = Path(path +"csv")
    csv_path.mkdir(parents=True, exist_ok=True)
    producing_plot(df, path, name_of_file)
    df.to_csv(str(csv_path) +"/"+ name_of_file + ".csv")


def producing_plot(df, path, name_of_file):
    if name_of_file == "time_information":
        i = 0
        whole_process_list = []
        initial_process_list = []
        testing_population_list = []
        every_seed_time_in_minutes = []
        whole_process_in_minute = (int(df["Whole process time"][i].split(":")[0]) * 60 + int(
            df["Whole process time"][i].split(":")[1]))
        initial_population_time_in_minute = (int(df["Initial population time"][i].split(":")[0]) * 60 +
                                             int(df["Initial population time"][i].split(":")[1]))
        evaluation_time_in_minutes = (int(df["Evaluation process time"][i].split(":")[0]) * 60 +
                                      int(df["Evaluation process time"][i].split(":")[1]))
        while i < len(df["Every seed duration"][0]):
            every_seed_time_in_minutes.append(int(df["Every seed duration"][0][i].split(":")[0]) * 60 +
                                               int(df["Every seed duration"][0][i].split(":")[1]))
            i = i + 1
        plt.figure(figsize=(12, 5))
        plt.bar(range(0,i),every_seed_time_in_minutes)
        plt.xlabel('Generation id')
        plt.ylabel('Whole process time')
        plt.title("time to process per generation")
        plot_path = Path(path + "plots")
        plot_path.mkdir(parents=True, exist_ok=True)
        plt.savefig(str(plot_path) + "/bar_whole_time_generation_id" + ".png", dpi=400)
        plt.show()
    elif name_of_file == "fog_density_details":

        successful_list = []
        failure_list = []

        print(df["Fog density of successful version"])

        failure = df["Fog density of failure version"]
        print(type(failure))

        plt.figure(figsize=(12, 5))
        plt.scatter(df["Seed id"], df["Fog density of successful version"], label='Successful member')
        plt.scatter(df["Seed id"], df["Fog density of failure version"], label='Failure member')
        plt.xlabel('fog density amount')
        plt.ylabel('name of individual')
        plt.title("fog density falure and succesful version")
        plot_path = Path(path + "plots")
        plot_path.mkdir(parents=True, exist_ok=True)
        plt.savefig(str(plot_path) + "/line_two_member_fog" + ".png", dpi=400)
        plt.show()

    elif name_of_file == "whole_fog_information":
        plt.figure(figsize=(12, 5))
        plt.plot(df["Generation id"], df["Standard deviation of fog density"])
        plt.xlabel('Generation id')
        plt.ylabel('Standard deviation of fog densityl')
        plt.title("standard deviation per generation")
        plot_path = Path(path + "plots")
        plot_path.mkdir(parents=True, exist_ok=True)
        plt.savefig(str(plot_path) + "/line_std_generation_id" + ".png", dpi=400)
        plt.show()


if __name__ == '__main__':
    for experiment in matching:
        path_of_experiment = mypath + "/" + experiment + "/"
        mypath_gen = mypath + "/" + experiment + "/exp"
        generation = [f for f in listdir(mypath_gen)]
        matcher_gen = ['individuals']
        matching_gen = [s for s in generation if any(xs in s for xs in matcher_gen)]
        first_data = []
        time_data = []
        i = 0
        for index in matching_gen:
            number_of_solution = 0
            fog_avg = 0
            average_fog = 0
            mypath_report = mypath + "/" + experiment + "/exp/" + index
            files_reports = [f for f in listdir(mypath_report)]
            matchers_report = ['report']
            reports = [s for s in files_reports if any(xs in s for xs in matchers_report)]
            json_path = mypath + "/" + experiment + "/exp/" + index + "/" + "report.json"
            f1 = open(json_path, )
            data1 = json.load(f1)
            # temp = time_consuming(data1, i)
            # time_data.append(temp)
            distances = []
            success_member_fog_amount = []
            failure_member_fog_amount = []
            evaluation_population_time = []
            whole_process_time = []
            initial_population_time = []
            every_evaluation_time = []
            for section in data1:
                distances.append(data1[section])
                if section == "amount for successful fog densities":
                    success_member_fog_amount = data1[section]
                elif section == "amount for failure fog densities":
                    failure_member_fog_amount = data1[section]
                elif section == "evaluation_population_time":
                    evaluation_population_time = data1[section]
                elif section == "whole_process_time":
                    whole_process_time = data1[section]
                elif section == "initial_population_time":
                    initial_population_time = data1[section]
                elif section == "every_evaluation_time":
                    every_evaluation_time = data1[section]
                    # if i == 0:
                columns_json.append(section)
            first_data = [i, number_of_solution, average_fog]
            time_data.append([initial_population_time, evaluation_population_time, whole_process_time,
                               every_evaluation_time])

            mypath_ind = mypath + "/" + experiment + "/exp/" + index + "/population_binary_search"
            files_ind = [f for f in listdir(mypath_ind)]
            matchers_ind = ['.json']
            inds = [s for s in files_ind if any(xs in s for xs in matchers_ind)]
            for ind in inds:
                json_ind_path = mypath + "/" + experiment + "/exp/" + index + "/population_binary_search/" + ind
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
        i = 0
        fog_amount = []
        fog_failures_array = []
        while i < len(success_member_fog_amount):
            fog_amount.append([i, success_member_fog_amount[i], failure_member_fog_amount[i]])
            fog_failures_array.append(failure_member_fog_amount[i])
            i = i + 1

        produce_csv(time_data, time_columns, "time_information", path_of_experiment)
        produce_csv(fog_amount, fog_columns, "fog_density_details", path_of_experiment)
        produce_csv([[np.std(fog_failures_array, axis=0), np.mean(fog_failures_array) , np.max(fog_failures_array),
                      np.min(fog_failures_array)]], avg_std_columns, "std_avg_details", path_of_experiment)
        

        # dframe = pd.DataFrame(fog_density, columns=fog_columns)
        # run_id = dframe["Generation id"].unique()
        # whole_data_info = []
        # for i in run_id:
        #     df = dframe[dframe["Generation id"] == i]
        #
        #     number_of_solution = df["Number of archives"].iloc[0]
        #     fog_avg = df["Average fog amount for whole generation"].iloc[0]
        #     list_of_avg_fog = df["Average fog density of individual"]
        #     std_fog_avg = np.std(list_of_avg_fog, axis=0)
        #     whole_data_info.append([i, number_of_solution, fog_avg, std_fog_avg])
        # produce_csv(whole_data_info, whole_data_columns, "whole_fog_information", path_of_experiment)