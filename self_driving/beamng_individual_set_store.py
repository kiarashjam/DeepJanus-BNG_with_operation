# this classes are here in the belief that it is needed to have on a drive folder files a representation of the
# individual this representation is different from saving/loading a member. This folder structure is aimed to
# give the highest information to the human inspecting the individual
# ------------ o --------------- o ----------------
# it is advisable that the folder structure is hidden externally to this file source code
# this is in the aim to access the individuals information through save (and load)
# so, if the folder structure changes, the only source code affected should be in this file source code

import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from core.archive import IndividualSet
from core.folders import folders
from self_driving.beamng_individual import BeamNGIndividual
from self_driving.beamng_member import BeamNGMember
from self_driving.beamng_road_imagery import BeamNGRoadImagery
from self_driving.road_points import RoadPoints


class BeamNGIndividualSetStore:
    def __init__(self, folder: Path):
        print(
            "BeamNGIndividualSetStore....................................... initial ...........................................")
        self.folder = folder

    def save(self, individuals: IndividualSet):
        print(
            "BeamNGIndividualSetStore....................................... save ...........................................")
        for ind in individuals:
            _BeamNGIndividualCompositeMembersStore(self.folder).save(ind)
            # _BeamNGIndividualSimpleStore(self.folder).save(ind)


class _BeamNGIndividualStore:

    def save(self, ind: BeamNGIndividual, prefix: str = None):
        print(
            "BeamNGIndividualSetStore..................._BeamNGIndividualStore.................... save ...........................................")
        raise NotImplemented()

    def load(self, prefix: str) -> BeamNGIndividual:
        print(
            "BeamNGIndividualSetStore..................._BeamNGIndividualStore.................... evaluate ...........................................")

        raise NotImplemented()


class _BeamNGIndividualCompositeMembersStore:
    def __init__(self, folder: Path):
        print(
            "BeamNGIndividualSetStore.................._BeamNGIndividualCompositeMembersStore..................... initial ...........................................")

        self.folder = folder

    def save(self, ind: BeamNGIndividual, prefix: str = None):
        print(
            "BeamNGIndividualSetStore...................._BeamNGIndividualCompositeMembersStore................... save ...........................................")
        if not prefix:
            prefix = ind.name

        self.folder.mkdir(parents=True, exist_ok=True)
        ind_path = self.folder.joinpath(prefix + '.json')
        ind_path.write_text(json.dumps(ind.to_dict()))

        fig, (left, right) = plt.subplots(ncols=2)
        fig.set_size_inches(15, 10)
        ml, mr = ind.members_by_distance_to_boundary()

        def plot(member: BeamNGMember, ax):
            print(
                "BeamNGIndividualSetStore................._BeamNGIndividualCompositeMembersStore...................... plot ...........................................")
            ax.set_title(f'dist to bound ~ {np.round(member.distance_to_boundary, 2)}', fontsize=12)
            road_points = RoadPoints.from_nodes(member.sample_nodes)
            road_points.plot_on_ax(ax)

        plot(ml, left)
        plot(mr, right)
        fig.suptitle(f'members distance = {ind.members_distance} ; oob_ff = {ind.oob_ff}')
        fig.savefig(self.folder.joinpath(prefix + '_both_roads.svg'))
        plt.close(fig)

    def load(self, prefix: str) -> BeamNGIndividual:
        print(
            "BeamNGIndividualSetStore......................._BeamNGIndividualCompositeMembersStore................ load ...........................................")
        ind_path = self.folder.joinpath(prefix + '.json')
        ind = BeamNGIndividual.from_dict(json.loads(ind_path.read_text()))
        return ind


if __name__ == '__main__':
    store = _BeamNGIndividualCompositeMembersStore(folders.experiments.joinpath('exp1/gen0/population'))
    ind = store.load('ind1')
    store.save(ind, 'ind_xx')


class _BeamNGIndividualSimpleStore:
    def __init__(self, folder: Path):
        print(
            "BeamNGIndividualSetStore..............._BeamNGIndividualSimpleStore........................ initial ...........................................")
        self.folder = folder

    def save(self, ind: BeamNGIndividual, prefix=None):
        print(
            "BeamNGIndividualSetStore.................._BeamNGIndividualSimpleStore..................... save ...........................................")
        if not prefix:
            prefix = ind.name

        self.folder.mkdir(parents=True, exist_ok=True)

        def save_road_img(member: BeamNGMember, name):
            print(
                "BeamNGIndividualSetStore................._BeamNGIndividualSimpleStore...................... save_road_img ...........................................")
            filepath = self.folder.joinpath(name)
            # BeamNGRoadImagery.from_sample_nodes(member.sample_nodes).save(filepath.with_suffix('.jpg'))
            BeamNGRoadImagery.from_sample_nodes(member.sample_nodes).save(filepath.with_suffix('.svg'))

        ind_path = self.folder.joinpath(prefix + '.json')
        ind_path.write_text(json.dumps(ind.to_dict()))
        save_road_img(ind.m1, ind.name + '_m1_road')
        save_road_img(ind.m2, ind.name + '_m2_road')
