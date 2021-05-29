import json

from data.experiments_20210519085252.self_driving import main_beamng, beamng_brewer
from datetime import datetime, time

class InitialValue:
    def __init__(self):
       pass

    def start(self):
        fog_densities_boundary_max = []
        fog_densities_boundary_min = []
        path_jsons = main_beamng.start()
        for path_ind in path_jsons:
            x = str(path_ind).split("gen")
            exp_path = x[0]
            print(path_ind)
            if path_ind:
                print("yes")
                f = open(path_ind)
                ind = json.load(f)
                type_operation = ind["m1"]['mutation_type']
                if type_operation == 'MUT_FOG':
                    temp1 = ind["m1"]['fog_density']
                    temp2 = ind["m2"]['fog_density']
                elif type_operation == 'MUT_RAIN':
                    temp1 = ind["m1"]['number_drop_rain']
                    temp2 = ind["m2"]['number_drop_rain']
                elif type_operation == 'MUT_WET_FOAM':
                    temp1 = ind["m1"]['wet_foam_density']
                    temp2 = ind["m2"]['wet_foam_density']
                elif type_operation == 'MUT_WET_RIPPLE':
                    temp1 = ind["m1"]['wet_ripple_density']
                    temp2 = ind["m2"]['wet_ripple_density']
                elif type_operation == 'MUT_ILLUMINATION':
                    temp1 = ind["m1"]['illumination']
                    temp2 = ind["m2"]['illumination']
                elif type_operation == 'MUT_OBSTACLE':
                    temp1 = ind["m1"]['position_of_obstacle']
                    temp2 = ind["m2"]['position_of_obstacle']
                elif type_operation == 'MUT_BUMP':
                    temp1 = ind["m1"]['number_of_bump']
                    temp2 = ind["m2"]['number_of_bump']
                elif type_operation == 'MUT_BUMP':
                    temp1 = ind["m1"]['number_of_bump']
                    temp2 = ind["m2"]['number_of_bump']


                f.close()
                print(temp1)
                print(temp2)
                if temp2 > temp1:
                    fog_densities_boundary_max.append(temp2)
                    fog_densities_boundary_min.append(temp1)
                else:
                    fog_densities_boundary_max.append(temp1)
                    fog_densities_boundary_min.append(temp2)
        print(fog_densities_boundary_max)

        boundary_max = min(fog_densities_boundary_max)
        boundary_min = max(fog_densities_boundary_min)
        print(boundary_max)
        print(boundary_min)
        print()

        return boundary_max, boundary_min, type_operation, exp_path


    def make_txt_outcome(self, boundary_max, boundary_min, type_operation, exp_path):
        path_of_test = "operation-" + str(datetime.now().date()) + "-" + str(datetime.now().time().hour) + "-" + str(
            datetime.now().time().minute) + "-" + str(datetime.now().time().second)

        with open(exp_path + path_of_test + "operators.txt", 'x') as f:
            f.write("changing the operation in type  = " + str(type_operation) + "\n" +
                    "max boundary of  is = " + str(boundary_max) + "\n" +
                    "max boundary of  is = " + str(boundary_min))



if __name__ == '__main__':
    one = InitialValue
    boundary_max, boundary_min, type_operation, path_of_test = InitialValue.start(one)
    if path_of_test:
        InitialValue.make_txt_outcome(one, boundary_max, boundary_min, type_operation, path_of_test)
