from typing import Dict

from core.problem import Problem
from core.member import Member
from core.folder_storage import SeedStorage
from core.folders import folders
from core.seed_pool import SeedPool


class SeedPoolFolder(SeedPool):
    def __init__(self, problem: Problem, folder_name, type_operation, amount):
        print(
            "SeedPoolImpl..................SeedPoolFolder..................... initial ...........................................")
        super().__init__(problem)
        self.storage = SeedStorage(folder_name)
        self.type_operation = type_operation
        self.amount = amount
        self.file_path_list = self.storage.all_files()
        assert (len(self.file_path_list)) > 0
        self.cache: Dict[str, Member] = {}

    def __len__(self):
        print(
            "SeedPoolImpl..................SeedPoolFolder..................... len ...........................................")
        return len(self.file_path_list)

    def __getitem__(self, item) -> Member:
        print(
            "SeedPoolImpl...................SeedPoolFolder.................... getitem ...........................................")
        path = self.file_path_list[item]
        result: Member = self.cache.get(path, None)
        if not result:
            result = self.problem.member_class().from_dict(self.storage.read(path), self.type_operation, self.amount)
            self.cache[path] = result
        result.problem = self.problem
        return result


class SeedPoolRandom(SeedPool):

    def __init__(self, problem, n):
        print(
            "SeedPoolImpl.................SeedPoolRandom...................... initial ...........................................")

        super().__init__(problem)
        self.n = n
        self.seeds = [problem.generate_random_member() for _ in range(self.n)]

    def __len__(self):
        print(
            "SeedPoolImpl..................SeedPoolRandom..................... len ...........................................")
        return self.n

    def __getitem__(self, item):
        print(
            "SeedPoolImpl...................SeedPoolRandom.................... getitem ...........................................")
        return self.seeds[item]


class SeedPoolMnist(SeedPool):
    def __init__(self, problem: Problem, filename):
        print(
            "SeedPoolImpl..............SeedPoolMnist......................... initial ...........................................")
        super().__init__(problem)
        content = folders.member_seeds.joinpath(filename).read_text()
        self.seeds_index = content.split(',')
        self.cache: Dict[str, Member] = {}

    def __len__(self):
        print(
            "SeedPoolImpl..................SeedPoolMnist..................... len ...........................................")
        return len(self.seeds_index)

    def __getitem__(self, item) -> Member:
        print(
            "SeedPoolImpl................SeedPoolMnist....................... getitem ...........................................")
        mnist_index = self.seeds_index[item]
        result: Member = self.cache.get(mnist_index, None)
        if not result:
            # result = self.problem.member_class().from_dict(self.storage.read(path))
            raise NotImplemented()
            self.cache[mnist_index] = result
        return result
