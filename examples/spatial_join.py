import csv

import fiona

from meridian import SpatialDataset

from examples.data import states_data, power_plants_data, data_path


def load(path):
    with fiona.open(path) as src:
        yield from src


def main():
    """
    This example shows how you'd perform a "spatial join", or apply attributes from one dataset to another based on
    spatial intersection.
    """
    power_plants = SpatialDataset(load(power_plants_data))
    states = SpatialDataset(load(states_data))

    for plant in power_plants:
        search = states.intersection(plant)
        if search:
            print("plant", plant.plant_name, "is in", search[0].name)


if __name__ == '__main__':
    main()
