class Config:
    GEN_RANDOM = 'GEN_RANDOM'
    GEN_RANDOM_SEEDED = 'GEN_RANDOM_SEEDED'
    GEN_SEQUENTIAL_SEEDED = 'GEN_SEQUENTIAL_SEEDED'

    SEG_LENGTH = 25
    NUM_SPLINE_NODES =10
    INITIAL_NODE = (0.0, 0.0, -28.0, 8.0)
    ROAD_BBOX_SIZE = (-250, 0, 250, 500)




    ##### threshold_min
    FOG_DENSITY_threshold_min = 0
    WET_FOAM_threshold_min = 0
    NUMBER_OF_DROP_RAIN_threshold_min = 0
    WET_RIPPLE_threshold_min = 0
    NUMBER_BUMP_threshold_min = 0
    ADDING_OBSTACLE_min = 0
    ILLUMINATION_AMOUNT_threshold_min = 0

    ##### threshold_max
    FOG_DENSITY_threshold_max = 1
    WET_FOAM_threshold_max = 40
    NUMBER_OF_DROP_RAIN_threshold_max = 30000
    WET_RIPPLE_threshold_max = 100
    NUMBER_BUMP_threshold_max = 1000
    ADDING_OBSTACLE_max = 100
    ILLUMINATION_AMOUNT_threshold_max = 1


    def __init__(self):
        print("............phase config / 3.1 a ................")
        self.experiment_name = 'exp'
        self.fitness_weights = (1.0, -1.0)

        self.POPSIZE = 1
        self.NUM_GENERATIONS = 150

        self.RESEED_UPPER_BOUND = int(self.POPSIZE * 0.1)

        self.MUTATION_EXTENT = 6.0
        self.ARCHIVE_THRESHOLD = 35.0

        ######## the intial amount
        self.FOG_DENSITY = 0.9
        self.WET_FOAM = 40
        self.NUMBER_OF_DROP_RAIN = 300000
        self.WET_RIPPLE = 30000
        self.NUMBER_BUMP = 400
        self.ILLUMINATION_AMOUNT = 0.7
        ################





        self.K_SD = 0.01

        self.simulation_save = True
        self.simulation_name = 'beamng_nvidia_runner/sim_$(id)'

        #self.keras_model_file = 'self-driving-car-4600.h5'
        self.keras_model_file = 'self-driving-car-190-2020.h5'

        #self.generator_name = Config.GEN_RANDOM
        #self.generator_name = Config.GEN_RANDOM_SEEDED
        self.generator_name = Config.GEN_SEQUENTIAL_SEEDED
        self.seed_folder = 'population_HQ1'
