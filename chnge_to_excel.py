import  pandas as pd
import json
import numpy as np
from os import listdir

# df_json = pd.read_json("/Users/kiarashjamshidi/PycharmProjects/DeepJanus-BNG_with_operation/data/experiments_20210614132437/exp/gen0/report0.json")
# for key , value in df_json:
#     print(key)

# Python program to read
# json file

mypath = "data"
onlyfiles = [f for f in listdir(mypath)]
matchers = ['experiments']
matching = [s for s in onlyfiles if any(xs in s for xs in matchers)]


i = 0
distances = []
main_distance = []
columns_json = []
fog_density = []
for experiment in matching:
    mypath_gen = mypath+"/"+experiment+"/exp"
    generation = [f for f in listdir(mypath_gen)]
    matcher_gen = ['gen']
    matching_gen = [s for s in generation if any(xs in s for xs in matcher_gen)]
    for index in matching_gen:
        mypath_report = mypath+"/"+experiment+"/exp/" +index
        files_reports = [f for f in listdir(mypath_report)]
        matchers_report = ['report']
        reports = [s for s in files_reports if any(xs in s for xs in matchers_report)]
        json_path = mypath+"/"+experiment+"/exp/" + index + "/" + reports[0]
        f1 = open(json_path, )
        data1 = json.load(f1)
        distances = []

        for section in data1:
            distances.append(data1[section])
            if section == "fog_average_amount":
                average_fog = data1[section]
            elif section == "archive_len":
                number_of_solution = data1[section]
            if i == 0:
                columns_json.append(section)

        mypath_ind = mypath + "/" + experiment + "/exp/" + index + "/archive"
        files_ind = [f for f in listdir(mypath_ind)]
        matchers_ind = ['.json']
        inds = [s for s in files_ind if any(xs in s for xs in matchers_ind)]
        for ind in inds:
            json_ind_path = mypath + "/" + experiment + "/exp/" + index + "/archive/"+ ind
            f2 = open(json_ind_path, )
            data2 = json.load(f2)
            temp1 = data2["m1"]["fog_density"]
            temp2 = data2["m2"]["fog_density"]
            if temp1 > temp2 :
                fog_density.append([i, number_of_solution, average_fog , data2["name"], temp1, temp2, abs(temp2+temp1) / 2 ])
            else:
                fog_density.append([i, number_of_solution, average_fog, data2["name"], temp2, temp1, abs(temp2+temp1) / 2])
        main_distance.append(distances)
        i = i + 1


    # main_distance.insert(0,columns_json)

    dframe = pd.DataFrame(fog_density, columns = ["generation number" , "number of solution", "average fog amount for whole generation",
                                                    "name of the individual", "fog density of failure version ",
                                                    "fog density of successful version", "average fog density of individual"])
    run_id = dframe["generation number"].unique()
    whole_data_info =[]
    for i in run_id:
        df = dframe[dframe["generation number"] == i]
        number_of_solution = df["number of solution"].iloc[0]
        fog_avg = df["average fog amount for whole generation"].iloc[0]
        list_of_avg_fog = df["average fog density of individual"]
        std_fog_avg = np.std(list_of_avg_fog, axis =0)
        whole_data_info.append([i, number_of_solution, fog_avg, std_fog_avg])
        print(std_fog_avg)

    dframe2 = pd.DataFrame(whole_data_info, columns = ["run id", "number of solutions", "average fog density ",
                                                       "standard deviation of fog density"])
    print(dframe2)
    # print(dframe)
    dframe2.to_csv(experiment + "_fog_information.csv")

# # Opening JSON file
# f = open('data/experiments_20210614132437/exp/gen0/report0.json', )
#
# # returns JSON object as
# # a dictionary
# data = json.load(f)
#
#
# # Iterating through the json
# # list
# columnes =[]
# rows = []
# for i in data:
#     rows.append(i)
#     columnes.append(data[i])
# print(len(rows))
# print(len(columnes))
#
#
# # print(data)
# # df = pd.DataFrame()
#
# # Closing file
# f.close()
# # importing pandas library
#
# # string values in the list
# lst = ['Java', 'Python', 'C', 'C++',
#        'JavaScript', 'Swift', 'Go']
#
# # Calling DataFrame constructor on list
# dframe = pd.DataFrame(data,index =["y"])
# print(dframe)