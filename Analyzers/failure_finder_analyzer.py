import pandas as pd
import json
import numpy as np
from os import listdir
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

csv_columns = ["amount", "status"]


mypath = "data"
onlyfiles = [f for f in listdir(mypath)]
matchers = ['experiments_20210722181712']
matching = [s for s in onlyfiles if any(xs in s for xs in matchers)]

distances = []
main_distance = []
columns_json = []
fog_density = []


def time_consuming(json_data, i):
    for section in json_data:
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
    csv_path = Path(path + "csv")
    csv_path.mkdir(parents=True, exist_ok=True)
    df.to_csv(str(csv_path) + "/" + name_of_file + ".csv")
    producing_plot(df, path, name_of_file)



def producing_plot(df, path, name_of_file):


        plt.figure(figsize=(12, 5))
        plt.scatter(df["amount"], df["status"], label='status amount')
        plt.title("status of the test per different amount of illumination")
        plot_path = Path(path + "plots")
        plot_path.mkdir(parents=True, exist_ok=True)
        plt.savefig(str(plot_path) + "/"+ name_of_file + ".png", dpi=400)



if __name__ == '__main__':
    for experiment in matching:
        path_of_experiment = mypath + "/" + experiment + "/"
        mypath_gen = mypath + "/" + experiment + "/exp"
        generation = [f for f in listdir(mypath_gen)]
        matcher_gen = ['reports']
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
            matchers_report = ['reports']
            reports = [s for s in files_reports if any(xs in s for xs in matchers_report)]
            json_path = mypath + "/" + experiment + "/exp/" + index + "/" + "report.json"
            f1 = open(json_path, )
            data1 = json.load(f1)
            amount= []
            status = []
            for section in data1:
                distances.append(data1[section])
                if section == "amount":
                    for element in data1[section]:
                        amount.append(element)
                elif section == "status":
                    for element in data1[section]:
                        status.append(element)
            i = 0
            each_seed= []
            while i < len(amount):
                data = []
                j=0
                while j < len(amount[i]):
                    data.append([amount[i][j], status[i][j]])
                    j = j + 1
                produce_csv( data, csv_columns, "illumination_status_seed_"+ str(i), path_of_experiment)
                i = i + 1


