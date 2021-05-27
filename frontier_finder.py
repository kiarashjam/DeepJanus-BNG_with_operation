import json
from datetime import time
from os import listdir
from os.path import isfile, join
from time import sleep

import main

my_path = "data"


class InitialValue:
    fog_max = 1
    fog_min = 0
    precise_fog = 0.2


    def give_new_boundry(old_files):
        new_files_data = []
        all_files = [f for f in listdir(my_path)]
        for i in all_files:
            new_files_data.append(i)

        simulation_name = ""
        new_list = list(set(old_files).difference(new_files_data))
        if len(new_list) != 0:
            for item in new_list:
                if "experiments" in item:
                    simulation_name = item
            path_of_genes = 'data/' + simulation_name + '/exp'

            genes = [f for f in listdir(path_of_genes)]

            fog_densities_boundry = []
            for gene in genes:
                if "gen" in gene:

                    path_of_ind = path_of_genes + "/" + gene + "/" + 'archive'
                    all_inf_ind = [f for f in listdir(path_of_ind)]
                    f = open(path_of_ind + "/" + all_inf_ind[0])
                    ind = json.load(f)
                    fog_densities_boundry.append(ind["m1"]['fog_density'])
                    fog_densities_boundry.append(ind["m2"]['fog_density'])
                    f.close()
            maximum = max(fog_densities_boundry)
            minimum = min(fog_densities_boundry)
        else:
            print("the list is empty")
            minimum = 0
            maximum = 0
        return maximum, minimum

    def finding_frontier(self):
        i = 0
        while i < 6:
            print(self.socket_port)
            fog_densities_boundary = []
            path_ind = main.start()
            if path_ind:
                f = open(path_ind)
                ind = json.load(f)
                fog_densities_boundary.append(ind["m1"]['fog_density'])
                fog_densities_boundary.append(ind["m2"]['fog_density'])
                f.close()
                maximum = max(fog_densities_boundary)
                minimum = min(fog_densities_boundary)
                self.fog_max = maximum
                self.fog_min = minimum
                self.precise_fog = self.precise_fog / 10
                print(self.fog_max)
                print(self.fog_min)
            self.socket_port = self.socket_port + 1
            i = i + 1


if __name__ == '__main__':
    one = InitialValue
    InitialValue.finding_frontier(one)
