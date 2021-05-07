class Config:
    GEN_RANDOM = 'GEN_RANDOM'
    GEN_RANDOM_SEEDED = 'GEN_RANDOM_SEEDED'
    GEN_SEQUENTIAL_SEEDED = 'GEN_SEQUENTIAL_SEEDED'

    SEG_LENGTH = 25
    NUM_SPLINE_NODES =10
    INITIAL_NODE = (0.0, 0.0, -28.0, 8.0)
    ROAD_BBOX_SIZE = (-250, 0, 250, 500)

    MUT_CONTROL_POINTS = 'MUT_CONTROL_POINTS'
    MUT_FOG = 'MUT_FOG'
    MUT_RAIN = 'MUT_RAIN'
    MUT_WET_FOAM = 'MUT_WET_FOAM'
    MUT_WET_RIPPLE = 'MUT_WET_RIPPLE'
    MUT_ILLUMINATION = 'MUT_ILLUMINATION'
    MUT_OBSTACLE = 'MUT_OBSTACLE'
    MUT_BUMP = 'MUT_BUMP'

    ### surrounding operation

    Sign = 'Sign'
    Trees = 'Trees'
    Terrain = 'Terrain'

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
        self.experiment_name = 'exp'
        self.fitness_weights = (1.0, -1.0)

        self.POPSIZE = 12
        self.NUM_GENERATIONS = 150

        self.RESEED_UPPER_BOUND = int(self.POPSIZE * 0.1)

        self.MUTATION_EXTENT = 6.0
        self.ARCHIVE_THRESHOLD = 35.0

        self.MUTATION_TYPE = Config.MUT_OBSTACLE
        self.SURROUNDING = [Config.Trees]

        self.K_SD = 0.01

        self.simulation_save = True
        self.simulation_name = 'beamng_nvidia_runner/sim_$(id)'

        #self.keras_model_file = 'self-driving-car-4600.h5'
        self.keras_model_file = 'self-driving-car-185-2020.h5'

        #self.generator_name = Config.GEN_RANDOM
        #self.generator_name = Config.GEN_RANDOM_SEEDED
        self.generator_name = Config.GEN_SEQUENTIAL_SEEDED
        self.seed_folder = 'population_HQ1'