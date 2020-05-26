import itertools

import meridian
from meridian import Dataset, Record

from examples.data import states_data, power_plants_data


# Define our data model for the power plant dataset
class PowerPlant(Record):
    fid: int
    plant_code: int
    plant_name: str
    sector_name: str
    primsource: str
    install_mw: int
    total_mw: int
    period: int


# Note that the state geojson has more attributes than
# listed here; we will only load the attributes
# specified in the model's annotations.
class State(Record):
    statefp: str
    stusps: str
    name: str


def main():
    """
    This example shows how you'd perform a "spatial join", or find items from one dataset that fulfill
    a spatial predicate with another.
    """

    # SpatialData models include a method to create a Dataset of that type from a file.
    power_plants: Dataset[PowerPlant] = PowerPlant.load_from(path=power_plants_data)

    states: Dataset[State] = State.load_from(path=states_data)

    # Use the intersection function to get intersecting records between the two Datasets
    # for power_plant, state in meridian.intersection(power_plants, states):
    #     print("Power plant", power_plant.plant_name, "is in", state.name)

    # Because intersection returns an iterator of tuples, it's fully
    # interoperable with many standard library tools.
    joined = meridian.intersection(states, power_plants)
    for state, power_plants in itertools.groupby(joined, key=lambda result: result[0]):
        plants = list(power_plants)
        print(state.name, "contains", len(plants), "power plants")


if __name__ == "__main__":
    main()
