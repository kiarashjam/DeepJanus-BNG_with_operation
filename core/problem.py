from typing import List

from core.config import Config
from core.archive import Archive
from core.individual import Individual
from core.member import Member


class Problem:
    def __init__(self, config: Config, archive: Archive):
        self.config: Config = config
        self.archive = archive
        print("............phase problem 4.2a ................")

    def deap_generate_individual(self) -> Individual:
        print("............phase 16 ................")
        raise NotImplemented()

    def deap_mutate_individual(self, individual: Individual):
        print("............phase 18 ................")
        individual.mutate()

    def deap_evaluate_individual(self, individual: Individual):
        print("............phase 17 ................")
        raise NotImplemented()

    def deap_individual_class(self):
        print("............phase 15 ................")
        raise NotImplemented()

    def on_iteration(self, idx, pop: List[Individual], logbook):
        print("............phase 9b ................")
        raise NotImplemented()

    def member_class(self):
        raise NotImplemented()

    def reseed(self, population, offspring):
        raise NotImplemented()

    def generate_random_member(self) -> Member:
        print("............phase 10 ................")
        raise NotImplemented()

    def pre_evaluate_members(self, individuals: List[Individual]):
        print("............phase 8b ................")
        pass