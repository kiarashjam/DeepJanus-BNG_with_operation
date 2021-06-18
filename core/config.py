class Config:
    GEN_RANDOM = 'GEN_RANDOM'
    GEN_RANDOM_SEEDED = 'GEN_RANDOM_SEEDED'
    GEN_SEQUENTIAL_SEEDED = 'GEN_SEQUENTIAL_SEEDED'
    GEN_DIVERSITY = 'GEN_DIVERSITY'


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

    # surrounding operation

    Sign = 'Sign'
    Trees = 'Trees'
    Terrain = 'Terrain'
    Rocks = 'Rocks'
    Cabin = 'Cabin'
    House = 'House'
    Surrounding_amount ={"Trees_amount": 2000, "Rocks_amount": 2000, "Cabin_amount": 1000, "House_amount": 1000}



    # threshold_min
    FOG_DENSITY_threshold_min = 0
    WET_FOAM_threshold_min = 0
    NUMBER_OF_DROP_RAIN_threshold_min = 0
    WET_RIPPLE_threshold_min = 0
    NUMBER_BUMP_threshold_min = 0
    ADDING_OBSTACLE_min = 0
    ILLUMINATION_AMOUNT_threshold_min = 0

    # threshold_max
    FOG_DENSITY_threshold_max = 1
    WET_FOAM_threshold_max = 30
    NUMBER_OF_DROP_RAIN_threshold_max = 3000000
    WET_RIPPLE_threshold_max = 700
    NUMBER_BUMP_threshold_max = 3
    ADDING_OBSTACLE_max = 100
    ILLUMINATION_AMOUNT_threshold_max = 1




    def __init__(self,):
        self.experiment_name = 'exp'
        self.fitness_weights = (1.0, -1.0)
        self.POOLSIZE = 40
        self.POPSIZE = 12
        self.NUM_GENERATIONS = 2

        self.RESEED_UPPER_BOUND = int(self.POPSIZE * 0.1)

        self.MUTATION_EXTENT = 6.0
        self.ARCHIVE_THRESHOLD = 35.0

        self.MUTATION_FOG_PRECISE = 0.05
        self.MUTATION_RAIN_PRECISE = 10
        self.MUTATION_FOAM_PRECISE = 2
        self.MUTATION_RIPPLE_PRECISE = 10
        self.MUTATION_OBSTACLE_PRECISE = 0.1
        self.MUTATION_OBSTACLE_AXIS = 'y'
        self.MUTATION_BUMP_PRECISE = 0.1
        self.MUTATION_ILLUMINATION_PRECISE = 0.1


        self.MUTATION_TYPE = Config.MUT_FOG
        self.SURROUNDING = []
        self.Surrounding_amount = Config.Surrounding_amount

        self.K_SD = 0.01

        self.simulation_save = True
        self.simulation_name = 'beamng_nvidia_runner/sim_$(id)'

        #self.keras_model_file = 'self-driving-car-4600.h5'
        self.keras_model_file = 'self-driving-car-185-2020.h5'

        #self.generator_name = Config.GEN_RANDOM
        #self.generator_name = Config.GEN_RANDOM_SEEDED
        # self.generator_name = Config.GEN_SEQUENTIAL_SEEDED
        self.generator_name = Config.GEN_RANDOM
        # self.seed_folder = 'population_HQ1'

        self.seed_folder = 'initial_pool'
        self.initial_population_folder = "initial_population"

        self.RUNTIME = 36000
        self.INTERVAL = 3600
