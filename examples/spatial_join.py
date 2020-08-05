import itertools

import meridian

from examples.data import states_data, power_plants_data


# Define our data model for the power plant dataset
class PowerPlant(meridian.Record):
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
class State(meridian.Record):
    statefp: str
    stusps: str
    name: str


def main():
    """
    This example shows how you'd perform a "spatial join", or find items from one dataset that fulfill
    a spatial predicate with another.
    """

    # SpatialData models include a method to create a Dataset of that type from a file.
    power_plants: meridian.Dataset[PowerPlant] = PowerPlant.load_from(power_plants_data)
    states: meridian.Dataset[State] = State.load_from(states_data)

    # Use the intersection function to get intersecting records between the two Datasets
    for power_plant, state in meridian.intersection(power_plants, states):
        print("Power plant", power_plant.plant_name, "is in", state.name)
        print(power_plant)
        break

    # Because intersection returns an iterator of tuples, it's fully
    # interoperable with many standard library tools.
    joined = meridian.intersection(states, power_plants)
    for state, power_plants in itertools.groupby(joined, key=lambda result: result[0]):
        plants = list(power_plants)
        print(state.name, "contains", len(plants), "power plants")


if __name__ == "__main__":
    main()
