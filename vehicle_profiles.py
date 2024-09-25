from lempel_ziv78 import LempelZivTree


class VehicleProfiles:

    def __init__(self):
        self.profiles = {}

    def add_trip(self, vehicle_id: str, trip: str):
        vehicle_id = str(vehicle_id)
        if vehicle_id not in self.profiles:
            self.profiles[vehicle_id] = {"trip_string": "", "tree": LempelZivTree()}
        # Add the trip data to the profile
        self.profiles[vehicle_id]["trip_string"] += trip
        tree = self.profiles[vehicle_id]["tree"]
        tree.build_tree(self.profiles[vehicle_id]["trip_string"])
        tree.calculate_weights()  # Fix: Call the correct method

    def display_profile(self, vehicle_id: str):
        if vehicle_id in self.profiles:
            self.profiles[vehicle_id]["tree"].print_summary()
        else:
            print(f"No profile found for vehicle number: {vehicle_id}")

    def calculate_probability_for_vehicle(self, vehicle_id: str, string: str):
        if vehicle_id in self.profiles:
            return self.profiles[vehicle_id]["tree"].calculate_sequence_probability(string)
        else:
            print(f"No profile found for vehicle number: {vehicle_id}")
            return 0.0

    def get_sorted_trip_probabilities(self, vehicle_id, trips):
        trip_probabilities = []
        for trip_string, actual_vehicle_id in trips:
            probability = self.calculate_probability_for_vehicle(vehicle_id, trip_string)
            is_belongs = (vehicle_id == actual_vehicle_id)
            trip_probabilities.append((trip_string, probability, is_belongs))
        return sorted(trip_probabilities, key=lambda x: x[1], reverse=True)